# ============================================
# FOOTER - MASI Futures Pro V0.0.0
# ============================================

import streamlit as st
import config
from datetime import datetime


def render_footer():
    """Affiche le footer de l'application."""
    st.divider()

    auteurs = " & ".join([a['nom'] for a in config.AUTHORS])

    st.markdown(f"""
        <div style='
            text-align: center;
            padding: 15px;
            color: {config.COLORS["text_muted"]};
            font-size: 0.85em;
            line-height: 1.8;
        '>
            <strong>{config.APP_NAME}</strong> v{config.APP_VERSION}
            &nbsp;|&nbsp; Conforme BAM IN-2026-01<br>
            © {datetime.now().year} — Développé par <strong>{auteurs}</strong><br>
            📧 {config.AUTHORS[0].get('email', '')}
        </div>
    """, unsafe_allow_html=True)
