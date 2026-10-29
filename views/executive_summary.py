"""
views/executive_summary.py
Page 1 — Executive Summary
The complete headline story at a glance

Required Elements (MD §5.2):
1. 4 KPI Cards: FY26 Total · Growth vs FY25 · Latest Month · Top Source Country
2. Annual bar chart + copper growth-rate line (FY19–FY26, dual axis) — with basis break
3. Cumulative YTD lines — FY27 vs FY25 vs FY24 (are we ahead or behind?)
4. Treemap — all source countries by FY26 share
5. Top 5 lollipop chart — ranked by FY26 value
6. Rolling 12-month momentum line — smoothed trend with shaded area
7. Month-on-month waterfall — last 12 months, teal = above last year, copper = below
8. Seasonality mini-heatmap — last 5 FYs × 12 months, relative to each year's own avg
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from core.metrics import (
    get_executive_kpis, get_annual_trend_data,
    get_corridor_rankings, load_clean_data, CORRIDOR_ENTITIES,
)
from core.formatting import fmt_usd_bn
from core.insights import get_executive_headline
from ui.layout.top_bar import render_top_bar
from ui.components.kpi_card import render_kpi_card
from ui.charts.annual_dual_axis import render_annual_dual_axis
from ui.charts.lollipop import render_horizontal_bar
from ui.theme import COLORS

# SBP fiscal-year month labels: July = month 1
_FY_MONTH_LABELS = {
    1: 'Jul', 2: 'Aug', 3: 'Sep',  4: 'Oct',
    5: 'Nov', 6: 'Dec', 7: 'Jan',  8: 'Feb',
    9: 'Mar', 10: 'Apr', 11: 'May', 12: 'Jun',
}


def render_view():
    # ── Top Banner ─────────────────────────────────────────────────────────
    render_top_bar()

    # ── Global Sidebar Filters ─────────────────────────────────────────────
    global_fy_range = st.session_state.get('fy_range', (2019, 2026))
    g_start, g_end = global_fy_range
    selected_regions = st.session_state.get('regions', ['Gulf (GCC)', 'Europe', 'North America', 'Asia-Pacific', 'Africa'])

    # ── Data Load ──────────────────────────────────────────────────────────
    kpis             = get_executive_kpis()
    df_m, df_fy, df_ent = load_clean_data()
    trend_df         = get_annual_trend_data()
    
    # Filter annual trend by global FY range
    trend_df_filtered = trend_df[(trend_df['fiscal_year'] >= g_start) & (trend_df['fiscal_year'] <= g_end)].copy()
    cash_m           = df_m[df_m['entity_id'] == 'total_cash'].sort_values('month_start').copy()

    # Sparkline series for KPI cards
    spark_fy_totals  = trend_df['value_bn'].tail(8).tolist()
    spark_fy_growths = trend_df['growth_pct'].dropna().tail(8).tolist()
    spark_monthly    = (cash_m['value_musd'].tail(12) / 1000.0).tolist()
    saudi_monthly    = df_m[df_m['entity_id'] == 'saudi_arabia'].sort_values('month_start')
    spark_saudi      = (saudi_monthly['value_musd'].tail(12) / 1000.0).tolist()

    # ── Page heading ───────────────────────────────────────────────────────
    st.markdown("<h2 class='page-heading'>Executive Summary</h2>", unsafe_allow_html=True)

    # ── Data-generated headline sentence (MD §8) ───────────────────────────
    headline = get_executive_headline(kpis)
    st.markdown(
        f'<div style="background:#F0F7F7; border-left:4px solid #0F5F6B;'
        f'padding:11px 18px; border-radius:0 8px 8px 0;'
        f'font-size:14px; color:#12262B; margin-bottom:18px;">{headline}</div>',
        unsafe_allow_html=True,
    )

    # ── 1. KPI Cards (4 columns) ───────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_kpi_card(
            title="FY26 Total",
            value=fmt_usd_bn(kpis['fy26_val_bn']),
            subtext="Formal inflows, latest full fiscal year",
            spark_points=spark_fy_totals,
            is_positive=True,
        )

    with c2:
        fy_pos = kpis['fy_growth_pct'] >= 0
        render_kpi_card(
            title="Growth vs FY25",
            value=f"{kpis['fy_growth_pct']:+.1f}%",
            subtext=f"{'Higher' if fy_pos else 'Lower'} than previous fiscal year",
            spark_points=spark_fy_growths,
            is_positive=fy_pos,
        )

    with c3:
        m_pos        = kpis['m_growth_pct'] >= 0
        revised_note = "* Revised figure" if kpis.get('is_latest_revised') else None
        render_kpi_card(
            title=f"Latest month: {kpis['latest_month_str']}",
            value=f"US$ {kpis['latest_month_val_bn']:.2f}B",
            subtext=f"{kpis['m_growth_pct']:+.1f}% vs same month last year",
            spark_points=spark_monthly,
            is_positive=m_pos,
            revised_note=revised_note,
        )

    with c4:
        render_kpi_card(
            title="Top source country",
            value=kpis['top_corridor_name'],
            subtext=f"{kpis['top_corridor_share']:.1f}% of FY26 total",
            spark_points=spark_saudi,
            is_positive=None,
        )

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # ── 2. Annual Dual-Axis (left) & Cumulative YTD (right) ───────────────
    col1, col2 = st.columns([1.5, 1.3])

    with col1:
        st.markdown(
            f'<div class="chart-headline">Annual Remittances &amp; Growth Rate (FY{str(g_start)[-2:]}–FY{str(g_end)[-2:]})</div>'
            '<div class="chart-subtitle">Teal columns = inflows (US$ Billion) &nbsp;·&nbsp; '
            'Copper line = year-on-year growth % &nbsp;·&nbsp; '
            'Shaded band = Jul 2019 reporting basis change</div>',
            unsafe_allow_html=True,
        )
        fig_annual = render_annual_dual_axis(
            trend_df_filtered,
            start_year=g_start,
            height=300,
            annotation_text="Jul 2019<br>Reporting basis<br>changed",
        )
        st.plotly_chart(fig_annual, use_container_width=True)

    with col2:
        st.markdown(
            '<div class="chart-headline">Year-to-Date: FY27 vs Prior Years</div>'
            '<div class="chart-subtitle">Cumulative inflows by month of fiscal year — '
            'is FY27 running ahead or behind?</div>',
            unsafe_allow_html=True,
        )
        fig_cum = go.Figure()

        for fy, color, width, dash, name in [
            (2024, '#A8B6B8',                     1.5, 'dot',   'FY24'),
            (2025, COLORS['secondary_copper'],     2.0, 'solid', 'FY25'),
            (2027, COLORS['primary_teal'],         3.0, 'solid', 'FY27 YTD (current)'),
        ]:
            sub = cash_m[cash_m['fiscal_year'] == fy].sort_values('month_of_fy').copy()
            if sub.empty:
                continue
            sub['cum_bn'] = sub['value_musd'].cumsum() / 1000.0
            x_labels = [_FY_MONTH_LABELS.get(int(m), f"M{m}") for m in sub['month_of_fy']]
            is_curr  = (fy == 2027)
            fig_cum.add_trace(go.Scatter(
                x=x_labels,
                y=sub['cum_bn'],
                mode='lines+markers+text' if is_curr else 'lines',
                name=name,
                line=dict(color=color, width=width, dash=dash),
                marker=dict(size=6) if is_curr else dict(size=0),
                text=[f"${v:.1f}B" for v in sub['cum_bn']] if is_curr else None,
                textposition='top left',
                hovertemplate=f"<b>{name}</b> · %{{x}}<br>Cumulative: US$ %{{y:.2f}}B<extra></extra>",
            ))

        fig_cum.update_layout(
            height=300,
            margin=dict(l=10, r=20, t=10, b=30),
            yaxis=dict(title="US$ Billion (cumulative)", showgrid=True,
                       gridcolor='#F0F0F0', ticksuffix="B"),
            xaxis=dict(title="Month of fiscal year"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        xanchor="right", x=1),
        )
        st.plotly_chart(fig_cum, use_container_width=True)

    # ── 3. Treemap (left) & Top 5 Lollipop (right) ────────────────────────
    corridors_fy26 = get_corridor_rankings(fiscal_year=2026)
    # Apply global region filter
    corridors_fy26 = corridors_fy26[corridors_fy26['region_group'].isin(selected_regions)].copy()
    if corridors_fy26.empty:
        corridors_fy26 = get_corridor_rankings(fiscal_year=2026)
    leader_name    = corridors_fy26.iloc[0]['display_name']
    corridors_fy26['highlight_color'] = [
        COLORS['secondary_copper'] if n == leader_name else COLORS['primary_teal']
        for n in corridors_fy26['display_name']
    ]

    col3, col4 = st.columns([1.5, 1.3])

    with col3:
        st.markdown(
            '<div class="chart-headline">All Source Countries — FY26 Share</div>'
            '<div class="chart-subtitle">Copper = leading corridor &nbsp;·&nbsp; '
            'Teal = all others &nbsp;·&nbsp; Click to zoom</div>',
            unsafe_allow_html=True,
        )
        fig_tree = px.treemap(
            corridors_fy26,
            names='display_name',
            parents=['All Remittances'] * len(corridors_fy26),
            values='value_musd',
            color='highlight_color',
            color_discrete_map={
                COLORS['secondary_copper']: COLORS['secondary_copper'],
                COLORS['primary_teal']:     COLORS['primary_teal'],
            },
        )
        fig_tree.update_traces(
            textinfo='label+percent parent',
            hovertemplate="<b>%{label}</b><br>US$ %{value:,.1f}M<extra></extra>",
        )
        fig_tree.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=20))
        st.plotly_chart(fig_tree, use_container_width=True)

    with col4:
        st.markdown(
            '<div class="chart-headline">Top 5 Sources — Ranked by FY26 Value</div>'
            '<div class="chart-subtitle">Share of total formal remittances</div>',
            unsafe_allow_html=True,
        )
        top5    = corridors_fy26.head(5).copy()
        fig_pop = render_horizontal_bar(
            top5, 'display_name', 'share_pct', height=320, is_percent=True
        )
        st.plotly_chart(fig_pop, use_container_width=True)

    # ── 4. Rolling 12-Month Momentum Line (full width) ─────────────────────
    st.markdown(
        '<div class="chart-headline">Rolling 12-Month Run-Rate</div>'
        '<div class="chart-subtitle">Smoothed trend — removes month-to-month noise '
        'to show the underlying momentum</div>',
        unsafe_allow_html=True,
    )
    roll_df              = cash_m.sort_values('month_start').copy()
    roll_df['rolling_12m_bn'] = roll_df['value_musd'].rolling(12).sum() / 1000.0
    roll_recent          = roll_df[roll_df['month_start'] >= '2016-01-01'].dropna()
    latest_roll          = roll_recent.iloc[-1]

    fig_roll = go.Figure()
    fig_roll.add_trace(go.Scatter(
        x=roll_recent['month_start'],
        y=roll_recent['rolling_12m_bn'],
        mode='lines', fill='tozeroy',
        name='12M Rolling Total',
        line=dict(color=COLORS['primary_teal'], width=2.5),
        fillcolor='rgba(15,95,107,0.12)',
        hovertemplate="%{x|%b %Y}: US$ %{y:.2f}B<extra></extra>",
    ))
    fig_roll.add_trace(go.Scatter(
        x=[latest_roll['month_start']],
        y=[latest_roll['rolling_12m_bn']],
        mode='markers+text',
        marker=dict(size=10, color=COLORS['secondary_copper'],
                    line=dict(color='#FFF', width=2)),
        text=[f"US$ {latest_roll['rolling_12m_bn']:.2f}B"],
        textposition='top left',
        showlegend=False,
        hovertemplate="Current run-rate: US$ %{y:.2f}B<extra></extra>",
    ))
    fig_roll.update_layout(
        height=280,
        margin=dict(l=10, r=20, t=10, b=30),
        xaxis=dict(title="Month"),
        yaxis=dict(title="12M Rolling Sum (US$ Billion)",
                   showgrid=True, gridcolor='#F0F0F0', ticksuffix="B"),
    )
    st.plotly_chart(fig_roll, use_container_width=True)

    # ── 5. Month-on-Month Waterfall (left) & Seasonality Heatmap (right) ──
    col5, col6 = st.columns([1.4, 1.4])

    with col5:
        st.markdown(
            '<div class="chart-headline">Month-by-Month vs Prior Year (Last 12 Months)</div>'
            '<div class="chart-subtitle">Teal = above same month last year &nbsp;·&nbsp; '
            'Copper = below</div>',
            unsafe_allow_html=True,
        )
        last12    = cash_m.tail(12).copy()
        wf_diffs  = []
        wf_labels = []
        for _, r in last12.iterrows():
            m_dt      = r['month_start']
            prev_m_dt = m_dt - pd.DateOffset(years=1)
            prev_row  = cash_m[cash_m['month_start'] == prev_m_dt]
            prev_val  = prev_row['value_musd'].iloc[0] if not prev_row.empty else r['value_musd']
            wf_diffs.append(r['value_musd'] - prev_val)
            wf_labels.append(m_dt.strftime('%b %y'))

        fig_wf_m = go.Figure(go.Waterfall(
            x=wf_labels, y=wf_diffs,
            measure=["relative"] * len(wf_diffs),
            decreasing=dict(marker=dict(color=COLORS['secondary_copper'])),
            increasing=dict(marker=dict(color=COLORS['primary_teal'])),
            connector=dict(line=dict(color="#B0DCDC", width=1)),
            hovertemplate="<b>%{x}</b><br>vs prior year: US$ %{y:+,.0f}M<extra></extra>",
        ))
        fig_wf_m.update_layout(
            height=290,
            margin=dict(l=10, r=20, t=10, b=30),
            yaxis=dict(title="Δ vs same month last year (US$ M)",
                       showgrid=True, gridcolor='#F0F0F0'),
        )
        st.plotly_chart(fig_wf_m, use_container_width=True)

    with col6:
        st.markdown(
            '<div class="chart-headline">Seasonal Pattern — Last 5 Fiscal Years</div>'
            '<div class="chart-subtitle">Colour = value relative to that year\'s own monthly average — '
            'growth trend removed so seasonal rhythm is visible</div>',
            unsafe_allow_html=True,
        )
        month_order = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                       'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        recent5_fy  = cash_m[cash_m['fiscal_year'].isin([2022, 2023, 2024, 2025, 2026])].copy()
        recent5_fy['month_name'] = recent5_fy['month_start'].dt.strftime('%b')

        pivot_raw = recent5_fy.pivot_table(
            index='fiscal_year', columns='month_name', values='value_musd'
        )
        available_months = [m for m in month_order if m in pivot_raw.columns]
        pivot_raw = pivot_raw[available_months]
        # Relative: each row ÷ its own mean → removes growth trend (MD §5.6)
        pivot_rel = pivot_raw.div(pivot_raw.mean(axis=1), axis=0)

        fig_mini_heat = px.imshow(
            pivot_rel,
            labels=dict(x="Month", y="Fiscal Year", color="× avg"),
            x=available_months,
            y=[f"FY{str(y)[-2:]}" for y in pivot_rel.index],
            color_continuous_scale=[
                [0.00, '#C2703D'],  # Copper (below avg)
                [0.25, '#F0CDB2'],  # Light copper
                [0.50, '#FFFFFF'],  # Neutral midpoint (1.0x avg)
                [0.75, '#7CC4CC'],  # Light teal
                [1.00, '#0F5F6B'],  # Dark teal (above avg)
            ],
            color_continuous_midpoint=1.0,
            aspect="auto",
            zmin=0.75,
            zmax=1.35,
        )
        fig_mini_heat.update_traces(
            customdata=pivot_raw.values,
            hovertemplate=(
                "FY%{y} · %{x}<br>"
                "Relative: %{z:.2f}× avg<br>"
                "Raw: US$ %{customdata:,.0f}M<extra></extra>"
            ),
        )
        fig_mini_heat.update_layout(
            height=290,
            margin=dict(l=10, r=20, t=10, b=30),
            coloraxis_colorbar=dict(title="× avg", tickformat=".1f"),
        )
        st.plotly_chart(fig_mini_heat, use_container_width=True)
