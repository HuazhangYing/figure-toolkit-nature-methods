# Nature Methods scientific figure standards

**Profile checked:** 17 November 2026\
**Scope:** statistical plots, single panels, and assembled multi-panel
figures made with Python, Matplotlib, Seaborn, and Scanpy/AnnData.

## 1. Official requirements used by this toolkit

The Nature Methods submission-formatting page states that figure panels
should be at least 300 dpi, no wider than 180 mm, and use 5--7 pt
sans-serif text. It also asks authors to use scale bars, keep labels and
scale/error bars editable, and define sample size, centre values, error
bars, statistical tests, and p-values in figure legends.

The Nature Research Figure Guide provides the broader production
specifications:

-   89 mm single-column and 183 mm double-column widths; maximum height
    170 mm.
-   Regular text 5--7 pt; multi-panel labels lowercase, bold, upright, 8
    pt.
-   Arial or Helvetica; embedded TrueType fonts; text must remain
    editable and must not be outlined.
-   PDF/EPS preferred for editable main figures; SVG is also accepted as
    an editable vector format.
-   RGB artwork; accessible colours; avoid red/green-only contrasts and
    rainbow scales.
-   Axis lines and tick marks should be present; axes should include
    units where applicable.
-   Main figures should be vector artwork. The guide lists PNG/JPEG/TIFF
    as unacceptable main-figure file formats; these are therefore
    preview/intermediate formats in this toolkit, not the default final
    main-figure submission.
-   Photographic images must be at least 300 dpi; the export section
    recommends 450 dpi or above for images. This toolkit targets 450 dpi
    for embedded raster panels when the original data support it, with
    300 dpi as the minimum.
-   Extended Data artwork has a separate specification: RGB, maximum 300
    dpi, and JPEG/TIFF/EPS formats.

**Nature Methods-specific width decision:** the journal's own formatting
page says maximum width 180 mm. Although the general Nature guide says
183 mm for double-column figures, this profile uses 180 mm as the
stricter journal-specific ceiling. Single-column width is 89 mm. Maximum
height is 170 mm.

Official references: 1. Nature Methods, AIP and formatting:
https://www.nature.com/nmeth/submission-guidelines/aip-and-formatting 2.
Nature Research Figure Guide, specifications:
https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/
3. Nature Research Figure Guide, building and exporting panels:
https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/
4. Springer Nature, AI use in manuscript preparation:
https://www.springernature.com/gp/policies/editorial-policies/ai-manuscript-preparation

Always re-check the live journal instructions at submission. Initial
submission and accepted-manuscript production can request different file
packaging.

## 2. Physical dimensions and typography

  Element                         Nature Methods toolkit default
  ----------------------------- --------------------------------
  Single-column width                                      89 mm
  Double-column width ceiling                             180 mm
  Maximum height                                          170 mm
  Axis label                                              6.5 pt
  Tick label                                              5.5 pt
  Legend                                                  5.5 pt
  Annotation                                              5.5 pt
  Panel label                     8 pt, bold, upright, lowercase
  Regular text range                                     5--7 pt
  Typical axis/data stroke                           0.6--0.9 pt
  Marker size                                            3--4 pt

These are practical defaults, not a claim that every element must have
exactly these values. Keep all regular text within 5--7 pt at final
size. Panel labels are the explicit 8 pt exception.

Set physical dimensions before plotting. Do not design a figure at
arbitrary screen size and shrink it during manuscript assembly. If a
figure is reduced, re-check all text and line weights at the final
placed size.

## 3. File formats and editability

### Main figures

-   Primary: PDF with editable vector text and paths.
-   Alternative: EPS.
-   Working/editing copy: SVG with text retained as text.
-   Preview only: PNG.
-   Do not use a PNG screenshot as the main figure.
-   Avoid TIFF/JPEG as the complete main figure unless the current
    Nature Methods submission system explicitly requests a raster file
    for a particular item.
-   Mixed figures may contain embedded raster photographs or microscopy
    panels, but axes, labels, arrows, scale bars, and annotations should
    remain vector/editable.

Matplotlib configuration: - `pdf.fonttype = 42` - `ps.fonttype = 42` -
`svg.fonttype = "none"`

Do not convert text to outlines. Check that fonts are actually installed
and embedded. A font-family declaration alone does not prove the output
uses Arial.

### Raster content

-   Minimum 300 dpi at the final placed size.
-   Target 450 dpi or higher when the original source resolution
    supports it.
-   Never upscale a low-resolution image and call it high-resolution.
-   Preserve original microscopy/photo files and metadata.
-   Keep scale bars and labels on separate editable layers; use scale
    bars rather than magnification factors.
-   Preserve the original image and record any permitted processing.

## 4. Colour and visual design

Use RGB. The default palette is the Okabe--Ito/Wong accessible palette:

-   Blue `#0072B2`
-   Orange `#E69F00`
-   Bluish green `#009E73`
-   Vermilion `#D55E00`
-   Sky blue `#56B4E9`
-   Reddish purple `#CC79A7`
-   Yellow `#F0E442`
-   Black `#000000`

Rules: - Avoid red/green as the only distinction. - Avoid rainbow colour
maps. - Use sequential maps for ordered quantities, diverging maps only
for meaningful signed deviations around a defined centre, and
qualitative palettes for categories. - Keep the same biological
condition mapped to the same colour throughout the manuscript. - Prefer
black/white text with sufficient contrast; avoid coloured text. - Keep
axis lines and tick marks visible. - Label axes with units in
parentheses when a unit exists. - Avoid unnecessary background
gridlines, shadows, patterns, gradients, decorative icons, and
overlapping labels.

## 5. Statistical display and reproducibility

Every plot must preserve the distinction between descriptive display and
inferential statistics.

Required decisions to record: - What is the experimental unit? - What
does `n` count (donors, animals, independent cultures, wells, cells,
fields, or technical replicates)? - Are observations paired, repeated,
nested, or independent? - What is the centre (mean, median, model
estimate)? - What do error bars represent (SD, SEM, confidence interval,
range)? - Which statistical test/model was used, with sidedness and
assumptions? - Was multiple-testing correction applied? Which method? -
Were any data excluded or transformed? Why and how?

Presentation guidance: - Show individual points when the sample size and
plot density permit. - For small samples (often n ≤ 10), show all
observations rather than only a summary bar. - Use
box/violin/raincloud/distribution displays only when their statistical
meaning is clear; do not hide sample size. - For paired data, show
pairing or use a paired summary. - Avoid bar charts for continuous data
when the underlying distribution can be shown. - Report exact p-values
where practical; do not write `p = 0` or imply that a threshold is an
effect size. - Include confidence intervals or effect sizes when
appropriate. - Do not choose a statistical test after inspecting which
one gives the smallest p-value. - Do not treat cells from the same donor
as independent biological replicates.

These are scientific-integrity requirements; the QC script cannot infer
whether the statistical design is correct.

## 6. Scanpy / AnnData-specific requirements

-   Record the AnnData file/version and the exact `obs`/`var` fields
    used.
-   Record the embedding basis (e.g. `X_umap`), colour variable,
    categorical order, and any filtering/subsetting.
-   State whether the plotted values are raw counts, normalized counts,
    log-transformed values, scaled values, or model outputs.
-   Do not overwrite the original AnnData object for figure-only
    operations.
-   Do not silently recompute neighbours, UMAP, clustering, or
    normalization during figure generation.
-   Preserve category order and colour mapping across panels.
-   If plotting cells from multiple donors or samples, make the
    biological sample structure visible or describe it in the legend.
-   For gene-expression panels, specify gene identifier/name and the
    layer or slot used.
-   Export through the shared style and inspect legends, overplotting,
    point size, and rasterization at final size.

## 7. Multi-panel assembly

-   Set the total canvas width and height in millimetres before creating
    panels.
-   Arrange panels in a clear reading order, normally alphabetical.
-   Align plot areas and axes where comparisons require it.
-   Use lowercase panel labels (`a`, `b`, `c`, ...), 8 pt bold upright.
-   Avoid a large global title inside the artwork.
-   Keep each panel independently editable where practical.
-   Avoid shrinking labels below 5 pt to make the layout fit; redesign
    the grid or split the figure.
-   Keep figure legends outside the figure artwork in the manuscript.

## 8. File naming and output bundle

Recommended structure:

``` text
figures/
  data/
  src/
    Fig1.py
  exports/
    Fig1.pdf
    Fig1.svg
    Fig1_preview.png
    Fig1.figure.json
    Fig1_data.csv
```

The sidecar JSON records software versions, dimensions, profile, data
references, and any statistical metadata supplied by the analyst. The
CSV is a snapshot of the exact plotted table when feasible. For large
AnnData objects, record the immutable `.h5ad` path/checksum and the
exact transformations instead of duplicating the entire object.

## 9. AI-assisted coding and visualisation

Springer Nature permits AI-assisted visual content derived from
verifiable data or source material when use is disclosed appropriately,
inputs and methods can be inspected, code/output are reviewed by humans,
and the result accurately represents the evidence. AI-generated visuals
without verifiable source material are not permitted under the current
policy. The authors remain responsible.

For this workflow: - Codex may write/refactor plotting code and help
generate figures from supplied data. - Authors must inspect and validate
the code, statistical methods, data transformations, and final
artwork. - Never ask an image-generation model to invent empirical data,
microscopy, gels, blots, or statistical plots. - Keep the model/tool
name, purpose, and contribution available for any required
declaration. - Follow the journal's live AI disclosure instructions at
submission.
