# Pakistan Workers' Remittances Dashboard: Design and Build Guide

**Version:** 1.0 (design specification, for review before any code is written)
**Date:** 29 October 2026
**Audience of the dashboard:** Client and management presentation (non-technical viewers)
**Source file:** `Homeremit_Arch.xlsx` (State Bank of Pakistan, Country-wise Workers' Remittances, US$ million)
**Stack:** Python, Streamlit, Plotly (multi-page app)
**Visual identity:** Teal, Copper and White

---

## 1. Purpose and success criteria

### 1.1 What this dashboard is for
To let a manager or client understand, within about five minutes and without any technical background, how much money overseas Pakistanis send home, where it comes from, how that has changed, and when it arrives.

### 1.2 Success criteria
| # | Criterion | How we will check it |
|---|---|---|
| 1 | A non-technical viewer can state the main message of each page after looking at it for 30 seconds | Review session with a non-technical person |
| 2 | Every number on screen ties back to the source workbook | Automated reconciliation report (Section 4.5) |
| 3 | No source value is altered, estimated, filled or smoothed | Raw-vs-loaded comparison test |
| 4 | The look matches the Teal, Copper and White identity on every page, including the top bar and sidebar | Visual review against Section 6 |
| 5 | Pages load in under 3 seconds after first load | Timing check with caching enabled |
| 6 | Readable on a 1920 x 1080 projector and on a laptop | Screen checks at both sizes |

### 1.3 Out of scope (for version 1)
- Live connection to SBP EasyData (the source says updates now live there; version 1 uses this file only).
- Forecasting (can be added later as a clearly labeled optional page).
- Rupee conversion (the file is in US dollars only).

---

## 2. What the source file contains (verified facts)

### 2.1 Structure
The workbook has three sheets covering **July 1972 to September 2026** (651 monthly values per series), in **US$ million**.

| Sheet | Period | Monthly columns | Fiscal-year columns | Rows |
|---|---|---|---|---|
| `Jul 72 to  Jun 10` | Jul 1972 to Jun 2010 (FY73 to FY10) | 456 | 38 | 12 country groups + total |
| `July 2010- Jun 2018` | Jul 2010 to Jun 2018 (FY11 to FY18) | 96 | 8 | Same as above |
| `July 2018 onwards ` | Jul 2018 to Sep 2026 (FY19 to FY26, plus FY27 year to date) | 96 valid + 3 current-year months + 2 invalid | 8 | 15 country groups + total |

Pakistan's fiscal year (FY) runs July to June. FY26 means July 2025 to June 2026. The fiscal-year total columns sit between the monthly columns, so they must be separated from months during loading.

### 2.2 Hierarchy inside the rows
Some rows are **parents** that already include their **children**. Adding both double-counts.

```
Total (Cash flow)
├── USA
├── U.K.
├── Saudi Arabia
├── U.A.E.                        (parent)
│     ├── Dubai
│     ├── Abu Dhabi
│     ├── Sharjah
│     └── Others (UAE)
├── Other GCC Countries           (parent)
│     ├── Bahrain
│     ├── Kuwait
│     ├── Qatar
│     └── Oman
├── EU Countries                  (parent)
│     ├── Germany  France  Netherland  Spain  Italy
│     └── Greece  Sweden  Denmark  Ireland  Belgium
├── Malaysia*                     (separate from Jul 2018 only)
├── Norway
├── Switzerland
├── Australia
├── Canada
├── Japan
├── South Africa*                 (separate from Jul 2018 only)
├── South Korea*                  (separate from Jul 2018 only)
└── Other Countries
```
Before July 2018, Malaysia, South Africa and South Korea were recorded inside "Other Countries". The first two sheets also carry a negligible FEBC/FCBC encashment row (a separate line, near zero).

### 2.3 Integrity checks already run on the workbook
These were run directly on the file during analysis.

| Check | Result |
|---|---|
| Sum of 12 months equals the printed fiscal-year total (54 fiscal years across 3 sheets) | **0 mismatches** |
| Total of the top-level rows equals the Cash row, every month | **0 mismatches** |
| UAE equals the sum of its four sub-rows, every month | **0 mismatches** |
| Other GCC equals the sum of its four members, every month | **0 mismatches** |
| EU equals the sum of its ten members, every month | **0 mismatches** |
| Total equals Cash plus FEBC/FCBC | **0 mismatches** except two invalid columns (below) |

### 2.4 Known data issues (and what we do about each)

| # | Issue | Handling (no values changed) |
|---|---|---|
| 1 | Columns labelled `Aug-27` and `Aug-28` on the latest sheet hold a Cash of 0 and a Total that duplicates other months (3,587.8 and 3,656.8). They are not real months | **Excluded and logged** in the load report. They are never charted or summed |
| 2 | The latest valid month is **Sep-26**. `Aug-26R` and `June-26R` carry an "R" (Revised) | Kept exactly as given. An `is_revised` flag is stored and a footnote appears on screen |
| 3 | **Methodology break in July 2019.** From July 2019 the SBP records the *original country of the remitter* (sheet note 3). For example the USA falls from 3,309 (FY19) to 1,743 (FY20) while Germany and the EU rise sharply | **Not corrected.** Stored as-is with a `basis` flag (`"pre_2019"` or `"post_2019"`). Handled differently by chart type: (a) **Full-history / trend charts** use a **split-series** approach — the line is drawn in two disconnected segments with a shaded gap region labelled *"Reporting basis changed — series not comparable across this point"*; (b) **Country-breakdown charts** default to **post-2019 data only** and show a toggle *"Show pre-2019 data (different methodology)"* that the user must click deliberately to see the earlier series. This prevents the discontinuity from looking like an error to non-technical viewers. |
| 4 | Roshan Digital Account conversions are included from September 2020 (sheet note 2) | Marked with an event annotation, not adjusted |
| 5 | Malaysia, South Africa and South Korea appear only from July 2018 | Before that they stay inside "Other Countries". Their lines start in July 2018 |
| 6 | Many pre-2000s country rows are all zeros (e.g., UAE emirates before FY75, EU members such as France and Spain in the 1970s) meaning **not separately reported**, not "zero remittances" | Raw zeros are kept in the data. For display, lines start at the first non-zero period and the tooltip says "not reported before <date>" |
| 7 | Spelling inconsistencies: `Behrain`, `EU Countryies`, `Netherland` | Original label is preserved in a `source_label` column. Display names are corrected (Bahrain, EU Countries, Netherlands) |
| 8 | Fiscal-year labels vary (`FY 73`, `FY14`, `FY26`) | Parsed into a numeric `fiscal_year` (year in which June falls) |
| 9 | Dates in the older sheets are Excel serial numbers | Converted to month-start dates |
| 10 | Wide layout: about 500 columns across | Reshaped to a tidy long table (Section 4.2) |

---

## 3. Data integrity rules (non-negotiable)

1. **No value is ever edited, filled, interpolated, rounded in storage, or deleted** from the source (except the two invalid columns in 2.4, which are excluded and logged).
2. All source numbers are stored at full precision. Rounding happens **only at display time** (for example "US$ 41.6 billion").
3. Every row in the clean table carries its provenance: `source_sheet`, `source_row`, `source_column`.
4. Parents and children are never added together. Every chart declares its level (Section 4.3).
5. Fiscal-year figures shown on screen are the SBP's printed totals, which have been proven equal to the sum of months.
6. Anything derived (growth rates, shares, rankings, rolling totals) is calculated in one module (`metrics.py`) and tested. Derived values are never written back into the source table.
7. Display-only groupings (such as "Gulf", "Europe", "North America") live in a separate mapping file and are documented on the Notes page.
8. The dashboard shows the reporting-basis break and the revised flag wherever relevant, so no viewer is misled.
9. A **reconciliation report** is produced on every data load, and the app shows a small "Data verified" badge only if all checks pass.

---

## 4. Data architecture

### 4.1 Folder structure
```
remittances_dashboard/
├── app.py                     # entry point, navigation, global theme
├── pages/
│   ├── 1_Executive_Summary.py
│   ├── 2_The_Long_View.py
│   ├── 3_Where_The_Money_Comes_From.py
│   ├── 4_Regional_Deep_Dive.py
│   └── 5_Monthly_Patterns_And_Momentum.py
├── core/
│   ├── load_data.py           # reads the 3 sheets, builds the tidy tables
│   ├── validate.py            # all reconciliation checks
│   ├── metrics.py             # growth, share, rank, rolling calculations
│   ├── insights.py            # plain-English sentence generator
│   └── formatting.py          # US$ billion/million, percent, labels
├── ui/
│   ├── theme.py               # colours, fonts, Plotly template
│   ├── components.py          # banner, KPI cards, chart frame, footer
│   ├── styles.css             # all custom CSS
│   └── assets/                # SVG skyline, world dots, icons
├── data/
│   ├── raw/Homeremit_Arch.xlsx
│   ├── processed/remittances_long.parquet
│   ├── processed/entities.parquet
│   ├── processed/fy_reported.parquet
│   └── mappings/region_groups.csv
├── reports/load_report.md     # auto-generated each load
├── tests/                     # pytest checks for integrity and metrics
└── requirements.txt
```
All code comments and console messages are in clean professional English.

### 4.2 Tidy tables

**`remittances_long`** (one row per month and entity)

| Column | Meaning |
|---|---|
| `month_start` | Date (first day of month) |
| `fiscal_year` | Numeric (FY26 = 2026) |
| `month_of_fy` | 1 (July) to 12 (June) |
| `entity_id` | Key to the entities table |
| `value_musd` | Exact source value, US$ million |
| `is_revised` | True where the source header carries "R" |
| `basis` | `pre_jul2019` or `from_jul2019` |
| `source_sheet`, `source_row`, `source_col` | Provenance |

**`entities`** (one row per series)

| Column | Meaning |
|---|---|
| `entity_id`, `source_label`, `display_name` | Key, original label, corrected label |
| `level` | `total`, `group`, `country`, `subcountry` |
| `parent_id` | Parent entity where applicable |
| `region_group` | Display grouping (Section 4.4) |
| `first_reported_month` | First non-zero month (for display only) |
| `lat`, `lon` | Capital or centre point, used only for the bubble map |

**`fy_reported`**: the printed fiscal-year totals, kept separately and checked against monthly sums.

### 4.3 Level rules (to prevent double counting)
| View name | Which rows are used |
|---|---|
| **Total** | The Total row |
| **Corridor view (default for rankings)** | USA, UK, Saudi Arabia, **UAE as one country**, Bahrain, Kuwait, Qatar, Oman, the ten EU members individually, Norway, Switzerland, Australia, Canada, Japan, Malaysia, South Africa, South Korea. "Other Countries" is shown as "Other (not itemised)" and never ranked |
| **Region view** | The mapping in 4.4 applied to the same rows |
| **UAE detail view** | Dubai, Abu Dhabi, Sharjah, UAE Others |

### 4.4 Display regions (mapping file, editable, does not touch data)
| Region | Members |
|---|---|
| Gulf (GCC) | Saudi Arabia, UAE, Bahrain, Kuwait, Qatar, Oman |
| Europe | UK, the ten EU members, Norway, Switzerland |
| North America | USA, Canada |
| Asia-Pacific | Japan, Malaysia, South Korea, Australia |
| Africa | South Africa |
| Other (not itemised) | Other Countries (and, before Jul 2018, the countries that were inside it) |

### 4.5 Validation report (runs on every load)
The report is written to `reports/load_report.md` and shows:
- Number of months loaded per sheet (expected 456, 96, 99 valid) and the two excluded columns.
- Fiscal-year check: 54 of 54 equal to the sum of months.
- Parent and child sums: UAE, Other GCC, EU. All zero differences.
- Cash equals the sum of top-level rows. Total equals Cash plus encashment.
- Raw-versus-loaded spot test: 200 randomly chosen cells compared with the source.
- Latest month detected and revised flags found.

The sidebar shows **"Data verified"** only if every check passes.

---

## 5. Pages and charts

### 5.1 Design principles for non-technical viewers
1. **One page, one question.** Each page title is a plain question ("Where does the money come from?").
2. **Headline first.** Every chart has a one-sentence answer above it, generated from the data (Section 8). A viewer can read the sentence and skip the chart.
3. **Maximum five charts per page**, with white space around them.
4. **Plain labels, no jargon.** "Money sent home" rather than "inflows"; "compared with last year" rather than "YoY".
5. **Units shown in words.** "US$ billion" on screen, with exact US$ million values available in the hover.
6. **Teal means up or good, copper means down or attention.** Not red and green, which colour-blind viewers cannot separate.
7. **Direct labels beat legends.** Label lines and bars on the chart itself wherever possible.
8. **A "How to read this" hint** (small info icon) on any chart that is not a simple line or bar.
9. **Event markers** are consistent: a thin copper dashed line with a small label.

### 5.2 Page 1: Executive Summary ("How are remittances doing?")

```
┌─────────────────────────────────────────────────────────────┐
│  BANNER (full height)                                       │
├─────────────────────────────────────────────────────────────┤
│ [FY26 total] [Growth vs FY25] [Latest month] [Top source]   │  KPI cards
├──────────────────────────────────────┬──────────────────────┤
│ Annual remittances FY19 to FY26      │ Top 5 sources        │
│ (columns + growth line)              │ (horizontal bars)    │
├──────────────────────────────────────┴──────────────────────┤
│ This year so far vs last year (FY27 YTD vs FY26 same months)│
└─────────────────────────────────────────────────────────────┘
```

**KPI cards (4)**, each with a tiny sparkline and a one-line caption:
1. Latest full fiscal year total (FY26: about US$ 41.6 billion).
2. Growth compared with the previous year (teal up arrow or copper down arrow).
3. Latest month (Sep 2026) and its change against the same month last year.
4. Biggest source country in the latest year and its share.

**Charts**
| Chart | Type | What it shows |
|---|---|---|
| Annual remittances, FY19 to FY26 | Teal columns with a copper growth-rate line on a second axis | Size and speed of growth. The FY19 to FY20 break marker is shown |
| Top 5 sources, latest FY | Horizontal lollipop (dot and line) with share labels | Who sends the most |
| Year-to-date comparison | Two cumulative lines, FY27 against FY26, by month of the fiscal year | Whether the current year is ahead or behind |

### 5.3 Page 2: The Long View ("How did we get here?", 1972 to 2026)

| Chart | Type | What it shows |
|---|---|---|
| 54 years of remittances | Smooth teal area with copper event markers: oil boom years, 2008 crisis, COVID, Roshan Digital Accounts (Sep 2020), reporting basis change (Jul 2019). A **linear / log** switch for viewers who want the early years visible | The full growth story |
| Growth by decade | Small bar chart of average annual growth rate per decade | Which decades grew fastest |
| Milestones strip | A horizontal timeline of key totals (first US$ 1B year, 5B, 10B, 20B, 30B, 40B year) computed from the data | Easy-to-quote facts for presentations |
| Year-on-year change | Bars: teal for growth, copper for decline | How steady or volatile the series is |

Event labels are written in plain language, and each event marker is verified against the data before inclusion.

### 5.4 Page 3: Where the Money Comes From ("Who sends the most?")

| Chart | Type | What it shows |
|---|---|---|
| Source countries, selected fiscal year | **Treemap**, teal shades by share, copper highlight on the leader | Instant sense of proportion |
| How shares have shifted | **Slope chart** from FY19 to FY26 (two columns of countries joined by lines; copper if share fell, teal if rose) | Winners and losers in share. The reporting basis change is stated in the subtitle |
| Rank race | **Bump chart**, rank of the top 8 sources by fiscal year | Who overtook whom |
| Share over time | **100% stacked area** by region | How the mix has changed |
| Concentration | Single big number: "Top 3 sources send X% of the total", with a mini bar | How dependent the total is on a few countries |

Page filter: one **fiscal-year selector**. Everything on the page updates.

### 5.5 Page 4: Regional Deep Dive ("What about each region?")

| Chart | Type | What it shows |
|---|---|---|
| World bubble map | Dotted world base in light teal, copper bubbles sized by the latest fiscal year, countries only (groups such as "Other (not itemised)" are listed in a note beside the map) | Geography at a glance |
| Region comparison | Small multiples: one sparkline panel per region, same scale | Which regions are growing |
| Gulf drill-down | Stacked columns by Saudi Arabia, UAE, Other GCC, then a second chart splitting the UAE into Dubai, Abu Dhabi, Sharjah and Others | The heart of the story for Pakistan |
| Europe drill-down | Horizontal bars for UK, then each EU member, Norway and Switzerland | Where Europe's money comes from |
| Flow diagram | **Sankey**: Region, then Country, then Pakistan, for the selected fiscal year | A visual of money flowing home |

### 5.6 Page 5: Monthly Patterns and Momentum ("When does it arrive and what is the trend?")

| Chart | Type | What it shows |
|---|---|---|
| Seasonality heatmap | Grid: fiscal years (rows) by months (columns), teal intensity by value. Months are shown relative to each year's own average so growth does not drown the seasonal pattern; the hover shows the real value | Which months are strong every year. Caption text is generated from the data, not assumed |
| Typical month profile | Radial or line chart of the average relative strength of each month over the last 5 years | A single picture of the seasonal rhythm |
| Rolling 12-month total | Line with latest point highlighted | The underlying trend without month-to-month noise |
| What changed from last year | **Waterfall** from FY25 total to FY26 total, bars for each source's contribution (teal up, copper down) | Exactly where growth came from |
| Momentum table | Top 5 risers and top 5 fallers (change in US$ million and percent) with tiny in-cell bars | Quick list for discussion |

### 5.7 Notes and data page (small, linked from the sidebar footer)
Source and date, methodology break explanation, revised-data note, region mapping, the data verification summary, and a **Download data (CSV)** button for each view. No dense tables.

---

## 6. Visual identity: Teal, Copper and White

### 6.1 Colour palette
| Token | Hex | Use |
|---|---|---|
| Teal 900 | `#08323A` | Banner and sidebar darkest tone |
| Teal 800 | `#0B4A54` | Banner and sidebar gradient |
| Teal 700 | `#0F5F6B` | Primary brand, main chart colour |
| Teal 500 | `#1B8A97` | Secondary chart colour |
| Teal 300 | `#7CC4CC` | Soft fills, map base |
| Teal 100 | `#DDF1F3` | Card tints, hover |
| Copper 700 | `#9A5527` | Strong accent, decline emphasis |
| Copper 500 | `#C2703D` | Main accent, highlights, events |
| Copper 400 | `#D98E5A` | Secondary accent |
| Copper 200 | `#F0CDB2` | Soft accent fills |
| White | `#FFFFFF` | Cards, page background |
| Mist | `#F5F8F8` | Page background behind cards |
| Ink | `#12262B` | Main text |
| Slate | `#5A6B70` | Secondary text, axes |
| Border | `#E3EAEB` | Card borders, gridlines |

**Semantic rules:** teal means growth or favourable; copper means decline or attention; the single leading item in any chart is copper.

**Fixed colour per region** (identical on every page so viewers learn it once): Gulf `#0F5F6B`, Europe `#C2703D`, North America `#1B8A97`, Asia-Pacific `#D98E5A`, Africa `#4F6D8F`, Other `#9AA7AB`.

All text and chart colours pass a minimum contrast ratio of 4.5:1 against their background; copper-on-teal is used only for large decorative elements.

### 6.2 Typography
| Use | Font | Notes |
|---|---|---|
| Banner title and page titles | Playfair Display (bold serif, matching the crime dashboard banner) | Large, high contrast |
| Body, labels, chart text | Inter | Clean and readable at projector distance |
| Numbers in KPI cards | Inter, tabular figures | Digits align |
| Eyebrow labels | Inter, small caps, wide letter-spacing | |

Minimum on-screen text size is 13 px for chart text and 15 px for body text, with large KPI numbers at 36 to 44 px.

### 6.3 Top banner (same structure as the crime dashboard)

The banner is a rounded card with a teal gradient and layered decorative elements, all as inline HTML, CSS and SVG (no external images, so it never breaks).

| Layer | Crime dashboard | Remittances dashboard |
|---|---|---|
| Background | Crimson gradient with faint grid | Teal 900 to Teal 700 to Teal 500 diagonal gradient with a faint grid |
| Top edge | Hazard stripes | **Copper pinstripe band** (diagonal copper lines on teal, 14 px high) |
| Eyebrow label | CRIME & JUSTICE MONITOR | **ECONOMY & EXTERNAL SECTOR MONITOR** |
| Title | Pakistan Crime News Analytics | **Pakistan Workers' Remittances Analytics** |
| Subtitle | 2025 news coverage across 26,007 reports | **Country-wise inflows, FY73 to Sep 2026, in US dollars** |
| Chips | Period, News shown, Language | **Period** (Jul 1972 to Sep 2026), **Latest fiscal year** (FY26, US$ 41.6B), **Source** (State Bank of Pakistan) |
| Skyline silhouette | City buildings | **Gulf skyline on the left blending into Pakistani landmarks on the right**, in a slightly lighter teal, low opacity |
| Numbered pins on a dotted route | Four map pins | **Four copper pins on a faint dotted world map: the top four source countries of the latest fiscal year (computed from data, not hard-coded)** joined by dashed copper arcs flowing toward Pakistan |
| Crosshair icon | Target | **Coin ring with a globe line-art**, copper, top right |

**Chips** use a frosted-glass look (semi-transparent white fill, thin white border, backdrop blur).

**Banner variants**
- **Full banner** on the Executive Summary (about 230 px high).
- **Slim banner** on other pages (about 120 px high): same gradient and pinstripe, page title and one chip row, simplified skyline.

### 6.4 Sidebar (same design language)
- Teal 900 to Teal 800 vertical gradient with a very faint dotted-map texture.
- **Logo block** at top: a copper coin-ring icon and the text "Remittances Monitor".
- **Navigation** with simple line icons; the active page has a copper left bar and a lighter teal fill. Hover brightens the item.
- **Filter cards** in frosted glass under small-caps headings: *Period* (fiscal-year range slider), *Region* (multi-select chips), *Compare with* (previous year).
- **Presentation mode toggle**: hides filters and increases chart and font sizes for projection.
- **Footer**: "Source: State Bank of Pakistan", "Data through Sep 2026", and the **Data verified** badge in copper.

### 6.5 Cards and chart frames
White cards with 14 px rounded corners, 1 px Border colour, soft shadow. Each chart sits in a frame with: a headline sentence (Ink, semi-bold), the chart, and a thin footer line with units and the source. A copper accent line (3 px) marks the top-left of each card.

### 6.6 Effects (tasteful, presentation-safe)
| Effect | Where | Details |
|---|---|---|
| Animated dotted arcs | Banner | Slow dash movement toward Pakistan, about 12 seconds per loop |
| Pin pulse | Banner | Soft copper glow, about 3 seconds |
| Count-up numbers | KPI cards | Animate from zero over about 0.8 seconds on load |
| Card lift | All cards | 2 px rise and slightly stronger shadow on hover |
| Copper shimmer | Banner top edge and card accent lines | A single slow highlight sweep |
| Chart entrance | Charts | Short fade (no bouncing or spinning) |
| Reduced motion | Everything | If the viewer's system asks for reduced motion, all animations are turned off |

### 6.7 Chart styling rules (one shared Plotly template)
- White chart background, no outer border, thin Border-colour gridlines (horizontal only).
- No chart title inside the plot (the headline sentence is above it).
- Hover boxes: white with a copper left edge, text such as "Saudi Arabia · FY26 · US$ 9.78B · 23.5% of total".
- Mode bar hidden. Zoom is not needed for the audience.
- Axis labels in plain words with units. Numbers abbreviated (1.2B, 450M) with full values in hover.
- Legends only when direct labels are impractical, placed above the chart.

---

## 6A. Layout and responsiveness
- Designed at 1920 x 1080, checked at 1366 x 768.
- Content width about 1280 px, centred, 24 px gaps between cards.
- KPI row: four equal cards. Chart rows: 2 columns (7:5 ratio) or full width.
- Below 1100 px width, columns stack vertically.
- Print stylesheet: hides sidebar, removes shadows, keeps one page per page-view so a PDF is clean.

---

## 7. Interaction (kept deliberately small)
| Control | Scope | Notes |
|---|---|---|
| Fiscal-year range | Global (sidebar) | Defaults to the last 8 fiscal years |
| Region filter | Global | Defaults to all |
| Selected fiscal year | Pages 3 and 4 | Single dropdown above the charts |
| Linear / log scale | Page 2 only | Small toggle |
| Presentation mode | Global | Larger text, hides filters |
| Download CSV | Notes page and per chart | Exactly the data behind the chart |

No more than three controls are visible on any page at once.

---

## 8. Plain-English insight engine
Every headline sentence is built from templates and the data, never typed by hand, so it stays correct when the data changes. Examples of templates:

- "Workers sent home **US$ {fy_total} billion** in {fy_label}, **{up/down} {pct}%** compared with {prev_fy_label}."
- "**{country}** was the largest source, sending **{share}%** of the total."
- "The top three sources together account for **{share}%** of all remittances."
- "{region} grew the fastest since {fy_label}, adding **US$ {delta} billion**."
- "So far in {current_fy}, remittances are **{pct}% {above/below}** the same months last year."
- "The strongest month of the year is usually **{month}**." (only when the pattern is consistent across the last {n} years)

Rules: a template only fires when its condition is met; any comparison that crosses July 2019 appends "(reporting basis changed in July 2019)"; numbers are formatted consistently by `formatting.py`.

---

## 9. Build plan with review gates

Each stage ends with a review before the next begins.

| Stage | Work | What you review |
|---|---|---|
| **0** | This design guide | Approval of pages, palette and rules |
| **1** | Data pipeline, tidy tables, validation report | The cleaned table and the load report (all checks green) |
| **2** | Theme, banner (full and slim), sidebar, card and KPI components | A preview screen with sample numbers |
| **3** | Pages 1 and 2 | Look, wording, numbers against the source |
| **4** | Pages 3 and 4 | Charts, filters, map and Sankey |
| **5** | Page 5 and the Notes page | Heatmap, waterfall and momentum table |
| **6** | Polish, performance, print layout, tests | Final walkthrough as a non-technical viewer |
| **7** | Deployment (same GitHub and Streamlit Community Cloud pattern used on your other dashboards) | Live link |

Deliverables per stage are complete working files rather than partial changes.

---

## 10. Testing and acceptance checklist

**Data**
- [ ] 651 valid monthly columns loaded; 2 invalid columns excluded and logged.
- [ ] 54 of 54 fiscal-year totals match monthly sums.
- [ ] Parent and child sums match for UAE, Other GCC and EU in every month.
- [ ] 200 random cells equal the source exactly.
- [ ] No double counting in any chart (level rules in 4.3).

**Metrics**
- [ ] Growth, share, rank and rolling totals tested against hand-calculated examples.
- [ ] FY27 year-to-date compares the same months of FY26.

**Visual**
- [ ] Banner, sidebar and every page use only the palette in 6.1.
- [ ] Contrast checks pass; teal and copper are distinguishable in greyscale.
- [ ] Reporting-basis break marker appears on every chart that crosses 2019.
- [ ] Revised-data footnote appears wherever Aug-26 or Jun-26 is shown.

**Usability**
- [ ] A non-technical reviewer can state each page's message in 30 seconds.
- [ ] No page shows more than five charts or three controls.
- [ ] Presentation mode readable from the back of a meeting room.

**Performance**
- [ ] Data loaded once and cached; page switches under 3 seconds.

---

## 11. Risks and open decisions

| Item | Note | Proposed handling |
|---|---|---|
| July 2019 basis change makes the USA and EU look like sudden jumps | Real reporting change, not an economic event | **Split-series** on trend charts (shaded gap + label); **post-2019 default** on country charts (with opt-in toggle for pre-2019). Stated in chart subtitle and Notes page. |
| Latest months are partly revised | Aug-26 and Jun-26 carry "R" | Footnote; values can change in future SBP releases |
| Pre-2000s data is sparse for many countries | Zeros mean not reported | Charts begin at first reported month |
| Data updates | The file says newer data live on SBP EasyData | Pipeline written so a refreshed file can be dropped in and revalidated |
| Client branding | A client logo or name may be needed on the banner | Decide before Stage 2 |
| Dashboard title wording | "Pakistan Workers' Remittances Analytics" is a proposal | Confirm at Stage 0 |
| Forecast page | Not in version 1 | Can be added later with clear labelling |

---

## 12. Summary of key decisions
1. Streamlit and Plotly multi-page app, five pages, each answering one plain question.
2. Teal, Copper and White identity with a banner, sidebar and cards that share one design language and keep the structure of your crime dashboard.
3. Source data untouched. Every number reconciles to the workbook, and every known quirk is flagged on screen.
4. Headline sentences are generated from the data, so non-technical viewers can read the message without reading the chart.
5. Delivered in reviewable stages.
