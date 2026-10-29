"""
views/where_money_comes_from.py
Page 3 — Where the Money Comes From
Which countries send the most and how that has shifted

Required Elements:
1. Treemap — FY26 share by country, user can switch fiscal year
2. Slope chart — FY19 share vs FY26 share, copper = fell, teal = rose
3. Bump chart — rank race of top 8 sources, FY19 to FY26
4. 100% stacked area — regional mix over time (UAE, Other GCC, EU, UK, USA, Others)
5. Concentration big number + mini bar — “Top 3 sources send X% of total”
6. Sankey diagram — FY26 flow from region → country → Pakistan total
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from core.metrics import get_corridor_rankings, load_clean_data, CORRIDOR_ENTITIES
from ui.theme import COLORS
from ui.layout.top_bar import render_top_bar

def render_view():
    render_top_bar(slim=True, title="Where the Money Comes From", subtitle="Which Countries Send the Most & Historical Mix Shifts", chip_text="Corridor Analytics")

    df_m, df_fy, df_ent = load_clean_data()
    global_fy_range = st.session_state.get('fy_range', (2019, 2026))
    g_start, g_end = global_fy_range
    selected_regions = st.session_state.get('regions', ['Gulf (GCC)', 'Europe', 'North America', 'Asia-Pacific', 'Africa'])

    available_years = [int(y) for y in sorted(df_fy['fiscal_year'].unique(), reverse=True) if y <= 2026 and y >= g_start and y <= g_end]
    if not available_years:
        available_years = list(range(2026, 1972, -1))

    # Fiscal Year selector for interactive Treemap
    col_sel, col_stat = st.columns([1.2, 2.8])
    with col_sel:
        selected_fy = st.selectbox("Select Fiscal Year for Treemap:", available_years, index=0)

    df_corridors = get_corridor_rankings(fiscal_year=selected_fy)
    df_corridors = df_corridors[df_corridors['region_group'].isin(selected_regions)].copy()
    if df_corridors.empty:
        df_corridors = get_corridor_rankings(fiscal_year=selected_fy)
    
    # ── 5. Concentration Big Number + Mini Bar ──
    top3 = df_corridors.head(3)
    top3_share = top3['share_pct'].sum()
    with col_stat:
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E1E8E9; border-left:4px solid {COLORS['secondary_copper']}; border-radius:8px; padding:10px 16px; margin-top:14px;">
            <div style="font-size:11.5px; color:#5A6B70; text-transform:uppercase; font-weight:700;">Concentration Ratio (FY{selected_fy}):</div>
            <div style="font-size:22px; font-weight:700; color:{COLORS['primary_teal']}; margin:2px 0;">Top 3 sources send {top3_share:.1f}% of total</div>
            <div style="font-size:12px; color:#5A6B70; margin-bottom:6px;">Leading sources: {', '.join(top3['display_name'].tolist())}</div>
            <div style="width:100%; height:8px; background:#EBF4F5; border-radius:4px; overflow:hidden;">
                <div style="width:{top3_share}%; height:100%; background:{COLORS['secondary_copper']}; border-radius:4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── 1. Treemap (FY26 / Selected FY share by country) ──
    st.markdown(
        f'<div class="chart-headline">1. Treemap — Country Shares (FY{selected_fy})</div>'
        f'<div class="chart-subtitle">Instant sense of proportion across all itemised sovereign corridors. Copper = top sender.</div>',
        unsafe_allow_html=True
    )
    df_tree = df_corridors.copy()
    leader_name = df_tree.iloc[0]['display_name']
    df_tree['highlight_color'] = [COLORS['secondary_copper'] if n == leader_name else COLORS['primary_teal'] for n in df_tree['display_name']]
    fig_tree = px.treemap(
        df_tree,
        names='display_name',
        parents=['All Remittances'] * len(df_tree),
        values='value_musd',
        color='highlight_color',
        color_discrete_map={COLORS['secondary_copper']: COLORS['secondary_copper'], COLORS['primary_teal']: COLORS['primary_teal']}
    )
    fig_tree.update_traces(
        textinfo='label+percent parent',
        textfont=dict(size=12, color='#FFFFFF'),
        marker=dict(pad=dict(t=18, l=6, r=6, b=6)),
        hovertemplate="<b>%{label}</b><br>Inflows: US$ %{value:,.1f}M<br>Share: %{percentParent:.1%}<extra></extra>"
    )
    fig_tree.update_layout(
        height=420,
        margin=dict(l=5, r=5, t=15, b=15)
    )
    st.plotly_chart(fig_tree, use_container_width=True)

    # ── 2. Slope Chart: FY19 Share vs FY26 Share ──
    st.markdown(
        '<div class="chart-headline">2. Slope Chart — Share Shift (FY19 vs FY26)</div>'
        '<div class="chart-subtitle">Tracking structural share gains/losses across the July 2019 reporting shift. Teal = Share Rose, Copper = Share Fell. Top corridors shown with clear spacing.</div>',
        unsafe_allow_html=True
    )
    
    c_fy19 = get_corridor_rankings(fiscal_year=2019).set_index('display_name')['share_pct']
    c_fy26 = get_corridor_rankings(fiscal_year=2026).set_index('display_name')['share_pct']
    common_countries = list(set(c_fy19.index).intersection(set(c_fy26.index)))
    
    slope_data = []
    # Pick significant corridors (> 1.8% in either year) to eliminate overlapping text
    for c in common_countries:
        s19, s26 = c_fy19[c], c_fy26[c]
        if s19 >= 1.8 or s26 >= 1.8:
            slope_data.append({'country': c, 'fy19': s19, 'fy26': s26, 'rose': s26 >= s19})
    df_slope = pd.DataFrame(slope_data).sort_values('fy26', ascending=False)
    
    fig_slope = go.Figure()
    for _, r in df_slope.iterrows():
        line_color = COLORS['primary_teal'] if r['rose'] else COLORS['secondary_copper']
        fig_slope.add_trace(go.Scatter(
            x=['FY19', 'FY26'],
            y=[r['fy19'], r['fy26']],
            mode='lines+markers+text',
            name=r['country'],
            line=dict(color=line_color, width=2.5),
            marker=dict(size=8),
            text=[f"{r['country']}&nbsp;&nbsp;<b>{r['fy19']:.1f}%</b>", f"<b>{r['fy26']:.1f}%</b>&nbsp;&nbsp;{r['country']}"],
            textposition=['middle left', 'middle right'],
            textfont=dict(size=11),
            hovertemplate=f"<b>{r['country']}</b><br>FY19: {r['fy19']:.1f}%<br>FY26: {r['fy26']:.1f}%<extra></extra>",
            showlegend=False
        ))
    fig_slope.update_layout(
        height=440,
        margin=dict(l=140, r=140, t=25, b=25),
        xaxis=dict(title="", showgrid=False, tickfont=dict(size=13, color='#12262B')),
        yaxis=dict(title="Share of Total Remittances (%)", showgrid=True, gridcolor='#F0F0F0', ticksuffix='%')
    )
    st.plotly_chart(fig_slope, use_container_width=True)

    # ── 3. Bump Chart: Rank Race of Top 8 Sources (FY19 to FY26) ──
    st.markdown(
        '<div class="chart-headline">3. Bump Chart — Rank Race of Top 8 Sources (FY19 to FY26)</div>'
        '<div class="chart-subtitle">Who overtook whom across fiscal years. Inverted rank axis (#1 on top).</div>',
        unsafe_allow_html=True
    )
    recent_fy_corridors = df_fy[(df_fy['fiscal_year'] >= 2019) & (df_fy['entity_id'].isin(CORRIDOR_ENTITIES))].copy()
    recent_fy_corridors = recent_fy_corridors.merge(df_ent[['entity_id', 'display_name']], on='entity_id', how='left')
    recent_fy_corridors['rank'] = recent_fy_corridors.groupby('fiscal_year')['value_musd'].rank(ascending=False, method='min')
    
    top8_fy26 = df_corridors.head(8)['display_name'].tolist()
    bump_df = recent_fy_corridors[recent_fy_corridors['display_name'].isin(top8_fy26)].copy()
    
    fig_bump = go.Figure()
    palette = ['#C2703D', '#0F5F6B', '#1B8A97', '#D98E5A', '#2E8B90', '#6C5B7B', '#4F6D8F', '#9A5527']
    for i, name in enumerate(top8_fy26):
        sub = bump_df[bump_df['display_name'] == name].sort_values('fiscal_year')
        fig_bump.add_trace(go.Scatter(
            x=[f"FY{str(y)[-2:]}" for y in sub['fiscal_year']],
            y=sub['rank'],
            mode='lines+markers',
            name=name,
            line=dict(color=palette[i % len(palette)], width=2.5),
            marker=dict(size=7),
            hovertemplate=f"<b>{name}</b><br>%{{x}}: Rank #%{{y:.0f}}<extra></extra>"
        ))
    fig_bump.update_layout(
        height=380,
        margin=dict(l=30, r=30, t=10, b=40),
        yaxis=dict(title="Rank (1 is Top)", autorange="reversed", tickmode='linear', tick0=1, dtick=1, gridcolor='#F0F0F0'),
        xaxis=dict(title="", showgrid=False),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, font=dict(size=11))
    )
    st.plotly_chart(fig_bump, use_container_width=True)

    # ── 4. 100% Stacked Area: Regional Mix Over Time ──
    st.markdown(
        '<div class="chart-headline">4. 100% Stacked Area — Regional Mix Over Time</div>'
        '<div class="chart-subtitle">Long-term structural evolution of regional share since 2000.</div>',
        unsafe_allow_html=True
    )
    reg_mix = df_fy[(df_fy['fiscal_year'] >= 2000) & (df_fy['entity_id'].isin(CORRIDOR_ENTITIES + ['other_countries']))].copy()
    reg_mix = reg_mix.merge(df_ent[['entity_id', 'region_group']], on='entity_id', how='left')
    reg_totals = reg_mix.groupby(['fiscal_year', 'region_group'])['value_musd'].sum().reset_index()
    
    fig_stack = px.area(
        reg_totals,
        x='fiscal_year',
        y='value_musd',
        color='region_group',
        groupnorm='percent',
        color_discrete_map={
            'Gulf (GCC)': '#0F5F6B',
            'Europe': '#C2703D',
            'North America': '#1B8A97',
            'Asia-Pacific': '#D98E5A',
            'Africa': '#4F6D8F',
            'Other (not itemised)': '#9AA7AB'
        }
    )
    fig_stack.update_layout(
        height=380,
        margin=dict(l=30, r=30, t=10, b=40),
        yaxis=dict(title="Share of Inflows (%)", ticksuffix='%', gridcolor='#F0F0F0'),
        xaxis=dict(title="Fiscal Year"),
        legend=dict(title="", orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, font=dict(size=11))
    )
    st.plotly_chart(fig_stack, use_container_width=True)

    # ── 6. Sankey Diagram: FY26 Flow from Region → Country → Pakistan ──
    st.markdown(
        '<div class="chart-headline">5. Sankey Diagram — FY26 Inflow Routing (Region → Country → Pakistan)</div>'
        '<div class="chart-subtitle">Visual representation of funds flowing from source regions through key sovereign corridors into Pakistan.</div>',
        unsafe_allow_html=True
    )
    fy26_c = df_fy[(df_fy['fiscal_year'] == 2026) & (df_fy['entity_id'].isin(CORRIDOR_ENTITIES))].copy()
    fy26_c = fy26_c.merge(df_ent[['entity_id', 'display_name', 'region_group']], on='entity_id', how='left').sort_values('value_musd', ascending=False).head(10)
    
    regions = fy26_c['region_group'].unique().tolist()
    countries = fy26_c['display_name'].unique().tolist()
    all_nodes = regions + countries + ["Pakistan Total 🇵🇰"]
    node_idx = {name: i for i, name in enumerate(all_nodes)}
    
    sources, targets, values = [], [], []
    for _, r in fy26_c.iterrows():
        # Region -> Country
        sources.append(node_idx[r['region_group']])
        targets.append(node_idx[r['display_name']])
        values.append(r['value_musd'])
        # Country -> Pakistan
        sources.append(node_idx[r['display_name']])
        targets.append(node_idx["Pakistan Total 🇵🇰"])
        values.append(r['value_musd'])
        
    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=18,
            thickness=20,
            label=all_nodes,
            color=[COLORS['primary_teal'] if n == "Pakistan Total 🇵🇰" else '#1B8A97' if n in regions else COLORS['secondary_copper'] for n in all_nodes],
            line=dict(color="#08373E", width=0.5)
        ),
        link=dict(source=sources, target=targets, value=values, color="rgba(194, 112, 61, 0.22)")
    )])
    fig_sankey.update_layout(
        height=420,
        margin=dict(l=15, r=15, t=15, b=15),
        font=dict(size=12, family="Inter, sans-serif")
    )
    st.plotly_chart(fig_sankey, use_container_width=True)
