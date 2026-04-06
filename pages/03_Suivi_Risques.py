# ============================================
# PAGE 3: SUIVI DES RISQUES - V0.0.0
# (Placeholder — à développer)
# ============================================

import streamlit as st
import config
from components.footer import render_footer

st.title("📊 Suivi des Risques")

st.markdown(f"""
    <div style='
        padding: 40px;
        background: linear-gradient(135deg, {config.COLORS["card"]}, #f0f4f8);
        border-radius: 14px;
        text-align: center;
        margin: 30px 0;
        border: 2px dashed {config.COLORS["border"]};
    '>
        <div style='font-size: 4em; margin-bottom: 15px;'>🚧</div>
        <h2 style='color: {config.COLORS["primary"]}; margin: 0 0 10px 0;'>Module en Développement</h2>
        <p style='color: {config.COLORS["text_muted"]}; font-size: 1.05em; max-width: 600px; margin: 0 auto;'>
            Le module de Suivi des Risques intégrera la VaR, le P&L, 
            les marges, le marking-to-market et les alertes.
        </p>
    </div>
""", unsafe_allow_html=True)

with st.expander("📋 Fonctionnalités prévues"):
    st.markdown("""
        - **VaR** : Value at Risk historique et paramétrique
        - **P&L** : Profit & Loss par position
        - **Marges** : Suivi des marges initiales et de maintenance
        - **Marking-to-Market** : Ajustement quotidien des positions
        - **Stress Testing** : Scénarios de stress sur le portefeuille
        - **Alertes** : Notifications d'appels de marge
    """)

render_footer()
