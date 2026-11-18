"""Nature Methods-oriented plotting style and reproducible export helpers.

This module styles Matplotlib figures; it does not perform statistical analysis.
All dimensions are physical dimensions in millimetres at final figure size.
"""
from __future__ import annotations

import json
import platform
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from cycler import cycler

MM_PER_INCH = 25.4

PALETTE = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky_blue": "#56B4E9",
    "bluish_green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "reddish_purple": "#CC79A7",
    "grey": "#666666",
    "light_grey": "#BDBDBD",
}
PALETTE_ORDER = [
    PALETTE["blue"], PALETTE["orange"], PALETTE["bluish_green"],
    PALETTE["vermillion"], PALETTE["sky_blue"],
    PALETTE["reddish_purple"], PALETTE["yellow"], PALETTE["black"],
]

_DEFAULT_PROFILE = {
    "name": "Nature Methods",
    "single_column_width_mm": 89.0,
    "double_column_width_mm": 180.0,
    "max_width_mm": 180.0,
    "max_height_mm": 170.0,
    "font_candidates": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
    "font_sizes_pt": {
        "axis_label": 6.5, "tick_label": 5.5, "legend": 5.5,
        "annotation": 5.5, "panel_label": 8.0,
    },
    "regular_text_min_pt": 5.0,
    "regular_text_max_pt": 7.0,
    "min_raster_dpi": 300,
    "recommended_raster_dpi": 450,
    "preferred_main_formats": ["pdf", "eps"],
    "editable_working_format": "svg",
    "preview_format": "png",
}

def _load_profile(profile: str | Mapping[str, Any] = "nature_methods",
                  config_path: Optional[str | Path] = None) -> dict[str, Any]:
    if isinstance(profile, Mapping):
        cfg = dict(profile)
    elif config_path:
        raw = json.loads(Path(config_path).read_text(encoding="utf-8"))
        cfg = dict(raw[profile])
    elif profile in ("nature_methods", "Nature Methods", "nature-methods"):
        cfg = dict(_DEFAULT_PROFILE)
    else:
        raise ValueError(f"Unknown profile {profile!r}. Provide a profile mapping or config_path.")
    # Nested defaults are copied so callers cannot mutate module-level settings.
    merged = dict(_DEFAULT_PROFILE)
    merged.update(cfg)
    merged["font_sizes_pt"] = {
        **_DEFAULT_PROFILE["font_sizes_pt"],
        **dict(cfg.get("font_sizes_pt", {})),
    }
    return merged

def _resolve_font(candidates: Sequence[str], strict: bool = False) -> str:
    available = {f.name for f in font_manager.fontManager.ttflist}
    preferred = [name for name in candidates if name in ("Arial", "Helvetica")]
    for candidate in preferred:
        if candidate in available:
            return candidate
    fallbacks = [name for name in candidates if name not in ("Arial", "Helvetica")]
    selected = next((name for name in fallbacks if name in available), "DejaVu Sans")
    message = (
        "Neither Arial nor Helvetica is installed. Matplotlib is using "
        f"'{selected}' as a fallback. Install Arial or Helvetica for production artwork "
        "and inspect the embedded fonts in the exported PDF."
    )
    if strict:
        raise RuntimeError(message)
    warnings.warn(message, RuntimeWarning, stacklevel=2)
    return selected

def apply_style(
    profile: str | Mapping[str, Any] = "nature_methods",
    *,
    config_path: Optional[str | Path] = None,
    strict_fonts: bool = False,
    overrides: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Apply the selected journal profile to Matplotlib and return its settings."""
    cfg = _load_profile(profile, config_path)
    if overrides:
        cfg.update(dict(overrides))
    selected_font = _resolve_font(cfg["font_candidates"], strict=strict_fonts)
    sizes = cfg["font_sizes_pt"]

    mpl.rcParams.update({
        "font.family": selected_font,
        "font.size": sizes["tick_label"],
        "axes.labelsize": sizes["axis_label"],
        "axes.titlesize": sizes["axis_label"],
        "xtick.labelsize": sizes["tick_label"],
        "ytick.labelsize": sizes["tick_label"],
        "legend.fontsize": sizes["legend"],
        "axes.linewidth": 0.65,
        "lines.linewidth": 0.85,
        "lines.markersize": 3.5,
        "xtick.major.width": 0.65,
        "ytick.major.width": 0.65,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "xtick.minor.width": 0.5,
        "ytick.minor.width": 0.5,
        "xtick.minor.size": 1.5,
        "ytick.minor.size": 1.5,
        "axes.labelcolor": "black",
        "axes.edgecolor": "black",
        "xtick.color": "black",
        "ytick.color": "black",
        "text.color": "black",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.edgecolor": "white",
        "savefig.transparent": False,
        "savefig.bbox": None,
        "legend.frameon": False,
        "axes.grid": False,
        "axes.prop_cycle": cycler(color=PALETTE_ORDER),
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "mathtext.fontset": "stixsans",
    })
    cfg["resolved_font"] = selected_font
    return cfg

def figure_size(
    width: str = "double",
    height_mm: float = 65.0,
    *,
    width_mm: Optional[float] = None,
    profile: str | Mapping[str, Any] = "nature_methods",
    config_path: Optional[str | Path] = None,
) -> tuple[float, float]:
    """Return (width_inches, height_inches), enforcing profile dimensions."""
    cfg = _load_profile(profile, config_path)
    if width_mm is None:
        if width == "single":
            width_mm = float(cfg["single_column_width_mm"])
        elif width == "double":
            width_mm = float(cfg["double_column_width_mm"])
        else:
            raise ValueError("width must be 'single' or 'double', or provide width_mm.")
    if width_mm <= 0 or height_mm <= 0:
        raise ValueError("Figure dimensions must be positive.")
    if width_mm > float(cfg["max_width_mm"]):
        raise ValueError(f"width_mm={width_mm} exceeds {cfg['max_width_mm']} mm.")
    if height_mm > float(cfg["max_height_mm"]):
        raise ValueError(f"height_mm={height_mm} exceeds {cfg['max_height_mm']} mm.")
    return width_mm / MM_PER_INCH, height_mm / MM_PER_INCH

def create_figure(
    *,
    width: str = "double",
    height_mm: float = 65.0,
    width_mm: Optional[float] = None,
    nrows: int = 1,
    ncols: int = 1,
    squeeze: bool = True,
    gridspec_kw: Optional[dict[str, Any]] = None,
    profile: str | Mapping[str, Any] = "nature_methods",
    config_path: Optional[str | Path] = None,
):
    """Create a Matplotlib figure at its final physical dimensions."""
    figsize = figure_size(
        width, height_mm, width_mm=width_mm, profile=profile, config_path=config_path
    )
    return plt.subplots(
        nrows=nrows, ncols=ncols, figsize=figsize, squeeze=squeeze,
        gridspec_kw=gridspec_kw,
    )

def add_panel_label(
    ax: Axes,
    label: str,
    *,
    x: float = -0.12,
    y: float = 1.06,
    fontsize: float = 8.0,
) -> Any:
    """Add a Nature-style lowercase, bold, upright panel label in axes coordinates."""
    return ax.text(
        x, y, label.lower(), transform=ax.transAxes,
        ha="left", va="bottom", fontsize=fontsize, fontweight="bold",
        fontstyle="normal", color="black", clip_on=False,
    )

def style_axis(ax: Axes, *, hide_top: bool = True, hide_right: bool = True) -> Axes:
    """Apply restrained axis styling while retaining visible left/bottom axes and ticks."""
    if hide_top:
        ax.spines["top"].set_visible(False)
    if hide_right:
        ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.65)
    ax.spines["bottom"].set_linewidth(0.65)
    ax.tick_params(direction="out", width=0.65, length=2.5, colors="black")
    ax.grid(False)
    return ax

def save_plot_data(dataframe, out_stem: str | Path, *, index: bool = False) -> Path:
    """Save the exact plotted table as CSV and return its path."""
    out = Path(out_stem)
    out.parent.mkdir(parents=True, exist_ok=True)
    path = out.with_name(out.name + "_data.csv")
    dataframe.to_csv(path, index=index)
    return path

def save_figure(
    fig: Figure,
    out_stem: str | Path,
    *,
    profile: str | Mapping[str, Any] = "nature_methods",
    formats: Sequence[str] = ("pdf", "svg", "png"),
    preview_dpi: int = 300,
    data_files: Optional[Iterable[str | Path]] = None,
    stats: Optional[Mapping[str, Any]] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    close: bool = False,
) -> list[Path]:
    """Export PDF/SVG/PNG and write a JSON provenance sidecar.

    PDF is the preferred main-figure output. SVG is an editable working copy.
    PNG is a preview only. No data or statistics are created by this function.
    """
    cfg = _load_profile(profile)
    out = Path(out_stem)
    out.parent.mkdir(parents=True, exist_ok=True)
    width_in, height_in = fig.get_size_inches()
    width_mm, height_mm = width_in * MM_PER_INCH, height_in * MM_PER_INCH

    if width_mm > float(cfg["max_width_mm"]) + 0.05:
        raise ValueError(f"Figure width {width_mm:.2f} mm exceeds profile maximum.")
    if height_mm > float(cfg["max_height_mm"]) + 0.05:
        raise ValueError(f"Figure height {height_mm:.2f} mm exceeds profile maximum.")

    allowed = {"pdf", "eps", "svg", "png"}
    unknown = set(formats) - allowed
    if unknown:
        raise ValueError(f"Unsupported format(s): {sorted(unknown)}")

    outputs: list[Path] = []
    for fmt in formats:
        path = (out.with_name(out.name + "_preview.png") if fmt == "png"
                else out.with_suffix("." + fmt))
        kwargs = {
            "format": fmt,
            "facecolor": "white",
            "transparent": False,
            "bbox_inches": None,  # Preserve the declared physical page size.
            "pad_inches": 0,
        }
        if fmt in ("png", "eps"):
            kwargs["dpi"] = preview_dpi if fmt == "png" else 450
        fig.savefig(path, **kwargs)
        outputs.append(path)

    try:
        import matplotlib
        mpl_version = matplotlib.__version__
    except Exception:
        mpl_version = "unknown"

    sidecar = {
        "profile": cfg.get("name", "Nature Methods"),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "figure_size_mm": {"width": round(width_mm, 3), "height": round(height_mm, 3)},
        "resolved_font": cfg.get("resolved_font", mpl.rcParams.get("font.family")),
        "outputs": [str(p) for p in outputs],
        "data_files": [str(Path(p)) for p in (data_files or [])],
        "statistics": dict(stats or {}),
        "metadata": dict(metadata or {}),
        "software": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "matplotlib": mpl_version,
        },
        "notes": [
            "PDF is the preferred editable main-figure output.",
            "SVG is an editable working copy; PNG is a preview only.",
            "Statistical metadata are supplied by the analyst and are not independently validated.",
        ],
    }
    sidecar_path = out.with_name(out.name + ".figure.json")
    sidecar_path.write_text(json.dumps(sidecar, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    outputs.append(sidecar_path)

    if close:
        plt.close(fig)
    return outputs

__all__ = [
    "PALETTE", "PALETTE_ORDER", "apply_style", "figure_size", "create_figure",
    "add_panel_label", "style_axis", "save_plot_data", "save_figure",
]
