# ============================================
# NEWS WIDGET - MASI Futures Pro V0.0.0
# ============================================

import streamlit as st
import config
from utils.news_scraper import get_all_news


def render_news_widget(max_news=5):
    """Affiche les dernières actualités du marché."""

    st.markdown("### 📰 Actualités du Marché")

    with st.spinner("Chargement des actualités..."):
        df_news = get_all_news(force_refresh=False, max_total=max_news)

    if df_news.empty:
        st.info("ℹ️ Aucune actualité disponible pour le moment.")
        return

    for _, row in df_news.iterrows():
        source = row.get('source', '')
        titre = row.get('titre', '')
        resume = row.get('resume', '')
        url = row.get('url', '')
        categorie = row.get('categorie', 'N/A')
        date = row.get('date', '')

        # Couleur par catégorie
        cat_colors = {
            'Produits Dérivés': config.COLORS['primary'],
            'Marché': config.COLORS['success'],
            'Réglementation': config.COLORS['warning'],
            'Institutionnel': config.COLORS['info'],
        }
        cat_color = cat_colors.get(categorie, config.COLORS['text_muted'])

        st.markdown(f"""
            <div style='
                padding: 16px 20px;
                background: {config.COLORS["card"]};
                border-radius: 10px;
                margin-bottom: 10px;
                border-left: 4px solid {cat_color};
                box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            '>
                <div style='display:flex; justify-content:space-between; align-items:flex-start; gap:10px;'>
                    <div style='flex:1;'>
                        <p style='margin:0 0 6px 0; font-weight:600; color:{config.COLORS["text"]}; font-size:0.95em;'>
                            {titre}
                        </p>
                        <p style='margin:0; color:{config.COLORS["text_muted"]}; font-size:0.82em;'>
                            {resume[:180] + '...' if len(resume) > 180 else resume}
                        </p>
                    </div>
                </div>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-top:10px;'>
                    <div style='display:flex; gap:12px; align-items:center;'>
                        <span style='
                            background: {cat_color}15;
                            color: {cat_color};
                            padding: 2px 10px;
                            border-radius: 12px;
                            font-size: 0.75em;
                            font-weight: 600;
                        '>{categorie}</span>
                        <span style='color:{config.COLORS["text_muted"]}; font-size:0.75em;'>
                            {source} · {date}
                        </span>
                    </div>
                    {'<a href="' + url + '" target="_blank" style="color:' + config.COLORS["primary"] + '; font-size:0.8em; text-decoration:none; font-weight:600;">Lire →</a>' if url else ''}
                </div>
            </div>
        """, unsafe_allow_html=True)
