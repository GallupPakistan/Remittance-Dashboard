"""
cumulative_lines.py
Reusable Cumulative Year-to-Date lines component (FY27 vs FY26).
"""

import plotly.graph_objects as go
from ui.theme import COLORS

def render_cumulative_ytd(fy26_series, fy27_series, height=290):
    fig = go.Figure()
    
    # FY26 line (Copper)
    fig.add_trace(go.Scatter(
        x=[f"M{m}" for m in fy26_series['month_of_fy']],
        y=fy26_series['cum_val'],
        mode='lines',
        name='FY26',
        line=dict(color=COLORS['secondary_copper'], width=2)
    ))
    
    # FY27 line (Teal)
    fig.add_trace(go.Scatter(
        x=[f"M{m}" for m in fy27_series['month_of_fy']],
        y=fy27_series['cum_val'],
        mode='lines',
        name='FY27',
        line=dict(color=COLORS['primary_teal'], width=2.5)
    ))
    
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=20, t=10, b=30),
        yaxis=dict(title="", showgrid=True, gridcolor='#F0F0F0'),
        xaxis=dict(title=""),
        showlegend=False
    )
    return fig
