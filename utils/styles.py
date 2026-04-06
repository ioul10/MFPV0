# ============================================
# STYLES - MASI Futures Pro V0.0.0
# CSS global réutilisable
# ============================================

import streamlit as st
import config


def inject_global_css():
    """Injecte le CSS global de l'application."""
    st.markdown(f"""
        <style>
        /* ── Background ── */
        .main {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 50%, #d4dce6 100%);
        }}

        /* ── Header bar ── */
        .stApp > header {{
            background: linear-gradient(90deg, {config.COLORS["primary"]} 0%, {config.COLORS["secondary"]} 100%);
            box-shadow: 0 2px 8px rgba(30, 58, 95, 0.3);
        }}

        /* ── Boutons ── */
        .stButton > button {{
            background: linear-gradient(135deg, {config.COLORS["primary"]} 0%, {config.COLORS["secondary"]} 100%);
            color: white !important;
            border: none;
            border-radius: 8px;
            padding: 8px 20px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        .stButton > button:hover {{
            background: linear-gradient(135deg, {config.COLORS["secondary"]} 0%, {config.COLORS["accent"]} 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(30, 58, 95, 0.3);
        }}

        /* ── Cards ── */
        .metric-card {{
            padding: 25px;
            background: {config.COLORS["card"]};
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: all 0.3s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(30, 58, 95, 0.12);
        }}

        /* ── Dev Banner ── */
        .dev-banner {{
            padding: 18px 24px;
            background: linear-gradient(135deg, #FEF3C7, #FDE68A);
            border-radius: 12px;
            border-left: 5px solid #F59E0B;
            margin-bottom: 15px;
        }}

        /* ── Tabs styling ── */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        .stTabs [data-baseweb="tab"] {{
            padding: 8px 20px;
            border-radius: 8px 8px 0 0;
        }}

        /* ── Divider ── */
        hr {{
            border: none;
            border-top: 1px solid {config.COLORS["border"]};
            margin: 20px 0;
        }}
        </style>
    """, unsafe_allow_html=True)
