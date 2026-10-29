"""
views/monthly_patterns.py
Page 5 — Monthly Patterns & Momentum ("When does it arrive and what is the trend?")

Elements per MD spec §5.6:
1. Seasonality heatmap — relative to each year's own average (not raw) so growth doesn't drown pattern
2. Typical month profile — radial/line chart of average relative strength per month (last 5 FYs)
3. Rolling 12-month total — line with latest point highlighted
4. Waterfall FY25→FY26 by source country contribution (teal up, copper down)
5. Momentum table — top 5 risers + top 5 fallers with in-cell bars (US$ M and %)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from core.metrics import load_clean_data, CORRIDOR_ENTITIES
from ui.theme import COLORS
from ui.layout.top_bar import render_top_bar

MONTH_ORDER = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
MONTH_NUM   = {m: i + 1 for i, m in enumerate(MONTH_ORDER)}


def _card(headline, subtitle="", info_hint=""):
    parts = [f'<div class="chart-headline">{headline}</div>']
    if subtitle:
        parts.append(f'<div class="chart-subtitle">{subtitle}</div>')
    if info_hint:
        parts.append(f'<div class="info-hint">ℹ {info_hint}</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_view():
    render_top_bar(slim=True,
                   title="Monthly Patterns & Momentum",
                   subtitle="When Does Money Arrive & Is Momentum Building?",
                   chip_text="High-Frequency Trends")

    df_m, df_fy, df_ent = load_clean_data()
    
    # Check global sidebar filters
    global_fy_range = st.session_state.get('fy_range', (2019, 2026))
    g_start, g_end = global_fy_range

    df_cash = df_m[df_m['entity_id'] == 'total_cash'].sort_values('month_start').copy()

    st.markdown("<h2 class='page-heading'>Monthly Patterns & Momentum</h2>", unsafe_allow_html=True)

    # ── Top Filter Bar for this page (Defaults to Sidebar global filter) ──
    available_years = [int(y) for y in sorted(df_cash['fiscal_year'].unique()) if y <= 2026]
    min_fy, max_fy = available_years[0], available_years[-1]

    f_col1, f_col2 = st.columns([1.5, 2.5])
    with f_col1:
        preset_choice = st.selectbox(
            "Select Period Preset:",
            [
                f"Global Filter ({g_start}–{g_end})",
                "Last 5 Fiscal Years (FY22–FY26)",
                "Last 10 Fiscal Years (FY17–FY26)",
                "Post-2019 Era (FY20–FY26)",
                "All 54 Years (FY73–FY26)",
                "Custom Year Range"
            ],
            index=0,
            key="mp_preset_choice"
        )

    if preset_choice == f"Global Filter ({g_start}–{g_end})":
        start_year, end_year = g_start, g_end
    elif preset_choice == "Last 5 Fiscal Years (FY22–FY26)":
        start_year, end_year = 2022, 2026
    elif preset_choice == "Last 10 Fiscal Years (FY17–FY26)":
        start_year, end_year = 2017, 2026
    elif preset_choice == "Post-2019 Era (FY20–FY26)":
        start_year, end_year = 2020, 2026
    elif preset_choice == "All 54 Years (FY73–FY26)":
        start_year, end_year = min_fy, max_fy
    else:
        with f_col2:
            start_year, end_year = st.slider(
                "Custom Fiscal Year Range:",
                min_value=min_fy,
                max_value=max_fy,
                value=(max(min_fy, g_start), min(max_fy, g_end)),
                key="mp_custom_slider"
            )

    # Filter all monthly cash data by active range
    heat_full = df_cash[(df_cash['fiscal_year'] >= start_year) & (df_cash['fiscal_year'] <= end_year)].copy()
    heat_full['month_name'] = heat_full['month_start'].dt.strftime('%b')

    # ─────────────────────────────────────────────────────────────────
    # 1. Seasonality Heatmap — relative to each year's own average
    # ─────────────────────────────────────────────────────────────────
    _card("Which months are strong — year by year?",
          f"Showing {start_year} to {end_year}. Colour = value relative to that year's monthly average (growth trend removed).",
          "Teal = above yearly average, Copper = below yearly average.")
    
    pivot_raw = heat_full.pivot_table(index='fiscal_year', columns='month_name', values='value_musd')
    available_months = [m for m in MONTH_ORDER if m in pivot_raw.columns]
    pivot_raw = pivot_raw[available_months]

    # Relative: divide each row by its own mean — removes growth trend
    row_means = pivot_raw.mean(axis=1)
    pivot_rel = pivot_raw.div(row_means, axis=0)

    # Dynamically scale heatmap height based on number of years selected (compact & proportional)
    num_years = len(pivot_rel)
    heat_height = max(180, min(num_years * 26 + 70, 520))

    fig_heat = px.imshow(
        pivot_rel,
        labels=dict(x="Month", y="Fiscal Year", color="Relative"),
        x=available_months,
        y=[f"FY{str(y)[-2:]}" for y in pivot_rel.index],
        color_continuous_scale=[
            [0.00, '#C2703D'],  # Copper (below avg)
            [0.25, '#F0CDB2'],
            [0.50, '#FFFFFF'],  # Neutral midpoint
            [0.75, '#7CC4CC'],
            [1.00, '#0F5F6B'],  # Teal (above avg)
        ],
        color_continuous_midpoint=1.0,
        aspect="auto",
        zmin=0.75, zmax=1.35
    )
    fig_heat.update_traces(
        customdata=pivot_raw.values,
        hovertemplate="FY%{y} · %{x}<br>Relative: %{z:.2f}× avg<br>Raw: US$ %{customdata:,.0f}M<extra></extra>"
    )
    fig_heat.update_layout(
        height=heat_height,
        margin=dict(l=20, r=30, t=10, b=20),
        coloraxis_colorbar=dict(title="× avg", tickformat=".1f")
    )
    st.plotly_chart(fig_heat, width='stretch')

    # ─────────────────────────────────────────────────────────────────
    # 2. Typical Month Profile / Average by Month Bar Chart
    # ─────────────────────────────────────────────────────────────────
    _card("Average by Month Bar Chart",
          f"12 bars calculated across selected period ({start_year} to {end_year}). Dashed copper line = overall period benchmark.")

    # Calculate average in US$ Billion for each of the 12 calendar months based on current period filter
    avg_by_month_m = heat_full.groupby('month_name')['value_musd'].mean().reindex(available_months)
    avg_by_month_bn = avg_by_month_m / 1000.0
    overall_mean_bn = avg_by_month_bn.mean()
    
    top_months = avg_by_month_bn.sort_values(ascending=False).head(2).index.tolist()
    top_months_str = " aur ".join(top_months) if top_months else ""

    # Metric Banner
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #E1E8E9; border-left:4px solid {COLORS['primary_teal']}; border-radius:8px; padding:8px 14px; margin-bottom:12px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
        <div>
            <span style="font-size:11px; color:#5A6B70; text-transform:uppercase; font-weight:700;">Period Benchmark ({start_year}–{end_year}): </span>
            <span style="font-size:16px; font-weight:700; color:{COLORS['primary_teal']};">US$ {overall_mean_bn:.2f}B / month</span>
        </div>
        <div style="font-size:12px; color:#5A6B70;">
            Peak Inflow Months: <strong style="color:{COLORS['primary_teal']};">{top_months_str}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    fig_avg_bar = go.Figure()
    bar_colors = [COLORS['primary_teal'] if v >= overall_mean_bn else COLORS['secondary_copper'] for v in avg_by_month_bn]
    bar_texts = [f"{v:.1f}B" if v < 3.0 else f"{v:.2f}B" for v in avg_by_month_bn]
    
    fig_avg_bar.add_trace(go.Bar(
        x=available_months,
        y=avg_by_month_bn,
        marker=dict(
            color=bar_colors,
            line=dict(color="rgba(0,0,0,0.05)", width=1)
        ),
        text=bar_texts,
        textposition='inside',
        insidetextanchor='start',
        textfont=dict(color='#FFFFFF', size=11.5, family="Inter, sans-serif"),
        hovertemplate="<b>%{x}</b><br>Average: US$ %{y:.2f} Billion<br>Status: %{customdata}<extra></extra>",
        customdata=["Above annual average" if v >= overall_mean_bn else "Below annual average" for v in avg_by_month_bn],
        showlegend=False
    ))
    
    fig_avg_bar.add_hline(
        y=overall_mean_bn,
        line_dash="dash",
        line_color=COLORS['secondary_copper'],
        line_width=1.8,
        opacity=0.85
    )
    
    last_month_col = available_months[-1] if available_months else 'Jun'
    fig_avg_bar.add_annotation(
        x=last_month_col,
        y=overall_mean_bn,
        text=f"Benchmark ({overall_mean_bn:.2f}B)",
        showarrow=False,
        xanchor='right',
        yanchor='bottom',
        font=dict(color=COLORS['secondary_copper'], size=11, family="Inter, sans-serif"),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor=COLORS['secondary_copper'],
        borderwidth=0.5,
        borderpad=3
    )

    fig_avg_bar.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(size=11, symbol='square', color=COLORS['primary_teal']),
        name="Above annual average"
    ))
    fig_avg_bar.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(size=11, symbol='square', color=COLORS['secondary_copper']),
        name="Below annual average"
    ))

    fig_avg_bar.update_layout(
        height=340,
        margin=dict(l=20, r=20, t=20, b=30),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor='#F0F0F0',
            ticksuffix="B",
            range=[0, max(avg_by_month_bn) * 1.18 if not avg_by_month_bn.empty else 4]
        ),
        xaxis=dict(
            title="",
            tickfont=dict(size=13, color='#12262B', family="Inter, sans-serif")
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="left",
            x=0.0,
            font=dict(size=11.5)
        ),
        bargap=0.32
    )
    st.plotly_chart(fig_avg_bar, use_container_width=True)

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────────
    # 3. Rolling 12-Month Total (Affected by Start Year)
    # ─────────────────────────────────────────────────────────────────
    _card("The underlying trend — smoothed over 12 months",
          f"Rolling 12-month sum from FY{str(start_year)[-2:]} to FY{str(end_year)[-2:]} showing true underlying run-rate.")

    df_cash['rolling_12m_bn'] = df_cash['value_musd'].rolling(12).sum() / 1000.0
    start_dt = pd.to_datetime(f"{start_year - 1}-07-01")
    end_dt = pd.to_datetime(f"{end_year}-06-30")
    recent_roll = df_cash[(df_cash['month_start'] >= start_dt) & (df_cash['month_start'] <= end_dt)].dropna(subset=['rolling_12m_bn'])
    
    if not recent_roll.empty:
        latest_roll = recent_roll.iloc[-1]
        fig_roll = go.Figure()
        fig_roll.add_trace(go.Scatter(
            x=recent_roll['month_start'], y=recent_roll['rolling_12m_bn'],
            mode='lines', fill='tozeroy',
            line=dict(color=COLORS['primary_teal'], width=2.5),
            fillcolor='rgba(15,95,107,0.10)',
            hovertemplate="%{x|%b %Y}: US$ %{y:.2f}B run-rate<extra></extra>",
            name="12M Rolling Total"
        ))
        fig_roll.add_trace(go.Scatter(
            x=[latest_roll['month_start']], y=[latest_roll['rolling_12m_bn']],
            mode='markers+text',
            marker=dict(size=10, color=COLORS['secondary_copper'],
                        line=dict(color='#FFF', width=2)),
            text=[f"US$ {latest_roll['rolling_12m_bn']:.2f}B"],
            textposition='top left', showlegend=False
        ))
        fig_roll.update_layout(
            height=300, margin=dict(l=10, r=20, t=10, b=30),
            xaxis=dict(title="Month"),
            yaxis=dict(title="12M Rolling Sum (US$ Billion)",
                       showgrid=True, gridcolor='#F0F0F0')
        )
        st.plotly_chart(fig_roll, width='stretch')
    else:
        st.info("No rolling data available for selected window.")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────────
    # 4. Where did growth come from? (Dynamic FY vs FY-1 based on selected period end year)
    # ─────────────────────────────────────────────────────────────────
    compare_fy = end_year
    base_fy = compare_fy - 1
    _card(f"Where did growth come from (FY{str(base_fy)[-2:]} → FY{str(compare_fy)[-2:]})?",
          f"Net change in formal remittances from FY{base_fy} to FY{compare_fy}. Teal = expanded, Copper = contracted (US$ Million).")

    corridors_curr = df_fy[(df_fy['fiscal_year'] == compare_fy) & (df_fy['entity_id'].isin(CORRIDOR_ENTITIES))].copy()
    corridors_prev = df_fy[(df_fy['fiscal_year'] == base_fy) & (df_fy['entity_id'].isin(CORRIDOR_ENTITIES))].set_index('entity_id')['value_musd']
    corridors_curr = corridors_curr.merge(df_ent[['entity_id', 'display_name']], on='entity_id', how='left')
    corridors_curr['diff_musd'] = corridors_curr.apply(
        lambda r: r['value_musd'] - corridors_prev.get(r['entity_id'], r['value_musd']), axis=1)
    
    top_gainers = corridors_curr[corridors_curr['diff_musd'] > 0].sort_values('diff_musd', ascending=False)
    decliners = corridors_curr[corridors_curr['diff_musd'] <= 0].sort_values('diff_musd', ascending=False)
    
    shown_gainers = top_gainers.head(6)
    other_gainers_val = top_gainers.iloc[6:]['diff_musd'].sum() if len(top_gainers) > 6 else 0
    
    chart_rows = []
    for _, r in shown_gainers.iterrows():
        chart_rows.append({'Corridor': r['display_name'], 'diff_musd': r['diff_musd']})
    if other_gainers_val > 0:
        chart_rows.append({'Corridor': 'Other Corridors (Net)', 'diff_musd': other_gainers_val})
    for _, r in decliners.iterrows():
        chart_rows.append({'Corridor': r['display_name'], 'diff_musd': r['diff_musd']})
        
    df_diff_chart = pd.DataFrame(chart_rows).sort_values('diff_musd', ascending=True)

    if not df_diff_chart.empty:
        bar_colors = [COLORS['primary_teal'] if v >= 0 else COLORS['secondary_copper'] for v in df_diff_chart['diff_musd']]
        bar_labels = [f"+${v:,.0f}M" if v >= 0 else f"-${abs(v):,.0f}M" for v in df_diff_chart['diff_musd']]

        fig_waterfall_alt = go.Figure(go.Bar(
            y=df_diff_chart['Corridor'],
            x=df_diff_chart['diff_musd'],
            orientation='h',
            marker=dict(
                color=bar_colors,
                line=dict(color="rgba(0,0,0,0.05)", width=1)
            ),
            text=bar_labels,
            textposition='outside',
            textfont=dict(size=11, family="Inter, sans-serif"),
            hovertemplate=f"<b>%{{y}}</b><br>Net Change FY{base_fy}→FY{compare_fy}: US$ %{{x:+,.1f}} Million<extra></extra>"
        ))
        fig_waterfall_alt.add_vline(x=0, line_width=1.2, line_color="#5A6B70")
        fig_waterfall_alt.update_layout(
            height=400,
            margin=dict(l=20, r=70, t=20, b=30),
            xaxis=dict(
                title=f"Net Change in Inflows FY{base_fy} vs FY{compare_fy} (US$ Million)",
                showgrid=True,
                gridcolor='#F0F0F0',
                zeroline=False
            ),
            yaxis=dict(
                title="",
                tickfont=dict(size=12, color='#12262B', family="Inter, sans-serif")
            )
        )
        st.plotly_chart(fig_waterfall_alt, use_container_width=True)

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────────
    # 5. Momentum Table — Top 5 risers + Top 5 fallers (Uses selected end year)
    # ─────────────────────────────────────────────────────────────────
    _card("Corridor Momentum: who moved the most?",
          f"Comparing recent months for selected fiscal year FY{compare_fy} vs prior year.")

    # Find the latest available month within the selected period
    available_period_months = df_m[(df_m['fiscal_year'] == compare_fy) & (df_m['entity_id'] == 'total_cash')]
    if not available_period_months.empty:
        m_latest = available_period_months['month_start'].max()
    else:
        m_latest = df_m['month_start'].max()
    m_prev_yr = m_latest - pd.DateOffset(years=1)

    curr_m = df_m[(df_m['month_start'] == m_latest) &
                  (df_m['entity_id'].isin(CORRIDOR_ENTITIES))].set_index('entity_id')['value_musd']
    prev_m = df_m[(df_m['month_start'] == m_prev_yr) &
                  (df_m['entity_id'].isin(CORRIDOR_ENTITIES))].set_index('entity_id')['value_musd']

    mom_rows = []
    for eid in CORRIDOR_ENTITIES:
        c_curr = curr_m.get(eid, 0.0)
        c_prev = prev_m.get(eid, 0.0)
        diff   = c_curr - c_prev
        pct    = (diff / c_prev * 100.0) if c_prev > 0 else 0.0
        name_r = df_ent[df_ent['entity_id'] == eid]['display_name']
        c_name = name_r.iloc[0] if not name_r.empty else eid
        bar_w  = min(abs(pct) / 30.0 * 100, 100)
        bar_col = COLORS['primary_teal'] if diff >= 0 else COLORS['secondary_copper']
        bar_html = (f'<div style="width:{bar_w:.0f}%;height:6px;border-radius:3px;'
                    f'background:{bar_col};margin-top:3px;"></div>')
        mom_rows.append({
            'Corridor': c_name,
            f'{m_latest.strftime("%b %Y")} (US$ M)': round(c_curr, 1),
            f'{m_prev_yr.strftime("%b %Y")} (US$ M)': round(c_prev, 1),
            'Δ US$ M': round(diff, 1),
            'Δ %': round(pct, 1),
            '_bar': bar_html,
            '_diff': diff
        })

    df_mom = pd.DataFrame(mom_rows)
    risers  = df_mom.sort_values('_diff', ascending=False).head(5)
    fallers = df_mom.sort_values('_diff', ascending=True).head(5)

    col_r, col_f = st.columns(2)
    with col_r:
        st.markdown(f"**🟢 Top 5 Risers** — {m_latest.strftime('%b %Y')} vs {m_prev_yr.strftime('%b %Y')}")
        rows_html = ""
        for _, row in risers.iterrows():
            rows_html += (
                f"<tr><td style='padding:6px 8px;font-weight:600'>{row['Corridor']}</td>"
                f"<td style='padding:6px 8px;text-align:right'>${row['Δ US$ M']:+.1f}M</td>"
                f"<td style='padding:6px 8px;text-align:right'>{row['Δ %']:+.1f}%</td>"
                f"<td style='padding:6px 8px;min-width:80px'>{row['_bar']}</td></tr>"
            )
        st.markdown(
            f"<table style='width:100%;border-collapse:collapse;font-size:12.5px'>"
            f"<thead><tr style='background:#F0F7F7;font-size:11px;color:#5A6B70'>"
            f"<th style='padding:6px 8px;text-align:left'>Corridor</th>"
            f"<th style='padding:6px 8px'>Δ US$ M</th>"
            f"<th style='padding:6px 8px'>Δ %</th>"
            f"<th style='padding:6px 8px'>Bar</th></tr></thead>"
            f"<tbody>{rows_html}</tbody></table>",
            unsafe_allow_html=True
        )

    with col_f:
        st.markdown(f"**🔴 Top 5 Fallers** — {m_latest.strftime('%b %Y')} vs {m_prev_yr.strftime('%b %Y')}")
        rows_html = ""
        for _, row in fallers.iterrows():
            rows_html += (
                f"<tr><td style='padding:6px 8px;font-weight:600'>{row['Corridor']}</td>"
                f"<td style='padding:6px 8px;text-align:right;color:#C2703D'>${row['Δ US$ M']:+.1f}M</td>"
                f"<td style='padding:6px 8px;text-align:right;color:#C2703D'>{row['Δ %']:+.1f}%</td>"
                f"<td style='padding:6px 8px;min-width:80px'>{row['_bar']}</td></tr>"
            )
        st.markdown(
            f"<table style='width:100%;border-collapse:collapse;font-size:12.5px'>"
            f"<thead><tr style='background:#FFF4EE;font-size:11px;color:#5A6B70'>"
            f"<th style='padding:6px 8px;text-align:left'>Corridor</th>"
            f"<th style='padding:6px 8px'>Δ US$ M</th>"
            f"<th style='padding:6px 8px'>Δ %</th>"
            f"<th style='padding:6px 8px'>Bar</th></tr></thead>"
            f"<tbody>{rows_html}</tbody></table>",
            unsafe_allow_html=True
        )

    # ── 6. Month-on-Month Growth Bars (Filtered to period) ──
    st.markdown("---")
    _card("Month-by-month: growing faster or slower than last year?",
          f"Monthly percentage change vs same month a year earlier within {start_year}–{end_year}.")

    period_cash = df_cash[(df_cash['fiscal_year'] >= start_year - 1) & (df_cash['fiscal_year'] <= end_year)].copy().reset_index(drop=True)
    mom_growth, mom_labels = [], []
    for i in range(len(period_cash)):
        curr_row = period_cash.iloc[i]
        curr_dt = curr_row['month_start']
        if curr_row['fiscal_year'] < start_year:
            continue
        prev_dt = curr_dt - pd.DateOffset(years=1)
        prev_match = period_cash[period_cash['month_start'] == prev_dt]
        if not prev_match.empty:
            prev_val = prev_match['value_musd'].iloc[0]
            pct = ((curr_row['value_musd'] - prev_val) / prev_val * 100.0) if prev_val > 0 else 0.0
            mom_growth.append(pct)
            mom_labels.append(curr_dt.strftime('%b %y'))

    if mom_growth:
        fig_mom = go.Figure(go.Bar(
            x=mom_labels, y=mom_growth,
            marker_color=[COLORS['primary_teal'] if v >= 0 else COLORS['secondary_copper']
                          for v in mom_growth],
            text=[f"{v:+.1f}%" for v in mom_growth],
            textposition='outside',
            hovertemplate="%{x}: %{y:+.1f}% vs same month last year<extra></extra>"
        ))
        fig_mom.add_hline(y=0, line_dash="solid", line_color="#888", line_width=0.8)
        fig_mom.update_layout(
            height=320, margin=dict(l=10, r=20, t=10, b=30),
            yaxis=dict(title="Growth vs Same Month Last Year (%)",
                       showgrid=True, gridcolor='#F0F0F0',
                       zeroline=True, zerolinecolor='#888')
        )
        st.plotly_chart(fig_mom, width='stretch')
