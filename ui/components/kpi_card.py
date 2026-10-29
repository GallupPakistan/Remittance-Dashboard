"""
kpi_card.py
Modular KPI Card component with embedded SVG sparklines.
Each card shows: title, large value, one-line data-generated caption, sparkline.
Arrow icon (↑ / ↓) and teal/copper coloring driven by is_positive flag.
"""

import streamlit as st


def _render_sparkline_svg(points, color="#1B8A97"):
    """Render a minimal SVG area sparkline from a list of float values."""
    if not points or len(points) < 2:
        return ""
    min_val, max_val = min(points), max(points)
    span = max_val - min_val if max_val != min_val else 1
    w, h = 100, 22
    coords = []
    for i, p in enumerate(points):
        x = (i / (len(points) - 1)) * w
        y = h - ((p - min_val) / span) * (h - 4) - 2
        coords.append(f"{x:.1f},{y:.1f}")
    path_d = "M " + " L ".join(coords)
    area_d = path_d + f" L {w} {h} L 0 {h} Z"
    return f"""<svg width="100%" height="22" viewBox="0 0 100 22" preserveAspectRatio="none" style="overflow:visible; display:block;"><defs><linearGradient id="sparkGrad_{color[1:]}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{color}" stop-opacity="0.25"/><stop offset="100%" stop-color="{color}" stop-opacity="0.0"/></linearGradient></defs><path d="{area_d}" fill="url(#sparkGrad_{color[1:]})"/><path d="{path_d}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>"""


def render_kpi_card(title, value, subtext, spark_points=None, is_positive=None,
                    revised_note=None):
    """
    Render a single KPI card.

    Parameters
    ----------
    title        : eyebrow label (small caps)
    value        : large primary number / text
    subtext      : one-line data-generated caption (plain text or HTML)
    spark_points : list of floats for the sparkline
    is_positive  : True → teal + ↑ arrow | False → copper + ↓ arrow | None → neutral
    revised_note : optional string shown as a small footnote (e.g. "* Revised figure")
    """
    # Choose arrow, accent colour, and spark colour
    if is_positive is True:
        arrow       = "↑ "
        accent_hex  = "#0F5F6B"   # Teal 700
        spark_color = "#1B8A97"   # Teal 500
    elif is_positive is False:
        arrow       = "↓ "
        accent_hex  = "#C2703D"   # Copper 500
        spark_color = "#C2703D"
    else:
        arrow       = ""
        accent_hex  = "#5A6B70"   # Slate (neutral)
        spark_color = "#1B8A97"

    spark_svg = _render_sparkline_svg(spark_points, color=spark_color) if spark_points else ""

    revised_html = f'<div class="mockup-kpi-revised">{revised_note}</div>' if revised_note else ""
    spark_html = f'<div class="mockup-kpi-spark">{spark_svg}</div>' if spark_svg else ""

    card_html = (
        f'<div class="mockup-kpi-card">'
        f'<div class="mockup-kpi-title">{title}</div>'
        f'<div class="mockup-kpi-val">{value}</div>'
        f'<div class="mockup-kpi-sub" style="color:{accent_hex};">{arrow}{subtext}</div>'
        f'{revised_html}'
        f'{spark_html}'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

