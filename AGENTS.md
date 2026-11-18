# Codex instructions: publication-quality scientific figures

These instructions apply to every task that creates, edits, analyzes, or
exports scientific figures in this repository.

## 1. Target journal and source of truth

-   Default target journal: **Nature Methods**.
-   Before final submission, re-check the current Nature Methods author
    instructions and the Nature Research Figure Guide. Journal
    requirements can change.
-   The checked baseline is recorded in `journal_profiles.json`; do not
    silently replace journal-specific values with generic Nature
    Portfolio values.
-   Nature Methods' own formatting page specifies a maximum figure width
    of 180 mm, minimum 300 dpi for figure panels, and 5--7 pt sans-serif
    labels. The Nature Research Figure Guide specifies 89 mm
    single-column width, 183 mm double-column width, maximum 170 mm
    height, editable vector artwork, and 5--7 pt regular text. This
    toolkit uses 89 mm single-column and the stricter 180 mm
    double-column maximum for Nature Methods.

## 2. Required workflow

For each figure task:

1.  Inspect the input data, schema, units, missingness, grouping
    variables, and replicate structure before plotting.
2.  Identify the scientific question and the correct statistical unit.
    Distinguish biological replicates from technical replicates and
    cells from independent biological samples.
3.  Decide whether the requested display is appropriate for the data.
    Prefer showing individual observations and distributions when
    informative; avoid defaulting to bar charts for continuous
    distributions.
4.  Use the shared style from `publication_style.py`. Do not create a
    separate ad hoc style unless the user explicitly requests it.
5.  Save analysis and plotting code under `figures/src/`, data snapshots
    or provenance under `figures/data/`, and exports under
    `figures/exports/` unless the repository already has an established
    structure.
6.  Export the editable PDF as the primary main-figure deliverable. Also
    export SVG for editing and PNG only as a preview. Do not present PNG
    as the preferred final Nature Methods main-figure file.
7.  Save a provenance sidecar (`*.figure.json`) and the exact plotted
    data or a clear reference to the immutable source data.
8.  For multi-panel figures, build panels as separate axes/functions,
    add lowercase panel labels (`a`, `b`, `c`, ...), and assemble them
    at final physical dimensions. Keep all labels, arrows, scale bars,
    and annotations editable.
9.  Run `figure_qc.py` on the exported files. Fix all errors and review
    warnings.
10. Render or open the final PDF/PNG and visually inspect clipping,
    overlaps, legibility at final size, and consistency across panels.

## 3. Scientific integrity rules

-   Never invent, interpolate, smooth, normalize, filter, impute, or
    remove observations merely to improve appearance.
-   Never fabricate sample sizes, p-values, confidence intervals, error
    bars, labels, or statistical significance.
-   Do not infer an experimental replicate from a cell, image field,
    technical well, or repeated measurement.
-   State what `n` represents. Use the biological replicate as the
    inferential unit when appropriate.
-   Define error bars exactly (SD, SEM, confidence interval, range, or
    another quantity).
-   Use statistical tests that match the design, distributional
    assumptions, pairing, repeated measures, and experimental unit.
-   Apply and report multiple-testing correction when relevant.
-   Report exact p-values where practical; use thresholds only when
    journal or field convention requires them.
-   Preserve all observations. Any exclusion or outlier rule must be
    scientifically justified, documented, and applied consistently.
-   Do not truncate axes in a way that exaggerates differences. If a
    non-zero baseline or transformed scale is scientifically necessary,
    label it clearly.
-   Do not imply causality from a descriptive association.
-   Do not alter primary microscopy, gel, blot, or other experimental
    images to create a desired result. Preserve raw files and document
    all permitted processing.

## 4. Nature Methods visual baseline

Use `publication_style.py` and `journal_profiles.json`:

-   Font: Arial or Helvetica; report if the requested font is
    unavailable. Do not silently claim Arial when a fallback was used.
-   Regular figure text: 5--7 pt at final physical size.
-   Panel labels: lowercase, bold, upright, 8 pt.
-   Main figure widths: 89 mm single column; 180 mm double-column
    ceiling for this Nature Methods profile.
-   Maximum figure height: 170 mm.
-   Main-figure output: editable PDF preferred; EPS is an alternative.
    SVG is an editable working/accepted vector format. PNG is
    preview-only.
-   Use RGB.
-   Embed raster photographs/microscopy at no less than 300 dpi at final
    size; target 450 dpi where source resolution permits. Never upscale
    a low-resolution source to claim higher resolution.
-   Keep text, axes, markers, arrows, scale bars, and panel labels as
    editable vector objects.
-   Use an accessible palette; avoid red/green-only distinctions and
    rainbow maps.
-   Include visible axes and tick marks. Label axes with units in
    parentheses where applicable.
-   Avoid unnecessary gridlines, shadows, decorative icons, coloured
    text, and overlapping labels.

## 5. Matplotlib / Seaborn / Scanpy implementation

-   Import and call `apply_style()` from `publication_style.py` before
    plotting.
-   If using `seaborn.set_theme`, call `apply_style()` after the Seaborn
    theme to restore publication settings.
-   For Scanpy, use `show=False`; obtain the figure object and export it
    through `save_figure()`. Keep the AnnData object and preprocessing
    provenance unchanged.
-   Set `pdf.fonttype = 42`, `ps.fonttype = 42`, and
    `svg.fonttype = 'none'`.
-   Do not use `bbox_inches='tight'` for final exports unless the final
    page dimensions are checked afterwards. Tight bounding boxes can
    silently change physical dimensions.
-   Do not rasterize axes, labels, text, or simple vector marks.
    Rasterize only dense point clouds when necessary and only after
    checking the result.
-   Avoid embedding external linked files in final artwork; embed
    required image assets.

## 6. Multi-panel figures

-   Plan the final page size before positioning panels.
-   Use a consistent panel grid, aligned axes, consistent typography,
    and a deliberate reading order.
-   Use lowercase panel labels (`a`, `b`, `c`, ...), 8 pt bold and
    upright.
-   Do not add an overall title inside the figure unless scientifically
    necessary.
-   Do not squeeze text below 5 pt to fit. Re-layout or split the figure
    instead.
-   Keep legends concise and avoid duplicating information already
    encoded by axes or labels.
-   Figure legends belong in the manuscript, not as large blocks of text
    inside the figure.

## 7. Required deliverables

For each figure, provide:

-   `FigX.pdf`: editable vector main-figure file.
-   `FigX.svg`: editable vector working file.
-   `FigX_preview.png`: visual preview, not the preferred final
    main-figure upload.
-   `FigX.py` or equivalent source code.
-   `FigX.figure.json`: provenance, dimensions, software versions, data
    references, and supplied statistical metadata.
-   A data snapshot (CSV/TSV) when feasible, or a precise reference to
    the source dataset and the transformations used.

For figures with raster panels, retain the original image files and
document their processing. The final composite should keep annotations
and labels editable.

## 8. Quality control and reporting

Run:

``` bash
python figure_qc.py figures/exports --strict
```

The QC script checks file presence/readability, PDF page dimensions,
embedded-font information when Poppler is available, SVG text
editability, PNG metadata, and file size. These checks do **not**
validate the scientific correctness of the analysis. Manually verify
statistics, sample size, units, panel identity, image integrity, and
final-size legibility.

When reporting completion, state: - which files were generated; - the
target profile and physical dimensions; - any font fallback or QC
warning; - the data source and statistical test metadata used; - what
still requires human scientific review.

## 9. AI-assisted figure creation

Codex may help write or review code that visualizes verifiable source
data. All generated code and outputs must be reviewed by the authors.
Never use text-to-image generation to fabricate empirical data,
microscopy, gels, blots, plots, or quantitative results. Follow Springer
Nature's current AI policy and disclose AI assistance when required by
the journal, including the system, purpose, and contribution. Authors
remain responsible for the accuracy and integrity of every figure.
