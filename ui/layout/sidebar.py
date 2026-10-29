"""
sidebar.py
Dedicated component for the application sidebar.
Implements:
- Dark teal gradient background with dotted-map texture (via CSS)
- Copper coin-ring icon + 'Remittances Monitor' title
- Capsule navigation buttons; active = copper left bar
- Global filter section: FY range slider, Region multi-select chips, Presentation mode toggle
- Footer with data vintage and 'Data verified' badge
"""

import streamlit as st

ALL_REGIONS = ['Gulf (GCC)', 'Europe', 'North America', 'Asia-Pacific', 'Africa']

def render_sidebar():
    # 1. Logo block
    st.sidebar.markdown("""
    <div class="sidebar-logo-container">
        <div class="sidebar-seal-icon">🪙</div>
        <div>
            <div class="sidebar-title">Remittances<br>Monitor</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Capsule Navigation
    nav_options = {
        "📑 Executive Summary":         "executive_summary",
        "📈 The Long View":              "the_long_view",
        "🗺️ Where Money Comes From":    "where_money_comes_from",
        "🔍 Regional Deep Dive":         "regional_deep_dive",
        "📅 Monthly Patterns":           "monthly_patterns",
        "📋 Notes & Data":               "notes_data",
    }

    selected_label = st.sidebar.radio(
        label="Navigation Menu",
        options=list(nav_options.keys()),
        index=0,
        label_visibility="collapsed"
    )

    # 3. Global Filters Section
    st.sidebar.markdown('<div class="sidebar-filter-heading">▸ Global Filters</div>', unsafe_allow_html=True)

    # FY range slider
    fy_range = st.sidebar.slider(
        "Fiscal Year Range",
        min_value=1973,
        max_value=2026,
        value=st.session_state.get('fy_range', (2019, 2026)),
        step=1,
        key="global_fy_slider",
        help="Filters charts on all pages to this fiscal year window"
    )

    # Region multi-select
    selected_regions = st.sidebar.multiselect(
        "Regions",
        options=ALL_REGIONS,
        default=st.session_state.get('regions', ALL_REGIONS),
        key="global_region_select",
        help="Filter corridor charts to selected regions"
    )
    if not selected_regions:
        selected_regions = ALL_REGIONS  # default to all if nothing chosen

    # 4. Presentation Mode toggle
    st.sidebar.markdown('<div class="sidebar-filter-heading">▸ Display</div>', unsafe_allow_html=True)
    presentation_mode = st.sidebar.toggle(
        "📽 Presentation Mode",
        value=False,
        help="Larger text and simplified view for projection"
    )

    if presentation_mode:
        st.markdown("""
        <style>
          html, body, [data-testid="stAppViewContainer"] { font-size: 17px !important; }
          .mockup-kpi-val { font-size: 36px !important; }
          [data-testid="stSidebar"] { display: none !important; }
        </style>
        """, unsafe_allow_html=True)

    # 5. Footer
    st.sidebar.markdown("""
    <div class="sidebar-footer">
        <div style="font-size: 10.5px; color: rgba(255,255,255,0.6); margin-bottom: 6px;">
            Source: State Bank of Pakistan<br>Data through Sep 2026
        </div>
        <div style="display: inline-flex; align-items: center; gap: 6px;
                    background: rgba(194,112,61,0.25); color: #F0CDB2;
                    font-size: 11.5px; font-weight: 600; padding: 4px 10px;
                    border-radius: 16px; border: 1px solid rgba(194,112,61,0.4);">
            ✓ Data verified
        </div>
    </div>
    """, unsafe_allow_html=True)

    return {
        'view': nav_options[selected_label],
        'fy_range': fy_range,
        'regions': selected_regions,
        'presentation_mode': presentation_mode,
    }
