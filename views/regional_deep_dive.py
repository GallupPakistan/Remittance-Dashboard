"""
views/regional_deep_dive.py
Page 4 — Regional Deep Dive ("What about each region?")

Elements per MD spec §5.5:
1. World bubble map — dotted teal base, copper bubbles sized by FY26 total
2. Small multiples — sparkline per region, same scale
3. Gulf drill-down — Saudi + UAE + Other GCC stacked columns, then UAE sub-breakdown
4. Europe drill-down — UK + all EU members + Norway + Switzerland horizontal bars
5. Waterfall — which countries drove FY26 change vs FY25
6. Sankey — Region → Country → Pakistan
7. Rolling 12M line for user-selected country with methodology break marker
8. Ranked bar slider — top 10 countries for any FY
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from core.metrics import get_corridor_rankings, load_clean_data, CORRIDOR_ENTITIES, get_uae_detail
from ui.theme import COLORS
from ui.layout.top_bar import render_top_bar

# Fixed region colours as per MD §6.1
REGION_COLORS = {
    'Gulf (GCC)':     '#0F5F6B',
    'Europe':         '#C2703D',
    'North America':  '#1B8A97',
    'Asia-Pacific':   '#D98E5A',
    'Africa':         '#4F6D8F',
    'Other':          '#9AA7AB',
}

COUNTRY_COORDS = {
    'Saudi Arabia': (23.8859, 45.0792),
    'U.A.E.': (23.4241, 53.8478),
    'U.K.': (55.3781, -3.4360),
    'USA': (37.0902, -95.7129),
    'Oman': (21.4735, 55.9754),
    'Kuwait': (29.3117, 47.4818),
    'Qatar': (25.3548, 51.1839),
    'Bahrain': (26.0667, 50.5577),
    'Germany': (51.1657, 10.4515),
    'Italy': (41.8719, 12.5674),
    'Spain': (40.4637, -3.7492),
    'France': (46.2276, 2.2137),
    'Netherlands': (52.1326, 5.2913),
    'Canada': (56.1304, -106.3468),
    'Australia': (-25.2744, 133.7751),
    'Malaysia': (4.2105, 101.9758),
    'Japan': (36.2048, 138.2529),
    'South Africa': (-30.5595, 22.9375),
    'South Korea': (35.9078, 127.7669),
    'Switzerland': (46.8182, 8.2275),
    'Norway': (60.4720, 8.4689),
    'Belgium': (50.5039, 4.4699),
    'Sweden': (60.1282, 18.6435),
    'Greece': (39.0742, 21.8243),
    'Denmark': (56.2639, 9.5018),
    'Ireland': (53.1424, -7.6921),
}

GULF_ENTITIES    = ['saudi_arabia', 'uae', 'bahrain', 'kuwait', 'qatar', 'oman']
EUROPE_ENTITIES  = ['uk', 'germany', 'france', 'netherlands', 'spain', 'italy',
                    'greece', 'sweden', 'denmark', 'ireland', 'belgium',
                    'norway', 'switzerland']
UAE_SUB_ENTITIES = ['uae_dubai', 'uae_abudhabi', 'uae_sharjah', 'uae_others']


def _card(headline, subtitle=""):
    parts = [f'<div class="chart-headline">{headline}</div>']
    if subtitle:
        parts.append(f'<div class="chart-subtitle">{subtitle}</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_view():
    render_top_bar(slim=True,
                   title="Regional Deep Dive",
                   subtitle="Country-by-Country Performance Across Global Regions",
                   chip_text="Regional Explorer")

    df_m, df_fy, df_ent = load_clean_data()
    global_fy_range = st.session_state.get('fy_range', (2019, 2026))
    g_start, g_end = global_fy_range
    selected_regions = st.session_state.get('regions', ['Gulf (GCC)', 'Europe', 'North America', 'Asia-Pacific', 'Africa'])

    # Determine focal fiscal year from range end
    focal_fy = g_end
    prev_focal_fy = max(1973, focal_fy - 1)

    corridors_curr = get_corridor_rankings(fiscal_year=focal_fy)
    corridors_prev = get_corridor_rankings(fiscal_year=prev_focal_fy).set_index('entity_id')['value_musd']

    st.markdown("<h2 class='page-heading'>Regional Deep Dive</h2>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # 1. World Bubble Map
    # ─────────────────────────────────────────────
    _card(f"Where in the world does Pakistan's money come from (FY{focal_fy})?",
          f"Bubble size = FY{focal_fy} inflows. Teal = grew vs FY{prev_focal_fy}, Copper = declined.")

    map_rows = []
    for _, r in corridors_curr.iterrows():
        c_name = r['display_name']
        if c_name in COUNTRY_COORDS and r['region_group'] in selected_regions:
            lat, lon = COUNTRY_COORDS[c_name]
            v_prev = corridors_prev.get(r['entity_id'], r['value_musd'])
            growth = ((r['value_musd'] - v_prev) / v_prev * 100.0) if v_prev > 0 else 0.0
            direction = "Growth" if growth >= 0 else "Decline"
            map_rows.append({'Country': c_name, 'lat': lat, 'lon': lon,
                             'Inflows_MUSD': r['value_musd'],
                             'Inflows_BN': r['value_musd'] / 1000.0,
                             'Growth_pct': growth, 'Direction': direction})
    df_map = pd.DataFrame(map_rows)

    fig_map = px.scatter_geo(
        df_map, lat='lat', lon='lon', hover_name='Country',
        size='Inflows_MUSD', color='Direction',
        color_discrete_map={"Growth": COLORS['primary_teal'], "Decline": COLORS['secondary_copper']},
        projection='natural earth', size_max=40,
        hover_data={'lat': False, 'lon': False,
                    'Inflows_BN': ':.2f', 'Growth_pct': ':+.1f%'}
    )
    fig_map.update_geos(
        showcoastlines=True, coastlinecolor="#C8D8DA",
        showland=True, landcolor="#F2F8F8",
        showocean=True, oceancolor="#E6F2F3",
        showcountries=True, countrycolor="#D5E3E4"
    )
    fig_map.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=10),
                          legend=dict(orientation="h", y=-0.05))
    st.plotly_chart(fig_map, width='stretch')

    st.markdown("---")

    # ─────────────────────────────────────────────
    # 2. Small Multiples — one sparkline per country in selected region
    # ─────────────────────────────────────────────
    _card("How has each country performed over the past 8 years?",
          "Each panel uses the same Y-axis scale for fair comparison.")

    regions_list = ['Gulf (GCC)', 'Europe', 'North America', 'Asia-Pacific', 'Africa']
    sel_region = st.selectbox("Select Geographic Region:", regions_list, index=0,
                               key="reg_sm_region")

    reg_entities = df_ent[df_ent['region_group'] == sel_region]['entity_id'].tolist()
    sub_fy = df_fy[(df_fy['fiscal_year'] >= 2019) & (df_fy['entity_id'].isin(reg_entities))].copy()
    sub_fy = sub_fy.merge(df_ent[['entity_id', 'display_name']], on='entity_id', how='left')

    fig_multi = px.line(
        sub_fy, x='fiscal_year', y='value_musd', facet_col='display_name',
        facet_col_wrap=4,
        color_discrete_sequence=[REGION_COLORS.get(sel_region, COLORS['primary_teal'])]
    )
    fig_multi.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig_multi.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=20),
                             yaxis_title="US$ M")
    st.plotly_chart(fig_multi, width='stretch')

    st.markdown("---")

    # ─────────────────────────────────────────────
    # 3. Gulf Drill-Down
    # ─────────────────────────────────────────────
    _card("The Gulf: Pakistan's financial heartland",
          "Left: Saudi Arabia, UAE, and Other GCC stacked FY19–FY26. Right: UAE broken into its four emirates (from Jul 2018).")

    gulf_col, uae_col = st.columns([1.4, 1.2])

    with gulf_col:
        st.markdown('<div class="chart-subtitle">Gulf GCC — Annual inflows by major source (FY19–FY26)</div>',
                    unsafe_allow_html=True)

        gulf_entities_disp = {
            'saudi_arabia': 'Saudi Arabia',
            'uae':          'U.A.E.',
            'bahrain':      'Bahrain',
            'kuwait':       'Kuwait',
            'qatar':        'Qatar',
            'oman':         'Oman',
        }
        gulf_fy = df_fy[(df_fy['fiscal_year'] >= 2019) &
                        (df_fy['entity_id'].isin(gulf_entities_disp.keys()))].copy()
        gulf_fy = gulf_fy.merge(df_ent[['entity_id', 'display_name']], on='entity_id', how='left')

        gulf_colors = {
            'Saudi Arabia': '#0F5F6B',
            'U.A.E.':       '#1B8A97',
            'Bahrain':      '#7CC4CC',
            'Kuwait':       '#C2703D',
            'Qatar':        '#D98E5A',
            'Oman':         '#F0CDB2',
        }

        fig_gulf = go.Figure()
        for name, col_hex in gulf_colors.items():
            sub = gulf_fy[gulf_fy['display_name'] == name]
            if sub.empty:
                continue
            fig_gulf.add_trace(go.Bar(
                x=sub['fiscal_year'].apply(lambda y: f"FY{str(y)[-2:]}"),
                y=sub['value_musd'] / 1000.0,
                name=name,
                marker_color=col_hex,
                hovertemplate=f"<b>{name}</b> · %{{x}}<br>US$ %{{y:.2f}}B<extra></extra>"
            ))
        fig_gulf.update_layout(
            barmode='stack', height=370,
            margin=dict(l=10, r=10, t=10, b=30),
            yaxis=dict(title="US$ Billion", showgrid=True, gridcolor='#F0F0F0'),
            legend=dict(orientation="h", y=-0.22, xanchor="center", x=0.5, font=dict(size=10))
        )
        st.plotly_chart(fig_gulf, width='stretch')

    with uae_col:
        st.markdown('<div class="chart-subtitle">UAE Emirates — FY26 breakdown (Dubai, Abu Dhabi, Sharjah, Others)</div>',
                    unsafe_allow_html=True)

        uae_detail = get_uae_detail(fiscal_year=2026)

        if uae_detail.empty:
            st.info("UAE sub-emirate data available from July 2018 onwards only. "
                    "Ensure the parquet files include these entity IDs.")
        else:
            uae_colors_map = {
                'Dubai':     '#C2703D',
                'Abu Dhabi': '#0F5F6B',
                'Sharjah':   '#1B8A97',
                'Others':    '#D98E5A',
            }
            fig_uae = go.Figure(go.Pie(
                labels=uae_detail['display_name'],
                values=uae_detail['value_musd'],
                hole=0.52,
                marker_colors=[uae_colors_map.get(n, '#9AA7AB') for n in uae_detail['display_name']],
                textinfo='label+percent',
                hovertemplate="<b>%{label}</b><br>US$ %{value:,.1f}M · %{percent}<extra></extra>"
            ))
            fig_uae.update_layout(
                height=370, margin=dict(l=10, r=10, t=10, b=10),
                showlegend=False
            )
            # Centre annotation
            total_uae = uae_detail['value_musd'].sum() / 1000.0
            fig_uae.add_annotation(
                text=f"<b>US$ {total_uae:.1f}B</b><br><span style='font-size:10px'>UAE Total FY26</span>",
                x=0.5, y=0.5, showarrow=False, font=dict(size=13, color='#0F5F6B'),
                xanchor='center', yanchor='middle'
            )
            st.plotly_chart(fig_uae, width='stretch')

    st.markdown("---")

    # ─────────────────────────────────────────────
    # 4. Europe Drill-Down
    # ─────────────────────────────────────────────
    _card("Europe: UK leads, followed by the EU bloc",
          "FY26 inflows — UK, all EU member states, Norway, and Switzerland. Teal = grew vs FY25, Copper = declined.")

    europe_fy26 = df_fy[(df_fy['fiscal_year'] == 2026) &
                        (df_fy['entity_id'].isin(EUROPE_ENTITIES))].copy()
    europe_fy25 = df_fy[(df_fy['fiscal_year'] == 2025) &
                        (df_fy['entity_id'].isin(EUROPE_ENTITIES))].set_index('entity_id')['value_musd']
    europe_fy26 = europe_fy26.merge(df_ent[['entity_id', 'display_name']], on='entity_id', how='left')
    europe_fy26['growth'] = europe_fy26.apply(
        lambda r: (r['value_musd'] - europe_fy25.get(r['entity_id'], r['value_musd'])) /
                  europe_fy25.get(r['entity_id'], r['value_musd']) * 100
                  if europe_fy25.get(r['entity_id'], 0) > 0 else 0, axis=1)
    europe_fy26 = europe_fy26.sort_values('value_musd', ascending=True)
    europe_fy26['color'] = europe_fy26['growth'].apply(
        lambda g: COLORS['primary_teal'] if g >= 0 else COLORS['secondary_copper'])

    fig_europe = go.Figure(go.Bar(
        x=europe_fy26['value_musd'] / 1000.0,
        y=europe_fy26['display_name'],
        orientation='h',
        marker_color=europe_fy26['color'],
        text=europe_fy26.apply(
            lambda r: f"US$ {r['value_musd']/1000:.2f}B  ({r['growth']:+.1f}%)", axis=1),
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>US$ %{x:.3f}B<extra></extra>"
    ))
    fig_europe.update_layout(
        height=460, margin=dict(l=10, r=120, t=10, b=30),
        xaxis=dict(title="US$ Billion", showgrid=True, gridcolor='#F0F0F0'),
        yaxis=dict(title="")
    )
    st.plotly_chart(fig_europe, width='stretch')

    st.markdown('<div class="basis-break-note">⚠ Reporting basis changed July 2019 — EU countries show higher values post-2019 as remitter origin is now recorded.</div>',
                unsafe_allow_html=True)

    st.markdown("---")

    # ─────────────────────────────────────────────
    # 5. Country Contribution Waterfall FY25 → FY26
    # ─────────────────────────────────────────────
    _card("What drove the change from FY25 to FY26?",
          "Net change in annual inflows by corridor. Teal bars = grew vs FY25, Copper bars = declined.")

    diff_series = []
    for _, r in corridors_fy26.iterrows():
        v25 = corridors_fy25.get(r['entity_id'], r['value_musd'])
        diff_series.append({'Country': r['display_name'], 'diff_musd': r['value_musd'] - v25})
    df_wf_countries = pd.DataFrame(diff_series).sort_values('diff_musd', ascending=False)

    top_pos = df_wf_countries.head(5)
    top_neg = df_wf_countries.tail(3)
    mid_diff = df_wf_countries.iloc[5:-3]['diff_musd'].sum()

    wf_x = top_pos['Country'].tolist() + ["Other Sources"] + top_neg['Country'].tolist() + ["Net Change"]
    wf_y = (top_pos['diff_musd'] / 1000.0).tolist() + [mid_diff / 1000.0] + (top_neg['diff_musd'] / 1000.0).tolist() + [0]
    wf_m = ["relative"] * (len(wf_x) - 1) + ["total"]

    fig_wf = go.Figure(go.Waterfall(
        x=wf_x, y=wf_y, measure=wf_m,
        decreasing=dict(marker=dict(color=COLORS['secondary_copper'])),
        increasing=dict(marker=dict(color=COLORS['primary_teal'])),
        totals=dict(marker=dict(color='#08373E')),
        connector=dict(line=dict(color="#C8D8DA", width=1)),
        text=[f"{v:+.2f}B" for v in wf_y[:-1]] + [f"{((corridors_fy26['value_musd'].sum() - corridors_fy25.sum())/1000.0):+.2f}B"],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Impact: US$ %{y:+.2f}B<extra></extra>"
    ))
    fig_wf.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=30, b=30),
        yaxis=dict(title="Contribution to Growth (US$ Billion)", showgrid=True, gridcolor='#F0F0F0')
    )
    st.plotly_chart(fig_wf, use_container_width=True)

    st.markdown("---")

    # ─────────────────────────────────────────────
    # 6 & 7. Rolling 12M by country + Ranked bar slider
    # ─────────────────────────────────────────────
    col_a, col_b = st.columns([1.3, 1.3])

    with col_a:
        _card("Rolling 12-month trend for a single corridor",
              "Methodology break shown at July 2019.")
        all_country_names = corridors_fy26['display_name'].tolist()
        sel_country = st.selectbox("Select Country:", all_country_names, index=0,
                                    key="reg_country_roll")
        c_ent = df_ent[df_ent['display_name'] == sel_country]['entity_id'].iloc[0]
        c_monthly = df_m[df_m['entity_id'] == c_ent].sort_values('month_start').copy()
        c_monthly['rolling_12m'] = c_monthly['value_musd'].rolling(12).sum()
        c_recent = c_monthly[c_monthly['month_start'] >= '2016-01-01'].dropna()

        fig_c_roll = go.Figure()
        fig_c_roll.add_trace(go.Scatter(
            x=c_recent['month_start'], y=c_recent['rolling_12m'],
            mode='lines', line=dict(color=COLORS['primary_teal'], width=2.5),
            fill='tozeroy', fillcolor='rgba(15,95,107,0.1)',
            name=sel_country,
            hovertemplate="%{x|%b %Y}: US$ %{y:,.0f}M<extra></extra>"
        ))
        # Methodology break marker
        fig_c_roll.add_vline(x="2019-07-01", line_width=1.5,
                              line_dash="dash", line_color=COLORS['secondary_copper'])
        if not c_recent.empty:
            fig_c_roll.add_annotation(
                x="2019-07-01", y=c_recent['rolling_12m'].max() * 0.88,
                text="Jul 2019 Reporting Shift", showarrow=False,
                font=dict(size=9, color=COLORS['secondary_copper']),
                bgcolor="#FFF2EC", bordercolor=COLORS['secondary_copper']
            )
        fig_c_roll.update_layout(height=320, margin=dict(l=10, r=20, t=10, b=20),
                                  yaxis_title="12M Sum (US$ M)")
        st.plotly_chart(fig_c_roll, width='stretch')

    with col_b:
        _card("Top 10 corridors ranked — any fiscal year",
              "Use the slider to explore historical rankings.")
        slider_fy = st.slider("Select Fiscal Year:", min_value=1980, max_value=2026,
                               value=2026, step=1, key="reg_rank_slider")
        rank_df = get_corridor_rankings(fiscal_year=slider_fy).head(10).sort_values('value_bn', ascending=True)

        fig_rank = go.Figure(go.Bar(
            x=rank_df['value_bn'], y=rank_df['display_name'],
            orientation='h',
            marker_color=COLORS['primary_teal'],
            text=rank_df['value_bn'].apply(lambda x: f"${x:.2f}B"),
            textposition='outside',
            hovertemplate="<b>%{y}</b><br>US$ %{x:.3f}B<extra></extra>"
        ))
        fig_rank.update_layout(height=320, margin=dict(l=10, r=60, t=10, b=20),
                                xaxis_title="US$ Billion", yaxis_title="")
        st.plotly_chart(fig_rank, width='stretch')
