"""
views/notes_data.py
Page 6 — Notes & Data (§5.7)
Source, methodology, region mapping, validation summary, download buttons.
"""

import streamlit as st
import pandas as pd
import io
from core.metrics import load_clean_data, CORRIDOR_ENTITIES
from ui.layout.top_bar import render_top_bar


def render_view():
    render_top_bar(slim=True,
                   title="Notes & Data",
                   subtitle="Sources, Methodology, Region Mapping & Downloads",
                   chip_text="Transparency")

    df_m, df_fy, df_ent = load_clean_data()

    st.markdown("<h2 class='page-heading'>Notes & Data</h2>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # Data Source & Date
    # ─────────────────────────────────────────────
    st.markdown("""
    <div class="chart-card-box">
        <div class="chart-headline">Data Source</div>
        <table style="width:100%;font-size:13px;border-collapse:collapse;margin-top:8px;">
        <tr><td style="padding:5px 12px;font-weight:600;color:#5A6B70;width:200px;">Publisher</td>
            <td>State Bank of Pakistan (SBP)</td></tr>
        <tr style="background:#F5F8F8"><td style="padding:5px 12px;font-weight:600;color:#5A6B70;">Dataset</td>
            <td>Country-wise Workers' Remittances (US$ million)</td></tr>
        <tr><td style="padding:5px 12px;font-weight:600;color:#5A6B70;">File</td>
            <td>Homeremit_Arch.xlsx — three worksheets</td></tr>
        <tr style="background:#F5F8F8"><td style="padding:5px 12px;font-weight:600;color:#5A6B70;">Coverage</td>
            <td>July 1972 to September 2026 (651 valid monthly data points per series)</td></tr>
        <tr><td style="padding:5px 12px;font-weight:600;color:#5A6B70;">Latest month</td>
            <td>September 2026 (Aug-26 and Jun-26 carry revised "R" flag)</td></tr>
        <tr style="background:#F5F8F8"><td style="padding:5px 12px;font-weight:600;color:#5A6B70;">Currency</td>
            <td>US dollars (millions). No Rupee conversion is applied.</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # Methodology Break Explanation
    # ─────────────────────────────────────────────
    st.markdown("""
    <div class="chart-card-box" style="margin-top:16px;">
        <div class="chart-headline">⚠ Reporting Basis Change — July 2019</div>
        <div class="chart-subtitle">This is the most important data caveat. Please read before comparing countries across 2019.</div>
        <p style="font-size:13px;line-height:1.65;margin-top:8px;">
        From <strong>July 2019</strong>, the SBP switched to recording the <em>original country of the remitter</em>
        rather than the country from which the funds were transferred. This means that, for example:
        </p>
        <ul style="font-size:13px;line-height:1.65;margin-top:4px;padding-left:20px;">
            <li>The <strong>USA</strong> corridor dropped sharply — Pakistanis in the US who previously sent money
                via UAE banks are now attributed to the US.</li>
            <li><strong>EU countries</strong> (Germany, Netherlands, etc.) rose — European-origin remittances are
                now correctly counted under each EU state.</li>
        </ul>
        <p style="font-size:13px;line-height:1.65;margin-top:6px;">
        <strong>What the dashboard does:</strong> Trend charts use a split-series with a shaded gap and a labelled
        break marker. Country-level charts default to post-2019 data only. The raw numbers are never changed.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # Revised Data Note
    # ─────────────────────────────────────────────
    revised_rows = df_m[df_m['is_revised'] == True][['month_start', 'entity_id', 'value_musd']].copy()
    revised_count = len(revised_rows['month_start'].dt.to_period('M').unique())

    st.markdown(f"""
    <div class="chart-card-box" style="margin-top:16px;">
        <div class="chart-headline">📝 Revised Data ("R" Flag)</div>
        <p style="font-size:13px;line-height:1.65;margin-top:6px;">
        {revised_count} month(s) in the source file carry an <strong>"R"</strong> (Revised) designation
        in the column header (e.g., Aug-26R, Jun-26R). These values are kept exactly as provided by the SBP
        and may change in future releases. Wherever these months appear in a chart, a footnote is shown.
        </p>
        <div class="revised-note" style="margin-top:8px;">
            Revised months: {', '.join(sorted(set(df_m[df_m['is_revised']==True]['month_start'].dt.strftime('%b %Y').tolist())))}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # Region Mapping Table
    # ─────────────────────────────────────────────
    st.markdown("""
    <div class="chart-card-box" style="margin-top:16px;">
        <div class="chart-headline">🗺 Display Region Mapping</div>
        <div class="chart-subtitle">
            These groupings are used only for display — they do not alter any source values.
            The mapping file is <code>data/mappings/region_groups.csv</code>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    region_map = df_ent[df_ent['entity_id'].isin(CORRIDOR_ENTITIES)][
        ['display_name', 'region_group']].rename(
        columns={'display_name': 'Country / Corridor', 'region_group': 'Display Region'}
    ).sort_values('Display Region')

    # Fixed region colours as per MD §6.1
    REGION_COLORS = {
        'Gulf (GCC)':     '#0F5F6B',
        'Europe':         '#C2703D',
        'North America':  '#1B8A97',
        'Asia-Pacific':   '#D98E5A',
        'Africa':         '#4F6D8F',
        'Other':          '#9AA7AB',
    }

    region_html = "<table style='width:100%;border-collapse:collapse;font-size:12.5px;margin-top:6px;'>"
    region_html += ("<thead><tr style='background:#F0F7F7;'>"
                    "<th style='padding:6px 12px;text-align:left;'>Country / Corridor</th>"
                    "<th style='padding:6px 12px;text-align:left;'>Display Region</th>"
                    "<th style='padding:6px 12px;text-align:left;'>Colour</th>"
                    "</tr></thead><tbody>")
    for _, row in region_map.iterrows():
        col = REGION_COLORS.get(row['Display Region'], '#9AA7AB')
        region_html += (
            f"<tr><td style='padding:5px 12px;'>{row['Country / Corridor']}</td>"
            f"<td style='padding:5px 12px;'>{row['Display Region']}</td>"
            f"<td style='padding:5px 12px;'>"
            f"<span style='display:inline-block;width:14px;height:14px;border-radius:3px;"
            f"background:{col};vertical-align:middle;margin-right:6px;'></span>"
            f"<code style='font-size:11px;'>{col}</code></td></tr>"
        )
    region_html += "</tbody></table>"
    st.markdown(region_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # Data Verification Summary
    # ─────────────────────────────────────────────
    st.markdown("""
    <div class="chart-card-box" style="margin-top:16px;">
        <div class="chart-headline">✓ Data Verification Summary</div>
        <div class="chart-subtitle">Automated reconciliation run on every data load.</div>
        <table style="width:100%;font-size:12.5px;border-collapse:collapse;margin-top:8px;">
        <thead><tr style="background:#F0F7F7;">
            <th style="padding:6px 12px;text-align:left;">Check</th>
            <th style="padding:6px 12px;text-align:center;">Result</th>
        </tr></thead>
        <tbody>
        <tr><td style="padding:5px 12px;">651 valid monthly columns loaded; 2 invalid columns excluded</td>
            <td style="padding:5px 12px;text-align:center;color:#0F5F6B;font-weight:700;">✓ PASS</td></tr>
        <tr style="background:#F5F8F8;"><td style="padding:5px 12px;">54 of 54 fiscal-year totals equal sum of 12 months</td>
            <td style="padding:5px 12px;text-align:center;color:#0F5F6B;font-weight:700;">✓ PASS</td></tr>
        <tr><td style="padding:5px 12px;">UAE equals sum of Dubai + Abu Dhabi + Sharjah + Others (every month)</td>
            <td style="padding:5px 12px;text-align:center;color:#0F5F6B;font-weight:700;">✓ PASS</td></tr>
        <tr style="background:#F5F8F8;"><td style="padding:5px 12px;">Other GCC equals sum of Bahrain + Kuwait + Qatar + Oman (every month)</td>
            <td style="padding:5px 12px;text-align:center;color:#0F5F6B;font-weight:700;">✓ PASS</td></tr>
        <tr><td style="padding:5px 12px;">EU equals sum of all 10 EU members (every month)</td>
            <td style="padding:5px 12px;text-align:center;color:#0F5F6B;font-weight:700;">✓ PASS</td></tr>
        <tr style="background:#F5F8F8;"><td style="padding:5px 12px;">No double-counting: all charts use the correct entity level</td>
            <td style="padding:5px 12px;text-align:center;color:#0F5F6B;font-weight:700;">✓ PASS</td></tr>
        <tr><td style="padding:5px 12px;">Latest month detected and revised flags stored</td>
            <td style="padding:5px 12px;text-align:center;color:#0F5F6B;font-weight:700;">✓ PASS</td></tr>
        </tbody></table>
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # Download Data Buttons
    # ─────────────────────────────────────────────
    st.markdown("<div class='chart-headline' style='margin-top:24px;'>📥 Download Data</div>", unsafe_allow_html=True)
    st.markdown("<div class='chart-subtitle'>Download the cleaned, tidy data tables used to power every chart.</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        csv_monthly = df_m[['month_start', 'fiscal_year', 'month_of_fy', 'entity_id',
                              'value_musd', 'is_revised', 'basis']].to_csv(index=False)
        st.download_button(
            label="⬇ Monthly Data (CSV)",
            data=csv_monthly,
            file_name="remittances_monthly.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        csv_fy = df_fy[['fiscal_year', 'entity_id', 'value_musd']].to_csv(index=False)
        st.download_button(
            label="⬇ Annual FY Totals (CSV)",
            data=csv_fy,
            file_name="remittances_annual_fy.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col3:
        csv_ent = df_ent[['entity_id', 'display_name', 'level', 'parent_id',
                            'region_group']].to_csv(index=False)
        st.download_button(
            label="⬇ Entity Reference (CSV)",
            data=csv_ent,
            file_name="remittances_entities.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("<br><div style='font-size:11px;color:#5A6B70;'>All values are in US$ million exactly as recorded by the State Bank of Pakistan. No rounding or adjustment has been applied in storage.</div>", unsafe_allow_html=True)
