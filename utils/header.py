# ============================================
# HEADER - MASI Futures Pro V0.0.0
# ============================================

import streamlit as st
import config


def render_header():
    """Affiche le header principal de l'application."""
    st.markdown(f"""
        <div style='
            padding: 22px 28px;
            margin-bottom: 20px;
            border-radius: 12px;
            background: linear-gradient(135deg, {config.COLORS["primary"]} 0%, {config.COLORS["secondary"]} 100%);
            box-shadow: 0 4px 15px rgba(30, 58, 95, 0.25);
        '>
            <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;'>
                <div>
                    <h1 style='margin:0; color:white; font-size:1.8em; font-weight:700;'>
                        📊 {config.APP_NAME}
                    </h1>
                    <p style='margin:8px 0 0 0; color:rgba(255,255,255,0.85); font-size:1em;'>
                        {config.APP_SUBTITLE}
                    </p>
                </div>
                <div style='text-align:right;'>
                    <span style='
                        background: rgba(255,255,255,0.15);
                        color: white;
                        padding: 6px 14px;
                        border-radius: 20px;
                        font-size: 0.85em;
                        font-weight: 600;
                    '>
                        v{config.APP_VERSION}
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
