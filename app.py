"""
app.py
Clean Master Controller for Pakistan Workers' Remittances Analytics.
Architecture:
- ui/styles.css: Master CSS
- ui/layout/top_bar.py: Full + Slim banner variants
- ui/layout/sidebar.py: Dark teal sidebar with global filters
- ui/charts/: Reusable chart engines
- ui/components/: Reusable components
- views/: Clean modular page assemblies
"""

import streamlit as st
import os
import sys

# Configure Streamlit page
st.set_page_config(
    page_title="Pakistan Workers' Remittances Analytics",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Master CSS Stylesheet
CSS_FILE = os.path.join(os.path.dirname(__file__), 'ui', 'styles.css')
if os.path.exists(CSS_FILE):
    with open(CSS_FILE, 'r', encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Hide Plotly mode bar globally
st.markdown("""
<style>
  .js-plotly-plot .plotly .modebar-container { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Render Sidebar — returns dict with view, fy_range, regions, presentation_mode
from ui.layout.sidebar import render_sidebar
sidebar_state = render_sidebar()
selected_view = sidebar_state['view']

# Store sidebar state in session_state for views to access
st.session_state['fy_range'] = sidebar_state['fy_range']
st.session_state['regions'] = sidebar_state['regions']
st.session_state['presentation_mode'] = sidebar_state['presentation_mode']

# Dispatch to view modules
if selected_view == "executive_summary":
    from views.executive_summary import render_view
    render_view()
elif selected_view == "the_long_view":
    from views.the_long_view import render_view
    render_view()
elif selected_view == "where_money_comes_from":
    from views.where_money_comes_from import render_view
    render_view()
elif selected_view == "regional_deep_dive":
    from views.regional_deep_dive import render_view
    render_view()
elif selected_view == "monthly_patterns":
    from views.monthly_patterns import render_view
    render_view()
elif selected_view == "notes_data":
    from views.notes_data import render_view
    render_view()
