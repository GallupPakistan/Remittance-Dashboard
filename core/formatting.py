"""
formatting.py
Formatters for numbers, currency, and percentage in natural human-friendly English.
Display-only: never modifies stored underlying data.
"""

def fmt_usd_bn(val, decimals=1):
    """
    Format value in billions of USD.
    e.g. 41.623 -> 'US$ 41.6B'
    """
    if val is None or val == 0:
        return "US$ 0.0B"
    return f"US$ {val:.{decimals}f}B"

def fmt_usd_m(val, decimals=1):
    """
    Format value in millions of USD.
    e.g. 3587.7 -> 'US$ 3,587.8M'
    """
    if val is None or val == 0:
        return "US$ 0.0M"
    return f"US$ {val:,.{decimals}f}M"

def fmt_growth(pct, decimals=1):
    """
    Format percentage growth with direction sign.
    """
    if pct is None:
        return "0.0%"
    sign = "+" if pct > 0 else ""
    return f"{sign}{pct:.{decimals}f}%"

def fmt_share(pct, decimals=1):
    """
    Format percentage share.
    """
    if pct is None:
        return "0.0%"
    return f"{pct:.{decimals}f}%"
