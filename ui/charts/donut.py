"""
donut.py
Reusable Donut Chart component.
Call this whenever a donut/pie breakdown is needed.
"""

import plotly.express as px
import plotly.graph_objects as go
from ui.theme import COLORS

def render_donut_chart(df, names_col, values_col, hole=0.5, title=None, height=350, custom_colors=None):
    """
    Renders a branded donut chart with direct percentage/labels and hover formatting.
    """
    if custom_colors is None:
        custom_colors = [
            COLORS['primary_teal'],
            COLORS['secondary_copper'],
            '#2E8B90',
            '#D97F52',
            '#4F9DA6',
            '#E0956E',
            '#9AA7AB'
        ]

    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        hole=hole,
        color_discrete_sequence=custom_colors
    )
    
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=20, b=25),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        title=dict(text=title, font=dict(size=14, color="#12262B")) if title else None
    )
    
    fig.update_traces(
        textinfo='percent+label',
        hovertemplate="<b>%{label}</b>: US$ %{value:,.1f}M (%{percent})<extra></extra>"
    )
    return fig
