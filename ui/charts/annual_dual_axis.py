"""
annual_dual_axis.py
Reusable Dual-Axis chart: Teal columns for annual inflows (US$ Billion) +
Copper line for YoY growth rate on a second axis.
Includes a copper dashed vline + shaded vrect at the Jul-2019 methodology break.
"""

import plotly.graph_objects as go
import pandas as pd
from ui.theme import COLORS


def render_annual_dual_axis(trend_df, start_year=2019, height=290,
                            annotation_text=None):
    recent = trend_df[trend_df['fiscal_year'] >= start_year].copy()
    recent['fy_label'] = [f"FY{str(y)[-2:]}" for y in recent['fiscal_year']]

    fig = go.Figure()

    # ── Primary axis: Teal columns in US$ Billion ──────────────────────
    fig.add_trace(go.Bar(
        x=recent['fy_label'],
        y=recent['value_musd'] / 1000.0,          # convert M → B
        name="Annual Inflows (US$ B)",
        marker_color=COLORS['primary_teal'],
        yaxis='y',
        hovertemplate="<b>%{x}</b><br>US$ %{y:.2f} Billion<extra></extra>"
    ))

    # ── Secondary axis: Copper YoY growth-rate line ─────────────────────
    growth_trace = recent.dropna(subset=['growth_pct']).copy()
    growth_trace['formatted_growth'] = growth_trace['growth_pct'].apply(lambda g: f"{g:+.1f}%")
    fig.add_trace(go.Scatter(
        x=growth_trace['fy_label'],
        y=growth_trace['growth_pct'],
        customdata=growth_trace['formatted_growth'],
        name="YoY Growth (%)",
        mode='lines+markers',
        line=dict(color=COLORS['secondary_copper'], width=2.5),
        marker=dict(size=6, color=COLORS['secondary_copper']),
        yaxis='y2',
        hovertemplate="<b>%{x}</b><br>Growth: %{customdata}<extra></extra>"
    ))

    # ── Methodology break marker (Jul 2019 → shows between FY19 & FY20) ─
    # For categorical axes in Plotly, numeric coordinates represent category midpoints/boundaries
    fy_labels = recent['fy_label'].tolist()
    if 'FY20' in fy_labels:
        break_idx = fy_labels.index('FY20')  # index 1
        # Shaded region between the end of FY19 column and start of FY20 column
        fig.add_vrect(
            x0=break_idx - 0.75,
            x1=break_idx - 0.25,
            fillcolor="rgba(194,112,61,0.12)",
            layer="below",
            line_width=0
        )
        fig.add_vline(
            x=break_idx - 0.5,
            line_width=1.5,
            line_dash="dash",
            line_color=COLORS['secondary_copper'],
            opacity=0.75
        )
        fig.add_annotation(
            x=break_idx - 0.5,
            y=recent['value_musd'].max() / 1000.0 * 0.90,
            yref='y',
            text=annotation_text or "Jul 2019<br>Reporting basis<br>changed",
            showarrow=False,
            font=dict(size=9, color="#9A5527"),
            bgcolor="rgba(255,244,238,0.92)",
            bordercolor=COLORS['secondary_copper'],
            borderwidth=1,
            borderpad=4,
            align="center"
        )

    fig.update_layout(
        height=height,
        margin=dict(l=10, r=40, t=10, b=30),
        yaxis=dict(
            title="US$ Billion",
            showgrid=True,
            gridcolor='#F0F0F0',
            ticksuffix="B"
        ),
        yaxis2=dict(
            title="YoY Growth %",
            overlaying='y',
            side='right',
            showgrid=False,
            ticksuffix="%",
            zeroline=True,
            zerolinecolor='#D5E0E1',
            zerolinewidth=1
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.30,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        ),
        bargap=0.35
    )
    return fig

