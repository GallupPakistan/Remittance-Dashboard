"""
lollipop.py
Reusable Horizontal Bar / Lollipop chart for corridor shares.
"""

import plotly.graph_objects as go
from ui.theme import COLORS

def render_horizontal_bar(df, name_col, value_col, height=290, is_percent=True, color=None):
    if color is None:
        color = COLORS['primary_teal']
        
    sorted_df = df.sort_values(value_col, ascending=True)
    suffix = "%" if is_percent else "M"
    
    fig = go.Figure(go.Bar(
        x=sorted_df[value_col],
        y=sorted_df[name_col],
        orientation='h',
        marker_color=color,
        text=[f"{v:.1f}{suffix}" for v in sorted_df[value_col]],
        textposition='outside',
        name="Lollipop"
    ))
    
    max_val = sorted_df[value_col].max() * 1.25 if not sorted_df.empty else 30
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=40, t=10, b=30),
        xaxis=dict(title="", showgrid=True, gridcolor='#F0F0F0', ticksuffix=suffix, range=[0, max_val]),
        yaxis=dict(title=""),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font=dict(size=11))
    )
    return fig
