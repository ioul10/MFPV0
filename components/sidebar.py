# ============================================
# SIDEBAR - MASI Futures Pro V0.0.0
# ============================================

import streamlit as st
import config
import time
from datetime import datetime


def render_sidebar():
    """Affiche la sidebar avec logo, statut et navigation."""

    with st.sidebar:

        # ── Animation de chargement (1ère fois) ──
        if 'sidebar_initialized' not in st.session_state:
            progress = st.progress(0)
            status = st.empty()

            for pct, msg in [(25, "🔍 Vérification des connexions..."),
                             (50, "📊 Connexion à BKAM..."),
                             (75, "🏦 Connexion Bourse de Casablanca..."),
                             (100, "✅ Application prête !")]:
                status.text(msg)
                time.sleep(0.3)
                progress.progress(pct)

            progress.empty()
            status.empty()
            st.session_state['sidebar_initialized'] = True

        # ── Logo ──
        try:
            st.image("logo.png", use_container_width=True)
        except Exception:
            st.markdown(
                "<div style='text-align:center; font-size:3.5em; margin:10px 0;'>📈</div>",
                unsafe_allow_html=True,
            )

        st.markdown(f"""
            <div style='text-align:center; margin:10px 0 5px 0;'>
                <h2 style='font-size:1.4em; margin:0; color:{config.COLORS["primary"]}; font-weight:700;'>
                    {config.APP_NAME}
                </h2>
                <p style='color:{config.COLORS["text_muted"]}; margin:3px 0; font-size:0.85em;'>
                    v{config.APP_VERSION}
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Statut des données ──
        st.markdown("#### 🔗 Statut des Données")

        statut_bkam = st.session_state.get('statut_bkam', '🟡')
        statut_bourse = st.session_state.get('statut_bourse', '🟡')
        statut_news = st.session_state.get('statut_news', '🟡')

        st.markdown(f"""
            <div style='font-size:0.9em; line-height:2;'>
                {statut_bkam} <strong>BKAM</strong> — Taux sans risque<br>
                {statut_bourse} <strong>Bourse de Casablanca</strong> — Indices<br>
                {statut_news} <strong>News</strong> — Actualités
            </div>
        """, unsafe_allow_html=True)

        st.caption("🟢 Live · 🟡 Mock/Cache · 🔴 Erreur")

        st.divider()

        # ── Navigation ──
        st.markdown("#### 🧭 Paramètres")

        indice_defaut = st.selectbox(
            "🇲🇦 Indice de Référence",
            config.INDICES,
            index=0,
        )
        st.session_state['indice_defaut'] = indice_defaut

        st.info(f"💰 Multiplicateur : **{config.MULTIPLICATEUR} {config.DEVISE}/point**")

        st.divider()

        # ── Spécifications Contrat (du PDF) ──
        st.markdown("#### 📋 Contrat Future")
        fc = config.FUTURES_CONFIG
        st.markdown(f"""
            <div style='font-size:0.82em; line-height:1.8; color:{config.COLORS["text_muted"]};'>
                <strong>Sous-jacent :</strong> {fc['sous_jacent']}<br>
                <strong>Multiplicateur :</strong> {fc['multiplicateur']} MAD/pt<br>
                <strong>Pas de cotation :</strong> {fc['pas_cotation']} pt<br>
                <strong>Échéances :</strong> {', '.join(fc['echeances'])}<br>
                <strong>Dénouement :</strong> {fc['mode_denouement']}<br>
                <strong>Dépôt garantie :</strong> {fc['depot_garantie']:,} MAD
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Auteurs ──
        st.markdown("#### 👥 Développeurs")
        for a in config.AUTHORS:
            st.write(f"👤 **{a['nom']}**")

        st.divider()

        # ── Footer sidebar ──
        st.caption(f"© {datetime.now().year} {config.APP_NAME}")
        st.caption("Conforme Instruction BAM N° IN-2026-01")
