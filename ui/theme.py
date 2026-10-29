"""
theme.py
Visual identity definitions: Teal, Copper, and Crisp White.
Fulfills Design Specification Section 6.
"""

import plotly.graph_objects as go
import plotly.io as pio

# Color Palette
COLORS = {
    'primary_teal': '#006B70',        # Deep Teal
    'teal_light': '#E6F4F4',          # Teal background tint
    'teal_hover': '#005357',
    'secondary_copper': '#C36839',    # Warm Copper / Attention
    'copper_light': '#FAF0E8',        # Copper tint
    'charcoal_text': '#1D2A30',       # Dark Charcoal for high readability
    'muted_slate': '#5C707A',         # Secondary text
    'card_bg': '#FFFFFF',             # Crisp White card
    'page_bg': '#F7FAFA',             # Very soft neutral backdrop
    'border_subtle': '#E2EBEB',       # Soft card border
    'border_accent': '#006B70',
}

# Plotly Custom Template
def apply_plotly_theme():
    template = go.layout.Template()
    template.layout = go.Layout(
        font=dict(family="Segoe UI, Inter, sans-serif", color=COLORS['charcoal_text'], size=13),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        colorway=[
            COLORS['primary_teal'],
            COLORS['secondary_copper'],
            '#2E8B90',
            '#D97F52',
            '#4F9DA6',
            '#E0956E',
            '#73B3BA',
            '#B55B32'
        ],
        xaxis=dict(
            showgrid=True,
            gridcolor='#EAEAEA',
            gridwidth=1,
            zeroline=False,
            showline=True,
            linecolor='#D0DCDC'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#EAEAEA',
            gridwidth=1,
            zeroline=False,
            showline=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=30, t=50, b=40)
    )
    pio.templates["remittances_teal_copper"] = template
    pio.templates.default = "remittances_teal_copper"

apply_plotly_theme()
