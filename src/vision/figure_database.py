"""
Figure Database Module: In-Process DuckDB Fingerprint Store & Incremental Indexer.

Implements an append-only, idempotent index of retracted and control scientific figures
using 64-bit perceptual hashes (pHash/dHash) and 256-dimensional dense embeddings.
Designed for continuous future expansion (5,000 -> 10,000 -> 50,000+ studies).
"""

from typing import Union, List, Dict, Any, Optional
import os
import json
import duckdb
import numpy as np
import cv2

from src.vision.figure_fingerprint import (
    compute_phash,
    compute_dhash,
    compute_figure_embedding,
    hamming_distance
)
from src.vision.panel_splitter import split_figure_panels, classify_figure_type


class FigureDatabase:
    """
    DuckDB-backed persistent vector and perceptual hash index for scientific figures.
    """

    def __init__(self, db_path: str = "data/retracted_figures.duckdb"):
        self.db_path = db_path
        if db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

        self.con = duckdb.connect(db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        """Initializes database schema with vector and unsigned 64-bit int support."""
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS retracted_figure_index (
                figure_id VARCHAR PRIMARY KEY,
                pmcid VARCHAR,
                doi VARCHAR,
                panel_id VARCHAR,
                is_retracted BOOLEAN,
                retraction_reasons VARCHAR,
                phash VARCHAR,
                phash_int UBIGINT,
                dhash VARCHAR,
                dhash_int UBIGINT,
                embedding FLOAT[256],
                figure_path VARCHAR,
                metadata_json VARCHAR,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

    def close(self) -> None:
        """Closes the DuckDB connection."""
        if self.con:
            self.con.close()
            self.con = None

    def get_stats(self) -> Dict[str, Any]:
        """Returns corpus summary statistics."""
        row = self.con.execute("""
            SELECT
                COUNT(*) AS total_figures,
                COUNT(DISTINCT pmcid) AS total_studies,
                COUNT(*) FILTER (WHERE is_retracted = TRUE) AS total_retracted_figures,
                COUNT(DISTINCT pmcid) FILTER (WHERE is_retracted = TRUE) AS total_retracted_studies
            FROM retracted_figure_index
        """).fetchone()

        return {
            "total_figures": row[0] or 0,
            "total_studies": row[1] or 0,
            "total_retracted_figures": row[2] or 0,
            "total_retracted_studies": row[3] or 0,
            "db_path": self.db_path
        }

    def index_figure(
        self,
        figure_id: str,
        pmcid: str,
        doi: str,
        panel_id: str,
        is_retracted: bool,
        retraction_reasons: str,
        img_input: Union[str, np.ndarray],
        figure_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Idempotently inserts or updates a single figure/panel into the DuckDB index.
        """
        phash_str = compute_phash(img_input)
        dhash_str = compute_dhash(img_input)
        emb = compute_figure_embedding(img_input, embed_dim=256)

        phash_val = int(phash_str, 16)
        dhash_val = int(dhash_str, 16)
        meta_str = json.dumps(metadata) if metadata else "{}"
        actual_path = figure_path if figure_path else (img_input if isinstance(img_input, str) else "")

        query = """
            INSERT OR REPLACE INTO retracted_figure_index (
                figure_id, pmcid, doi, panel_id, is_retracted,
                retraction_reasons, phash, phash_int, dhash, dhash_int,
                embedding, figure_path, metadata_json, indexed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
        """
        self.con.execute(query, [
            figure_id, pmcid, doi, panel_id, is_retracted,
            retraction_reasons, phash_str, phash_val, dhash_str, dhash_val,
            emb, actual_path, meta_str
        ])

    def index_study_figures(
        self,
        pmcid: str,
        doi: str,
        figure_paths: List[str],
        is_retracted: bool = True,
        retraction_reasons: str = "Figure reuse and data fabrication",
        split_panels: bool = True
    ) -> int:
        """
        Indexes all figures from a study, optionally splitting multi-panel figures.
        Returns total count of indexed figure panels.
        """
        indexed_count = 0
        for fig_idx, fig_path in enumerate(figure_paths):
            if not os.path.exists(fig_path):
                continue
            fig_name = os.path.splitext(os.path.basename(fig_path))[0]
            full_fig_id = f"{pmcid}_{fig_name}_FULL"

            # 1. Index full figure
            self.index_figure(
                figure_id=full_fig_id,
                pmcid=pmcid,
                doi=doi,
                panel_id="FULL",
                is_retracted=is_retracted,
                retraction_reasons=retraction_reasons,
                img_input=fig_path,
                figure_path=fig_path
            )
            indexed_count += 1

            # 2. Optionally split into constituent sub-panels
            if split_panels:
                try:
                    panels = split_figure_panels(fig_path)
                    for panel in panels:
                        panel_id = panel.get("panel_id", "SUB")
                        sub_fig_id = f"{pmcid}_{fig_name}_{panel_id}"
                        self.index_figure(
                            figure_id=sub_fig_id,
                            pmcid=pmcid,
                            doi=doi,
                            panel_id=panel_id,
                            is_retracted=is_retracted,
                            retraction_reasons=retraction_reasons,
                            img_input=panel["image"],
                            figure_path=fig_path,
                            metadata={"bbox": panel.get("bbox"), "figure_type": panel.get("figure_type")}
                        )
                        indexed_count += 1
                except Exception:
                    pass

        return indexed_count

    def query_candidates(
        self,
        img_input: Union[str, np.ndarray],
        top_k: int = 20,
        max_hamming: int = 16,
        min_cosine: float = 0.65
    ) -> List[Dict[str, Any]]:
        """
        Queries the DuckDB index using 64-bit Hamming filter and dense vector cosine ranking.
        """
        phash_str = compute_phash(img_input)
        dhash_str = compute_dhash(img_input)
        emb = compute_figure_embedding(img_input, embed_dim=256)

        phash_val = int(phash_str, 16)
        dhash_val = int(dhash_str, 16)

        # Stage 1 & 2 Combined Query in DuckDB SIMD Engine
        sql = """
            SELECT
                figure_id, pmcid, doi, panel_id, is_retracted, retraction_reasons,
                figure_path, phash, dhash, metadata_json,
                bit_count(xor(phash_int, ?::UBIGINT)) AS hamming_phash,
                bit_count(xor(dhash_int, ?::UBIGINT)) AS hamming_dhash,
                list_cosine_similarity(embedding, ?::FLOAT[256]) AS cosine_similarity
            FROM retracted_figure_index
            WHERE bit_count(xor(phash_int, ?::UBIGINT)) <= ?
               OR bit_count(xor(dhash_int, ?::UBIGINT)) <= ?
               OR list_cosine_similarity(embedding, ?::FLOAT[256]) >= ?
            ORDER BY cosine_similarity DESC, hamming_phash ASC
            LIMIT ?;
        """

        rows = self.con.execute(sql, [
            phash_val, dhash_val, emb,
            phash_val, max_hamming,
            dhash_val, max_hamming,
            emb, min_cosine,
            top_k
        ]).fetchall()

        # If no candidates match filter thresholds, fall back to best global cosine matches
        if not rows:
            fallback_sql = """
                SELECT
                    figure_id, pmcid, doi, panel_id, is_retracted, retraction_reasons,
                    figure_path, phash, dhash, metadata_json,
                    bit_count(xor(phash_int, ?::UBIGINT)) AS hamming_phash,
                    bit_count(xor(dhash_int, ?::UBIGINT)) AS hamming_dhash,
                    list_cosine_similarity(embedding, ?::FLOAT[256]) AS cosine_similarity
                FROM retracted_figure_index
                ORDER BY cosine_similarity DESC
                LIMIT ?;
            """
            rows = self.con.execute(fallback_sql, [phash_val, dhash_val, emb, top_k]).fetchall()

        results = []
        for r in rows:
            results.append({
                "figure_id": r[0],
                "pmcid": r[1],
                "doi": r[2],
                "panel_id": r[3],
                "is_retracted": bool(r[4]),
                "retraction_reasons": r[5],
                "figure_path": r[6],
                "phash": r[7],
                "dhash": r[8],
                "metadata": json.loads(r[9]) if r[9] else {},
                "hamming_phash": int(r[10]),
                "hamming_dhash": int(r[11]),
                "cosine_similarity": float(r[12])
            })

        return results

    def bulk_index_from_manifest(self, manifest_path: str, is_retracted: bool = True) -> int:
        """
        Loads and indexes figures from a JSON or JSONL manifest for batch scaling.
        Manifest format: list of dicts with keys: pmcid, doi, figure_paths, retraction_reasons.
        """
        indexed_total = 0
        if manifest_path.endswith(".jsonl"):
            with open(manifest_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    item = json.loads(line)
                    count = self.index_study_figures(
                        pmcid=item.get("pmcid", "UNKNOWN"),
                        doi=item.get("doi", ""),
                        figure_paths=item.get("figure_paths", []),
                        is_retracted=item.get("is_retracted", is_retracted),
                        retraction_reasons=item.get("retraction_reasons", "Literature integrity audit")
                    )
                    indexed_total += count
        else:
            with open(manifest_path, "r", encoding="utf-8") as f:
                items = json.load(f)
                for item in items:
                    count = self.index_study_figures(
                        pmcid=item.get("pmcid", "UNKNOWN"),
                        doi=item.get("doi", ""),
                        figure_paths=item.get("figure_paths", []),
                        is_retracted=item.get("is_retracted", is_retracted),
                        retraction_reasons=item.get("retraction_reasons", "Literature integrity audit")
                    )
                    indexed_total += count
        return indexed_total
