"""
top_bar.py — Pakistan Workers' Remittances Dashboard
Full-height and slim banner variants, rendered via st.html().
"""

import streamlit as st


# ── Full banner (Executive Summary) ──────────────────────────────────────
FULL_TOPBAR_HTML = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;500;600&display=swap">

<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  .banner {
    position: relative;
    width: 100%;
    height: 200px;
    background: linear-gradient(135deg, #08323A 0%, #0F5F6B 55%, #0B4A54 100%);
    overflow: hidden;
    font-family: 'Inter', system-ui, sans-serif;
    border-radius: 0 0 8px 8px;
    margin-bottom: 4px;
  }

  /* ── Copper pinstripe top band ── */
  .banner::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0;
    height: 14px;
    background: repeating-linear-gradient(
      -45deg,
      #C2703D, #C2703D 8px,
      #08323A 8px, #08323A 16px
    );
    z-index: 10;
    animation: shimmer 4s linear infinite;
  }
  @keyframes shimmer {
    0%   { background-position: 0 0; }
    100% { background-position: 32px 0; }
  }

  /* ── Grid lines ── */
  .banner-grid {
    position: absolute; inset: 0;
    background:
      repeating-linear-gradient(0deg, transparent, transparent 29px,
        rgba(194,112,61,0.12) 29px, rgba(194,112,61,0.12) 30px);
    pointer-events: none;
  }

  /* ── Text layer ── */
  .banner-text {
    position: relative; z-index: 5;
    padding: 30px 32px 0;
  }
  .banner-eyebrow {
    font-size: 10.5px; font-weight: 600;
    letter-spacing: 0.16em; color: #D98E5A;
    text-transform: uppercase; margin-bottom: 7px;
    display: flex; align-items: center; gap: 8px;
  }
  .banner-eyebrow::before {
    content: ''; display: inline-block;
    width: 16px; height: 2px;
    background: #D98E5A; border-radius: 1px;
  }
  .banner-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 32px; font-weight: 800; color: #FFFFFF;
    line-height: 1.1; letter-spacing: -0.01em;
    text-shadow: 0 2px 20px rgba(0,0,0,0.45);
  }
  .banner-subtitle {
    font-size: 12.5px; font-weight: 400;
    color: rgba(221,241,243,0.78);
    margin-top: 6px; letter-spacing: 0.01em;
  }

  /* ── Chips row ── */
  .banner-chips {
    position: relative; z-index: 5;
    padding: 10px 32px 0;
    display: flex; gap: 10px; flex-wrap: wrap;
  }
  .chip {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.22);
    color: #FFFFFF; font-size: 11px; font-weight: 600;
    letter-spacing: 0.04em; padding: 4px 12px;
    border-radius: 20px;
  }
  .chip-dot { width: 6px; height: 6px; border-radius: 50%; background: #D98E5A; }

  /* ── Pin pulse animation ── */
  @keyframes pinPulse {
    0%   { r: 6px; opacity: 0.7; }
    100% { r: 18px; opacity: 0; }
  }
  @keyframes dash-flow {
    to { stroke-dashoffset: -100; }
  }
  .pin-pulse { animation: pinPulse 2.4s ease-out infinite; transform-origin: center; transform-box: fill-box; }
  .pin-pulse-2 { animation-delay: 0.5s; animation-duration: 2.8s; }
  .pin-pulse-3 { animation-delay: 0.9s; animation-duration: 3.0s; }
  .pin-pulse-4 { animation-delay: 1.3s; animation-duration: 2.6s; }
  .arc-flow { animation: dash-flow 12s linear infinite; }

  @media (prefers-reduced-motion: reduce) {
    .pin-pulse, .arc-flow { animation: none; opacity: 0; }
  }
</style>

<div class="banner">
  <div class="banner-grid"></div>

  <!-- SVG: World map arcs, pins, globe, skyline -->
  <svg style="position:absolute;inset:0;width:100%;height:100%;"
       viewBox="0 0 1200 200" preserveAspectRatio="xMidYMid slice"
       xmlns="http://www.w3.org/2000/svg">
    <defs>
      <radialGradient id="pg" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#D98E5A" stop-opacity="0.65"/>
        <stop offset="100%" stop-color="#D98E5A" stop-opacity="0"/>
      </radialGradient>
      <linearGradient id="sg" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%"   stop-color="#9A5527" stop-opacity="0"/>
        <stop offset="35%"  stop-color="#C2703D" stop-opacity="0.4"/>
        <stop offset="65%"  stop-color="#D98E5A" stop-opacity="0.55"/>
        <stop offset="100%" stop-color="#9A5527" stop-opacity="0"/>
      </linearGradient>
    </defs>

    <!-- Grid lines SVG -->
    <line x1="0" y1="60"  x2="1200" y2="60"  stroke="url(#sg)" stroke-width="0.7"/>
    <line x1="0" y1="110" x2="1200" y2="110" stroke="url(#sg)" stroke-width="0.5"/>
    <line x1="0" y1="160" x2="1200" y2="160" stroke="url(#sg)" stroke-width="0.7"/>

    <!-- World-map grid (right half) -->
    <g stroke="rgba(124,196,204,0.09)" stroke-width="0.8" fill="none">
      <ellipse cx="880" cy="95" rx="230" ry="85"/>
      <ellipse cx="880" cy="95" rx="155" ry="85"/>
      <ellipse cx="880" cy="95" rx="78"  ry="85"/>
      <line x1="650" y1="95"  x2="1110" y2="95"/>
      <line x1="650" y1="48"  x2="1110" y2="48"/>
      <line x1="650" y1="142" x2="1110" y2="142"/>
    </g>

    <!-- Continent blobs -->
    <g fill="rgba(124,196,204,0.07)" stroke="rgba(124,196,204,0.13)" stroke-width="0.8">
      <ellipse cx="820" cy="80" rx="58" ry="28"/>
      <ellipse cx="940" cy="92" rx="42" ry="27"/>
      <ellipse cx="765" cy="58" rx="33" ry="18"/>
      <ellipse cx="710" cy="60" rx="17" ry="10"/>
    </g>

    <!-- Animated dashed arc routes → Pakistan -->
    <path d="M 820 80 Q 890 30 980 90"
          stroke="#C2703D" stroke-width="1.4" fill="none"
          stroke-dasharray="5 4" stroke-linecap="round" opacity="0.9"
          class="arc-flow"/>
    <path d="M 860 95 Q 915 50 980 90"
          stroke="#C2703D" stroke-width="1.4" fill="none"
          stroke-dasharray="5 4" stroke-linecap="round" opacity="0.9"
          class="arc-flow" style="animation-delay:-3s"/>
    <path d="M 712 62 Q 825 18 980 90"
          stroke="#C2703D" stroke-width="1.2" fill="none"
          stroke-dasharray="5 4" stroke-linecap="round" opacity="0.72"
          class="arc-flow" style="animation-delay:-6s"/>
    <path d="M 765 60 Q 855 22 980 90"
          stroke="#C2703D" stroke-width="1.1" fill="none"
          stroke-dasharray="4 5" stroke-linecap="round" opacity="0.66"
          class="arc-flow" style="animation-delay:-9s"/>
    <path d="M 636 75 Q 790 10 980 90"
          stroke="#C2703D" stroke-width="0.9" fill="none"
          stroke-dasharray="4 6" stroke-linecap="round" opacity="0.52"
          class="arc-flow" style="animation-delay:-1.5s"/>

    <!-- Pulse rings -->
    <circle cx="820" cy="80" r="6" fill="url(#pg)" class="pin-pulse"/>
    <circle cx="860" cy="95" r="6" fill="url(#pg)" class="pin-pulse pin-pulse-2"/>
    <circle cx="712" cy="62" r="5" fill="url(#pg)" class="pin-pulse pin-pulse-3"/>
    <circle cx="765" cy="60" r="5" fill="url(#pg)" class="pin-pulse pin-pulse-4"/>

    <!-- Country pins -->
    <g transform="translate(820,80)">
      <circle r="5" fill="#C2703D" stroke="#F0CDB2" stroke-width="1"/>
      <path d="M0 5 L-3 14 L0 12 L3 14Z" fill="#9A5527"/>
    </g>
    <g transform="translate(860,95)">
      <circle r="5" fill="#C2703D" stroke="#F0CDB2" stroke-width="1"/>
      <path d="M0 5 L-3 14 L0 12 L3 14Z" fill="#9A5527"/>
    </g>
    <g transform="translate(712,62)">
      <circle r="4.5" fill="#C2703D" stroke="#F0CDB2" stroke-width="1"/>
      <path d="M0 4.5 L-2.5 12 L0 10 L2.5 12Z" fill="#9A5527"/>
    </g>
    <g transform="translate(765,60)">
      <circle r="4" fill="#C2703D" stroke="#F0CDB2" stroke-width="1"/>
      <path d="M0 4 L-2 11 L0 9 L2 11Z" fill="#9A5527"/>
    </g>
    <!-- Pakistan destination dot -->
    <g transform="translate(980,90)">
      <circle r="7" fill="#1B8A97" stroke="#DDF1F3" stroke-width="1.5"/>
      <circle r="3" fill="#DDF1F3"/>
    </g>

    <!-- Globe icon top-right -->
    <g transform="translate(1158,42)">
      <circle r="28" fill="rgba(27,138,151,0.15)" stroke="rgba(194,112,61,0.5)" stroke-width="1.5"/>
      <circle r="18" fill="none" stroke="rgba(124,196,204,0.75)" stroke-width="1.5"/>
      <ellipse rx="9" ry="18" fill="none" stroke="rgba(124,196,204,0.5)" stroke-width="1"/>
      <line x1="-18" y1="0"  x2="18" y2="0"  stroke="rgba(124,196,204,0.5)" stroke-width="1"/>
      <line x1="-16" y1="-9" x2="16" y2="-9" stroke="rgba(124,196,204,0.3)" stroke-width="0.8"/>
      <line x1="-16" y1="9"  x2="16" y2="9"  stroke="rgba(124,196,204,0.3)" stroke-width="0.8"/>
    </g>

    <!-- Gulf skyline → Pakistani landmarks silhouette -->
    <g fill="rgba(7,44,52,0.90)">
      <rect x="0"   y="162" width="18" height="38"/>
      <rect x="10"  y="152" width="12" height="48"/>
      <rect x="22"  y="158" width="20" height="42"/>
      <rect x="28"  y="144" width="8"  height="56"/>
      <polygon points="38,100 42,100 50,144 36,144"/>
      <rect x="36" y="144" width="15" height="56"/>
      <rect x="35" y="140" width="17" height="5"/>
      <rect x="38" y="97"  width="5"  height="4"/>
      <line x1="40" y1="97" x2="40" y2="84" stroke="rgba(7,44,52,0.90)" stroke-width="2"/>
      <rect x="52"  y="154" width="22" height="46"/>
      <rect x="60"  y="148" width="10" height="52"/>
      <rect x="74"  y="163" width="18" height="37"/>
      <rect x="80"  y="156" width="14" height="44"/>
      <rect x="92"  y="150" width="12" height="50"/>
      <!-- Mosque dome -->
      <rect x="116" y="163" width="40" height="37"/>
      <ellipse cx="136" cy="163" rx="20" ry="13"/>
      <rect x="128" y="138" width="3" height="27"/>
      <rect x="143" y="138" width="3" height="27"/>
      <ellipse cx="129.5" cy="137" rx="4" ry="5"/>
      <ellipse cx="144.5" cy="137" rx="4" ry="5"/>
      <rect x="158" y="156" width="16" height="44"/>
      <rect x="174" y="150" width="10" height="50"/>
      <rect x="184" y="165" width="20" height="35"/>
      <polygon points="400,100 404,100 414,148 396,148"/>
      <rect x="395" y="148" width="20" height="52"/>
      <rect x="393" y="144" width="24" height="5"/>
      <rect x="397" y="96"  width="6"  height="5"/>
      <line x1="400" y1="96" x2="400" y2="83" stroke="rgba(7,44,52,0.90)" stroke-width="2"/>
      <rect x="416" y="158" width="20" height="42"/>
      <rect x="425" y="150" width="12" height="50"/>
      <rect x="437" y="163" width="18" height="37"/>
      <rect x="445" y="156" width="10" height="44"/>
      <rect x="455" y="168" width="15" height="32"/>
      <rect x="470" y="162" width="20" height="38"/>
      <rect x="480" y="154" width="14" height="46"/>
      <rect x="494" y="165" width="18" height="35"/>
      <rect x="510" y="160" width="22" height="40"/>
      <rect x="620" y="168" width="580" height="32"/>
    </g>
  </svg>

  <!-- Text overlay -->
  <div class="banner-text">
    <div class="banner-eyebrow">Economy &amp; External Sector Monitor</div>
    <div class="banner-title">Pakistan Workers&#8217; Remittances Analytics</div>
    <div class="banner-subtitle">Country-wise inflows, FY73 to Sep 2026, in US dollars</div>
  </div>

  <!-- Chips row -->
  <div class="banner-chips">
    <div class="chip"><span class="chip-dot"></span> Jul 1972 – Sep 2026</div>
    <div class="chip"><span class="chip-dot"></span> FY26: US$ 41.6B</div>
    <div class="chip"><span class="chip-dot"></span> Source: State Bank of Pakistan</div>
  </div>

</div>
"""


# ── Slim banner (Pages 2–5) ────────────────────────────────────────────
SLIM_TOPBAR_HTML_TEMPLATE = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;500;600&display=swap">

<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  .slim-banner {{
    position: relative; width: 100%; height: 120px;
    background: linear-gradient(135deg, #08323A 0%, #0F5F6B 55%, #0B4A54 100%);
    overflow: hidden; font-family: 'Inter', system-ui, sans-serif;
    border-radius: 0 0 8px 8px; margin-bottom: 4px;
  }}
  .slim-banner::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 10px;
    background: repeating-linear-gradient(-45deg,
      #C2703D, #C2703D 7px, #08323A 7px, #08323A 14px);
    z-index: 10; animation: shimmer 4s linear infinite;
  }}
  @keyframes shimmer {{ to {{ background-position: 28px 0; }} }}
  .slim-grid {{
    position: absolute; inset: 0;
    background: repeating-linear-gradient(0deg,transparent,transparent 24px,
      rgba(194,112,61,0.10) 24px,rgba(194,112,61,0.10) 25px);
    pointer-events: none;
  }}
  .slim-text {{ position: relative; z-index: 5; padding: 22px 32px 0; }}
  .slim-eyebrow {{
    font-size: 9.5px; font-weight: 600; letter-spacing: 0.16em;
    color: #D98E5A; text-transform: uppercase; margin-bottom: 5px;
    display: flex; align-items: center; gap: 7px;
  }}
  .slim-eyebrow::before {{
    content: ''; display: inline-block;
    width: 14px; height: 2px; background: #D98E5A; border-radius: 1px;
  }}
  .slim-title {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 22px; font-weight: 800; color: #FFFFFF;
    line-height: 1.1; text-shadow: 0 2px 16px rgba(0,0,0,0.4);
  }}
  .slim-subtitle {{
    font-size: 11.5px; color: rgba(221,241,243,0.72); margin-top: 4px;
  }}
  .slim-chips {{
    position: relative; z-index: 5;
    padding: 8px 32px 0; display: flex; gap: 8px;
  }}
  .slim-chip {{
    display: inline-flex; align-items: center; gap: 4px;
    background: rgba(255,255,255,0.12); backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.20); color: #FFFFFF;
    font-size: 10px; font-weight: 600; padding: 3px 10px; border-radius: 16px;
  }}
  .slim-chip-dot {{ width: 5px; height: 5px; border-radius: 50%; background: #D98E5A; }}
  .slim-skyline {{ position: absolute; bottom: 0; right: 0; opacity: 0.18; }}
</style>

<div class="slim-banner">
  <div class="slim-grid"></div>
  <svg class="slim-skyline" width="400" height="120" viewBox="0 0 400 120">
    <g fill="#DDF1F3">
      <rect x="0" y="80" width="12" height="40"/>
      <rect x="14" y="68" width="10" height="52"/>
      <polygon points="30,50 34,50 42,80 26,80"/>
      <rect x="26" y="80" width="17" height="40"/>
      <rect x="46" y="75" width="15" height="45"/>
      <rect x="65" y="60" width="10" height="60"/>
      <rect x="78" y="82" width="18" height="38"/>
      <rect x="100" y="88" width="14" height="32"/>
      <ellipse cx="125" cy="84" rx="14" ry="9"/>
      <rect x="112" y="84" width="27" height="36"/>
      <rect x="118" y="68" width="3" height="18"/>
      <rect x="130" y="68" width="3" height="18"/>
      <rect x="160" y="78" width="14" height="42"/>
      <rect x="180" y="88" width="12" height="32"/>
      <polygon points="200,58 204,58 212,90 196,90"/>
      <rect x="196" y="90" width="17" height="30"/>
      <rect x="220" y="82" width="14" height="38"/>
      <rect x="240" y="74" width="10" height="46"/>
      <rect x="255" y="86" width="16" height="34"/>
      <rect x="275" y="90" width="125" height="30"/>
    </g>
  </svg>
  <div class="slim-text">
    <div class="slim-eyebrow">Economy &amp; External Sector Monitor</div>
    <div class="slim-title">{title}</div>
    <div class="slim-subtitle">{subtitle}</div>
  </div>
  <div class="slim-chips">
    <div class="slim-chip"><span class="slim-chip-dot"></span> {chip}</div>
    <div class="slim-chip"><span class="slim-chip-dot"></span> Data: SBP</div>
  </div>
</div>
"""


def render_top_bar(slim: bool = False, title: str = None, subtitle: str = None, chip_text: str = None) -> None:
    """
    Render the dashboard top banner.
    Call this at the top of every page script before other components.
    - slim=False  → full-height Executive Summary banner (~200 px)
    - slim=True   → compact banner for inner pages (~120 px)
    """
    st.markdown(
        """
        <style>
          [data-testid="stAppViewContainer"] > .main > .block-container {
              padding-top: 0 !important;
          }
          [data-testid="stHeader"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if slim:
        html = SLIM_TOPBAR_HTML_TEMPLATE.format(
            title=title or "Pakistan Workers&#8217; Remittances Analytics",
            subtitle=subtitle or "Country-wise inflows, FY73 to Sep 2026, in US dollars",
            chip=chip_text or "SBP Data"
        )
        st.html(html)
    else:
        st.html(FULL_TOPBAR_HTML)


# Backward-compatible alias
render_topbar = render_top_bar
