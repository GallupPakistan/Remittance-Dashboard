"""
views/the_long_view.py
Page 2 — The Long View
54 years of growth, from oil booms to digital remittances

Required Elements:
1. Full 54-year area chart (FY73–FY26) with split-series at Jul-2019 methodology break + event markers
2. Growth by decade bar chart — average annual growth rate per decade
3. Milestones horizontal timeline — first $1B, $5B, $10B, $20B, $30B, $40B year
4. Year-on-year change bars — teal = growth, copper = decline, all 54 years
5. Log-scale vs linear toggle line chart — shows early years properly
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from core.metrics import get_annual_trend_data
from ui.theme import COLORS
from ui.layout.top_bar import render_top_bar

def render_view():
    render_top_bar(slim=True, title="The Long View (1972 to 2026)", subtitle="54 Years of Growth: From Oil Booms to Digital Inflows", chip_text="54 Fiscal Years")

    global_fy_range = st.session_state.get('fy_range', (1973, 2026))
    g_start, g_end = global_fy_range

    df_trend_all = get_annual_trend_data()
    # Filter by global range
    df_trend = df_trend_all[(df_trend_all['fiscal_year'] >= g_start) & (df_trend_all['fiscal_year'] <= g_end)].copy()
    total_54yr = df_trend['value_bn'].sum()

    st.markdown(f"""
    <div style="background-color: #F0F7F7; border-left: 4px solid #0F5F6B; padding: 12px 18px; border-radius: 0 8px 8px 0; margin-bottom: 20px; font-size: 14.5px; color: #12262B;">
        💡 For selected period (FY{str(g_start)[-2:]} to FY{str(g_end)[-2:]}), overseas Pakistanis channeled <strong>US$ {total_54yr:.1f} Billion</strong> in formal remittances.
    </div>
    """, unsafe_allow_html=True)

    # ── 3. Milestones Horizontal Timeline ──
    st.markdown("### 🏆 Remittances Milestone Timeline")
    milestone_targets = [1.0, 5.0, 10.0, 20.0, 30.0, 40.0]
    m_cols = st.columns(len(milestone_targets))
    for idx, target in enumerate(milestone_targets):
        hit = df_trend[df_trend['value_bn'] >= target].head(1)
        with m_cols[idx]:
            if not hit.empty:
                fy_hit = int(hit['fiscal_year'].iloc[0])
                val_hit = hit['value_bn'].iloc[0]
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E1E8E9; border-top:3px solid {COLORS['secondary_copper']}; border-radius:8px; padding:10px 12px; text-align:center;">
                    <div style="font-size:11px; font-weight:700; color:#5A6B70; text-transform:uppercase;">First US$ {int(target)}B</div>
                    <div style="font-size:20px; font-weight:700; color:{COLORS['primary_teal']}; margin:2px 0;">FY{str(fy_hit)[-2:]}</div>
                    <div style="font-size:11px; color:#5A6B70;">US$ {val_hit:.2f}B</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # ── 1 & 5. Full Area Chart + Split-Series + Event Markers + Linear/Log Toggle ──
    scale_col, _ = st.columns([1.5, 3.5])
    with scale_col:
        scale_type = st.radio("Chart Scale (Linear vs Log-Scale):", ["Linear Scale", "Logarithmic Scale (Log)"], horizontal=True)

    is_log = (scale_type == "Logarithmic Scale (Log)")
    fig_54 = go.Figure()

    # Pre-2020 Segment (Pre-July 2019 basis) within selected FY range
    pre_20 = df_trend[df_trend['fiscal_year'] < 2020]
    if not pre_20.empty:
        fig_54.add_trace(go.Scatter(
            x=pre_20['fiscal_year'],
            y=pre_20['value_bn'],
            mode='lines',
            fill='tozeroy',
            name='Pre-2019 Basis',
            line=dict(color=COLORS['primary_teal'], width=2.5),
            fillcolor='rgba(15, 95, 107, 0.18)',
            hovertemplate="FY%{x}: US$ %{y:.2f}B<extra></extra>"
        ))

    # Post-2020 Segment (Post-July 2019 basis - split series) within selected FY range
    post_20 = df_trend[df_trend['fiscal_year'] >= 2020]
    if not post_20.empty:
        fig_54.add_trace(go.Scatter(
            x=post_20['fiscal_year'],
            y=post_20['value_bn'],
            mode='lines',
            fill='tozeroy',
            name='Post-2019 Remitter Origin Basis',
            line=dict(color=COLORS['secondary_copper'], width=2.8),
            fillcolor='rgba(194, 112, 61, 0.18)',
            hovertemplate="FY%{x}: US$ %{y:.2f}B<extra></extra>"
        ))

    # Event Markers within selected range
    events = [
        {'fy': 1976, 'label': "Gulf Oil Boom (FY76)", 'y': 0.8},
        {'fy': 2002, 'label': "Post-9/11 Banking Reforms (FY02)", 'y': 3.5},
        {'fy': 2008, 'label': "Global Financial Crisis (FY08)", 'y': 7.5},
        {'fy': 2019, 'label': "Jul 2019 Reporting Basis Break", 'y': 22.0},
        {'fy': 2021, 'label': "COVID & Roshan Digital (FY21)", 'y': 31.0}
    ]

    for ev in events:
        if g_start <= ev['fy'] <= g_end:
            fig_54.add_vline(
                x=ev['fy'],
                line_width=1.2,
                line_dash="dash",
                line_color=COLORS['secondary_copper']
            )
            fig_54.add_annotation(
                x=ev['fy'],
                y=ev['y'],
                text=ev['label'],
                showarrow=True,
                arrowhead=2,
                ax=-30 if ev['fy'] > 2015 else 40,
                ay=-35,
                bgcolor="#FFF4EE",
                bordercolor=COLORS['secondary_copper'],
                font=dict(size=10, color="#743714")
            )

    fig_54.update_layout(
        height=420,
        margin=dict(l=30, r=30, t=30, b=40),
        xaxis=dict(title=f"Fiscal Year (FY{str(g_start)[-2:]} to FY{str(g_end)[-2:]})", range=[g_start - 0.5, g_end + 0.5]),
        yaxis=dict(title="US$ Billion" if not is_log else "US$ Billion (Log Scale)", type="log" if is_log else "linear", showgrid=True, gridcolor='#F0F0F0'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_54, width='stretch')

    # ── 2 & 4. Growth by Decade & Year-on-Year Change Bars ──
    col1, col2 = st.columns([1.2, 1.6])
    with col1:
        st.markdown("### Growth by Decade (Avg Annual Growth Rate)")
        decades = [
            {'decade': '1970s (FY73-80)', 'sub': df_trend[(df_trend['fiscal_year'] >= 1973) & (df_trend['fiscal_year'] <= 1980)]},
            {'decade': '1980s (FY81-90)', 'sub': df_trend[(df_trend['fiscal_year'] >= 1981) & (df_trend['fiscal_year'] <= 1990)]},
            {'decade': '1990s (FY91-00)', 'sub': df_trend[(df_trend['fiscal_year'] >= 1991) & (df_trend['fiscal_year'] <= 2000)]},
            {'decade': '2000s (FY01-10)', 'sub': df_trend[(df_trend['fiscal_year'] >= 2001) & (df_trend['fiscal_year'] <= 2010)]},
            {'decade': '2010s (FY11-20)', 'sub': df_trend[(df_trend['fiscal_year'] >= 2011) & (df_trend['fiscal_year'] <= 2020)]},
            {'decade': '2020s (FY21-26)', 'sub': df_trend[(df_trend['fiscal_year'] >= 2021) & (df_trend['fiscal_year'] <= 2026)]},
        ]
        decade_data = [{'decade': d['decade'], 'avg_growth': d['sub']['growth_pct'].mean()} for d in decades]
        df_decades = pd.DataFrame(decade_data)
        
        fig_dec = go.Figure(go.Bar(
            x=df_decades['decade'],
            y=df_decades['avg_growth'],
            marker_color=[COLORS['primary_teal'] if v >= 0 else COLORS['secondary_copper'] for v in df_decades['avg_growth']],
            text=[f"{v:+.1f}%" for v in df_decades['avg_growth']],
            textposition='auto'
        ))
        fig_dec.update_layout(height=340, margin=dict(l=20, r=20, t=20, b=50), xaxis=dict(tickangle=-30), yaxis=dict(title="Avg Growth Rate %", showgrid=True, gridcolor='#F0F0F0'))
        st.plotly_chart(fig_dec, width='stretch')

    with col2:
        st.markdown("### Year-on-Year Change (Teal = Growth, Copper = Decline)")
        growth_bars = df_trend.dropna(subset=['growth_pct']).copy()
        fig_yoy = go.Figure(go.Bar(
            x=growth_bars['fiscal_year'],
            y=growth_bars['growth_pct'],
            marker_color=[COLORS['primary_teal'] if g >= 0 else COLORS['secondary_copper'] for g in growth_bars['growth_pct']],
            hovertemplate="<b>FY%{x}</b>: %{y:+.1f}%<extra></extra>"
        ))
        fig_yoy.update_layout(
            height=340,
            margin=dict(l=20, r=20, t=20, b=30),
            xaxis=dict(title="Fiscal Year", tickmode='linear', tick0=1975, dtick=5),
            yaxis=dict(title="YoY Growth %", showgrid=True, gridcolor='#F0F0F0', zeroline=True, zerolinecolor='#666')
        )
        st.plotly_chart(fig_yoy, width='stretch')
