"""
Chart Data Models and Extraction Schema.
Defines typed representations for calibrated axes, extracted data points,
p-value comparison brackets, and conversion to standard FastMCP TableRow formats.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import numpy as np


@dataclass
class AxisCalibration:
    label: str = ""
    min_val: float = 0.0
    max_val: float = 1.0
    scale_type: str = "LINEAR"  # "LINEAR" or "LOG"

    def pixel_to_val(self, pixel_y: float, pixel_origin_y: float, pixel_top_y: float) -> float:
        """
        Maps a screen Y pixel coordinate to numerical value along the calibrated axis.
        Note: Screen Y pixels increase downwards (origin at bottom has larger Y than top).
        """
        if abs(pixel_origin_y - pixel_top_y) < 1e-6:
            return self.min_val

        # Normalized ratio: 0.0 at origin, 1.0 at top
        ratio = (pixel_origin_y - pixel_y) / (pixel_origin_y - pixel_top_y)
        ratio = max(0.0, min(1.0, ratio))

        if self.scale_type.upper() == "LOG":
            log_min = np.log10(max(1e-6, self.min_val))
            log_max = np.log10(max(1e-6, self.max_val))
            return float(10 ** (log_min + ratio * (log_max - log_min)))
        else:
            return float(self.min_val + ratio * (self.max_val - self.min_val))


@dataclass
class ChartDataPoint:
    group_name: str
    mean: float
    dispersion_val: float = 0.0
    dispersion_type: str = "SD"  # "SD", "SEM", "CI95"
    n_sample: Optional[int] = None
    is_discrete: bool = False
    bbox: Optional[List[int]] = None  # [ymin, xmin, ymax, xmax]


@dataclass
class PValueBracket:
    group_a: str
    group_b: str
    claimed_text: str
    claimed_p_threshold: float
    bbox: Optional[List[int]] = None


@dataclass
class ExtractedChartData:
    figure_id: str
    chart_type: str
    y_axis: AxisCalibration
    series: List[ChartDataPoint] = field(default_factory=list)
    p_value_brackets: List[PValueBracket] = field(default_factory=list)
    raw_points: Optional[List[Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ExtractedChartData":
        y_axis = AxisCalibration(**d["y_axis"])
        series = [ChartDataPoint(**pt) for pt in d.get("series", [])]
        brackets = [PValueBracket(**b) for b in d.get("p_value_brackets", [])]
        return cls(
            figure_id=d.get("figure_id", ""),
            chart_type=d.get("chart_type", "BAR_WITH_ERROR_BARS"),
            y_axis=y_axis,
            series=series,
            p_value_brackets=brackets,
            raw_points=d.get("raw_points")
        )

    def to_table_rows(self) -> List[Dict[str, Any]]:
        """
        Converts extracted chart points into standardized TableRows
        compatible with the FastMCP mathematical consistency engine (GRIM, SPRITE, etc.).
        """
        rows = []
        for pt in self.series:
            sd_val = pt.dispersion_val
            # If dispersion is SEM, convert to SD = SEM * sqrt(N)
            if pt.dispersion_type.upper() == "SEM" and pt.n_sample and pt.n_sample > 1:
                sd_val = pt.dispersion_val * np.sqrt(pt.n_sample)

            row = {
                "variable_name": self.y_axis.label or "Chart Metric",
                "group_name": pt.group_name,
                "mean": pt.mean,
                "sd": round(float(sd_val), 4) if sd_val is not None else 0.0,
                "n_sample": pt.n_sample,
                "is_discrete": pt.is_discrete,
                "metric_type": "DISCRETE" if pt.is_discrete else "CONTINUOUS"
            }
            rows.append(row)
        return rows
