"""
insights.py
Generates natural-English, non-technical headline answers from the raw data.
Fulfills Design Principle 5.1: "Headline first: A viewer can read the sentence and skip the chart."
"""

from core.formatting import fmt_usd_bn, fmt_growth, fmt_share

def get_executive_headline(kpis):
    """
    Returns concise executive summary sentence.
    """
    dir_word = "up" if kpis['fy_growth_pct'] >= 0 else "down"
    return (
        f"In FY2026, overseas Pakistanis sent home **{fmt_usd_bn(kpis['fy26_val_bn'])}**, "
        f"{dir_word} **{abs(kpis['fy_growth_pct']):.1f}%** compared with FY2025, "
        f"led by **{kpis['top_corridor_name']}** which contributed **{fmt_share(kpis['top_corridor_share'])}** of all inflows."
    )

def get_corridor_headline(corridors_df):
    """
    Returns plain English summary for corridor breakdown.
    """
    top3 = corridors_df.head(3)
    top1 = top3.iloc[0]
    top2 = top3.iloc[1]
    top3_c = top3.iloc[2]
    combined_share = top3['share_pct'].sum()
    
    return (
        f"The top three corridors — **{top1['display_name']}** ({top1['share_pct']:.1f}%), "
        f"**{top2['display_name']}** ({top2['share_pct']:.1f}%), and **{top3_c['display_name']}** ({top3_c['share_pct']:.1f}%) — "
        f"account for **{combined_share:.1f}%** of total worker remittances."
    )

def get_regional_headline(regional_df):
    """
    Returns regional summary headline.
    """
    gulf = regional_df[regional_df['region_group'] == 'Gulf (GCC)']
    gulf_share = gulf['share_pct'].iloc[0] if not gulf.empty else 0.0
    return (
        f"The **Gulf (GCC) region** remains Pakistan's largest economic anchor, "
        f"accounting for **{gulf_share:.1f}%** of all formal remittances."
    )
