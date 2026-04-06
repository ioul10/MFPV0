# ============================================
# PAGE 1: NEWS & INDICES - MASI Futures Pro V0.0.0
# Niveaux, Évolution, Statistiques, Actualités
# Basé sur le document CDG Capital
# ============================================

import streamlit as st
import config
from utils.scraping import get_indices_bourse
from utils.data_generator import (
    generer_donnees_historiques,
    calculer_statistiques,
    build_ohlc_dataframe,
    build_stats_dataframe,
)
from components.news_widget import render_news_widget
from components.footer import render_footer
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go

# ════════════════════════════════════════════
# TITRE
# ════════════════════════════════════════════
st.title("📰 News & Indices MASI")
st.caption("Niveaux en temps réel, évolution historique, statistiques descriptives et actualités du marché")

# ════════════════════════════════════════════
# 1. NIVEAUX ACTUELS DES INDICES
# ════════════════════════════════════════════
st.markdown("---")
st.markdown("### 📊 Niveaux Actuels des Indices")

indices_data = get_indices_bourse()

if indices_data:
    col1, col2 = st.columns(2)

    for idx_name in ['MASI', 'MASI20']:
        idx_data = indices_data.get(idx_name)
        if not idx_data:
            continue

        col = col1 if idx_name == 'MASI' else col2
        variation = idx_data.get('variation', '+0.00%')
        is_positive = '+' in variation or (not variation.startswith('-'))
        couleur = config.COLORS["success"] if is_positive else config.COLORS["danger"]
        arrow = "▲" if is_positive else "▼"
        source_tag = idx_data.get('source', 'mock')
        source_badge = "🟢 Live" if source_tag == 'live' else "🟡 Simulé"

        with col:
            st.markdown(f"""
                <div style='
                    padding: 22px;
                    background: {config.COLORS["card"]};
                    border-radius: 12px;
                    margin-bottom: 12px;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.06);
                    border-left: 5px solid {config.COLORS["primary"]};
                '>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div>
                            <div style='display:flex; align-items:center; gap:8px; margin-bottom:8px;'>
                                <h3 style='margin:0; color:{config.COLORS["primary"]}; font-size:1.2em;'>
                                    🇲🇦 {idx_data['nom']}
                                </h3>
                                <span style='
                                    font-size:0.7em; 
                                    background: {"#D1FAE5" if source_tag == "live" else "#FEF3C7"}; 
                                    color: {"#065F46" if source_tag == "live" else "#92400E"};
                                    padding:2px 8px; 
                                    border-radius:10px;
                                '>{source_badge}</span>
                            </div>
                            <p style='margin:0; font-size:2em; font-weight:700; color:{config.COLORS["text"]};'>
                                {idx_data['niveau']:,.2f}
                            </p>
                        </div>
                        <div style='text-align:right;'>
                            <p style='margin:0; font-size:1.3em; font-weight:600; color:{couleur};'>
                                {arrow} {variation}
                            </p>
                            <p style='margin:5px 0 0 0; color:{config.COLORS["text_muted"]}; font-size:0.8em;'>
                                {idx_data.get('timestamp', '')}
                            </p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
else:
    st.error("❌ Impossible de récupérer les données des indices.")

# ════════════════════════════════════════════
# 2. CONTEXTE: POURQUOI LES FUTURES MASI/MASI20
# ════════════════════════════════════════════
st.markdown("---")

with st.expander("📘 Contexte — Les Futures sur Indices MASI et MASI20", expanded=False):
    st.markdown(f"""
        #### 🎯 Objectif Général

        L'introduction des contrats futures sur les indices **MASI** et **MASI20** vise à doter 
        le marché financier marocain d'un instrument de gestion du risque moderne. L'objectif principal :

        > *Améliorer l'efficacité du marché en permettant la couverture, l'optimisation de l'allocation 
        et la découverte des prix.*

        #### 📋 Qu'est-ce qu'un Future sur Indice ?

        Un **future sur indice** est un contrat standardisé permettant de prendre une position sur 
        la performance globale d'un indice boursier **sans détenir les actions** qui le composent. 
        Il se caractérise par :

        - Un **prix fixé à l'avance** (le prix future)
        - Une **échéance déterminée** (trimestrielle : Mars, Juin, Sept, Déc)
        - Un **règlement en cash** (pas de livraison physique)
        - Une **chambre de compensation** (CCP) qui garantit les engagements

        #### 🏦 Rôle de CDG Capital

        CDG Capital intervient sur **4 rôles** dans la chaîne de valeur :

        | Rôle | Description |
        |------|-------------|
        | **Investisseur** | Trading pour compte propre, gestion active |
        | **Négociateur** | Exécution des ordres, animation de la liquidité |
        | **Compensateur** | Gestion des marges et appels de marge via la CCP |
        | **Post-trade** | Règlement, rapprochement, reporting |

        #### 📈 Impacts Attendus

        - Augmentation de la profondeur et liquidité du marché
        - Meilleure formation des prix (price discovery)
        - Attraction des investisseurs institutionnels et internationaux
        - Couverture du risque de marché (hedging)
        - Stratégies d'arbitrage spot/futures
    """)


# ════════════════════════════════════════════
# 3. DONNÉES HISTORIQUES ET ANALYSE
# ════════════════════════════════════════════
st.markdown("---")

# Récupérer les niveaux
niveau_masi = indices_data.get('MASI', {}).get('niveau', 16500.0) if indices_data else 16500.0
niveau_masi20 = indices_data.get('MASI20', {}).get('niveau', 1870.0) if indices_data else 1870.0

# Générer les données
donnees_masi = generer_donnees_historiques('MASI', niveau_masi)
donnees_masi20 = generer_donnees_historiques('MASI20', niveau_masi20)

stats_masi = calculer_statistiques(donnees_masi)
stats_masi20 = calculer_statistiques(donnees_masi20)


# ────────────────────────────────────────────
# FONCTIONS D'AFFICHAGE
# ────────────────────────────────────────────

def render_chart(nom, donnees, couleur):
    """Graphique d'évolution avec area fill."""
    fig = go.Figure()

    fill_color = 'rgba(16,185,129,0.08)' if nom == 'MASI' else 'rgba(30,58,95,0.08)'

    fig.add_trace(go.Scatter(
        x=donnees['dates'],
        y=donnees['prices'],
        name=nom,
        line=dict(color=couleur, width=2.5),
        fill='tozeroy',
        fillcolor=fill_color,
        hovertemplate='<b>%{x|%d %b %Y}</b><br>Niveau: %{y:,.2f}<extra></extra>',
    ))

    # Ligne moyenne
    avg = np.mean(donnees['prices'])
    fig.add_hline(
        y=avg,
        line_dash="dot",
        line_color="#9CA3AF",
        annotation_text=f"Moyenne: {avg:,.2f}",
        annotation_position="top left",
    )

    fig.update_layout(
        title=dict(text=f'Évolution du {nom} — 90 derniers jours', font=dict(size=16)),
        xaxis_title='Date',
        yaxis_title='Niveau',
        height=420,
        template='plotly_white',
        hovermode='x unified',
        margin=dict(t=50, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_candlestick(nom, donnees, couleur):
    """Graphique chandelier OHLC."""
    fig = go.Figure(data=[go.Candlestick(
        x=donnees['dates'],
        open=donnees['opens'],
        high=donnees['highs'],
        low=donnees['lows'],
        close=donnees['prices'],
        increasing_line_color=config.COLORS['success'],
        decreasing_line_color=config.COLORS['danger'],
        name=nom,
    )])

    fig.update_layout(
        title=dict(text=f'Chandelier {nom} — 90 jours', font=dict(size=16)),
        xaxis_title='Date',
        yaxis_title='Niveau',
        height=420,
        template='plotly_white',
        xaxis_rangeslider_visible=False,
        margin=dict(t=50, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_returns_histogram(nom, donnees, couleur):
    """Histogramme de distribution des rendements."""
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=donnees['returns'] * 100,
        nbinsx=30,
        marker_color=couleur,
        opacity=0.75,
        name='Rendements (%)',
        hovertemplate='Rendement: %{x:.2f}%<br>Fréquence: %{y}<extra></extra>',
    ))

    fig.update_layout(
        title=dict(text=f'Distribution des Rendements — {nom}', font=dict(size=16)),
        xaxis_title='Rendement quotidien (%)',
        yaxis_title='Fréquence',
        height=350,
        template='plotly_white',
        bargap=0.05,
        margin=dict(t=50, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_interpretations(stats, nom, niveau_actuel):
    """Affiche les interprétations financières de toutes les statistiques."""

    # ── Prix et Performance ──
    st.markdown("#### 📈 Prix et Performance")

    st.info(f"**Prix Minimum : {stats['prix_minimum']:,.2f}**")
    st.caption("Support historique sur 90 jours. Si le cours actuel est proche, possibilité de zone d'achat.")

    st.info(f"**Prix Maximum : {stats['prix_maximum']:,.2f}**")
    st.caption("Résistance historique. Si le cours actuel est proche, possible résistance à la hausse.")

    tendance = "au-dessus" if niveau_actuel > stats['moyenne'] else "en-dessous"
    signal = "haussière" if niveau_actuel > stats['moyenne'] else "baissière"
    st.info(f"**Moyenne : {stats['moyenne']:,.2f}**")
    st.caption(f"Cours actuel ({niveau_actuel:,.2f}) {tendance} de la moyenne → tendance {signal} à moyen terme.")

    st.info(f"**Médiane : {stats['mediane']:,.2f}**")
    st.caption("50e percentile. Moins sensible aux extrêmes que la moyenne, utile pour une analyse robuste.")

    perf = stats['performance_cumulee']
    st.info(f"**Performance Cumulée : {perf:+.2f}%**")
    st.caption(f"Un investisseur passif aurait {'gagné' if perf > 0 else 'perdu'} {abs(perf):.2f}% sur 90 jours.")

    st.markdown("---")

    # ── Volatilité ──
    st.markdown("#### 📊 Volatilité et Rendements")

    st.info(f"**Volatilité Quotidienne : {stats['volatilite_quotidienne']:.2f}%**")
    st.caption("Écart-type des rendements journaliers. 1–2% est typique pour un indice émergent.")

    st.info(f"**Volatilité Annualisée : {stats['volatilite_annualisee']:.2f}%**")
    st.caption("Risque annuel standardisé. Pour le MASI, 15–25% est dans la norme historique.")

    st.info(f"**Rendement Min : {stats['rendement_minimum']:+.2f}% · Max : {stats['rendement_maximum']:+.2f}%**")
    st.caption("Pire perte et meilleur gain journalier. Utile pour l'évaluation du risque extrême (VaR historique).")

    st.markdown("---")

    # ── Distribution ──
    st.markdown("#### 📐 Distribution des Rendements")

    skew = stats['skewness']
    if skew > 0.5:
        skew_txt = "positive — plus de gains extrêmes que de pertes"
        skew_badge = "✅ Favorable"
    elif skew < -0.5:
        skew_txt = "négative — plus de pertes extrêmes que de gains"
        skew_badge = "⚠️ Prudence"
    else:
        skew_txt = "proche de zéro — distribution symétrique"
        skew_badge = "ℹ️ Neutre"

    st.info(f"**Skewness : {skew:.4f}** {skew_badge}")
    st.caption(f"Asymétrie {skew_txt}. Un skewness positif indique plus de chances de gains exceptionnels.")

    kurt = stats['kurtosis']
    if kurt > 3:
        kurt_txt = f"élevé ({kurt:.2f} > 3) — fat tails, événements extrêmes plus fréquents"
        kurt_badge = "⚠️ Risque extrême"
    elif kurt < 0:
        kurt_txt = f"négatif ({kurt:.2f}) — distribution plus plate que la normale"
        kurt_badge = "ℹ️ Modéré"
    else:
        kurt_txt = f"modéré ({kurt:.2f}) — proche d'une distribution normale"
        kurt_badge = "✅ Normal"

    st.info(f"**Kurtosis : {kurt:.4f}** {kurt_badge}")
    st.caption(f"Aplatissement {kurt_txt}. Un kurtosis élevé signifie plus de risque de krachs ou rallies soudains.")


def render_indice_section(nom, donnees, stats, niveau_actuel, couleur):
    """Section complète d'analyse pour un indice."""

    # Sélecteur de type de graphique
    chart_type = st.radio(
        f"Type de graphique — {nom}",
        ["📈 Ligne", "🕯️ Chandelier"],
        horizontal=True,
        key=f"chart_type_{nom}",
    )

    if chart_type == "📈 Ligne":
        render_chart(nom, donnees, couleur)
    else:
        render_candlestick(nom, donnees, couleur)

    # Distribution des rendements
    render_returns_histogram(nom, donnees, couleur)

    # Tableau OHLC
    st.markdown(f"### 📋 Données OHLC — {nom}")
    df = build_ohlc_dataframe(donnees)
    st.dataframe(
        df.style.format({
            'Open': '{:,.2f}', 'High': '{:,.2f}', 'Low': '{:,.2f}',
            'Close': '{:,.2f}', 'Volume': '{:,.0f}', 'Change %': '{:+.2f}%',
        }),
        use_container_width=True,
        height=400,
    )

    # Statistiques
    st.markdown(f"### 📊 Statistiques Descriptives — {nom}")
    df_stats = build_stats_dataframe(stats)
    st.dataframe(df_stats, use_container_width=True, hide_index=True)

    # Interprétations
    with st.expander(f"📘 Interprétations Financières — {nom}", expanded=False):
        render_interpretations(stats, nom, niveau_actuel)


# ════════════════════════════════════════════
# ONGLETS MASI / MASI20 / COMPARAISON
# ════════════════════════════════════════════

tab1, tab2, tab3 = st.tabs(["🇲🇦 MASI", "🇲🇦 MASI20", "📊 Comparaison"])

with tab1:
    st.markdown("### 📈 Analyse de l'Indice MASI")
    st.caption("Moroccan All Shares Index — Indice global du marché actions marocain")
    render_indice_section("MASI", donnees_masi, stats_masi, niveau_masi, config.COLORS['success'])

with tab2:
    st.markdown("### 📈 Analyse de l'Indice MASI20")
    st.caption("Indice des 20 titres les plus liquides — Sous-jacent du contrat Future")
    render_indice_section("MASI20", donnees_masi20, stats_masi20, niveau_masi20, config.COLORS['primary'])

with tab3:
    st.markdown("### 📊 Comparaison MASI vs MASI20")
    st.caption("Performance relative normalisée (Base 100) et comparaison des statistiques")

    # ── Graphique comparatif ──
    masi_norm = [p / donnees_masi['prices'][0] * 100 for p in donnees_masi['prices']]
    masi20_norm = [p / donnees_masi20['prices'][0] * 100 for p in donnees_masi20['prices']]

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Scatter(
        x=donnees_masi['dates'], y=masi_norm, name='MASI',
        line=dict(color=config.COLORS['success'], width=2.5),
    ))
    fig_comp.add_trace(go.Scatter(
        x=donnees_masi20['dates'], y=masi20_norm, name='MASI20',
        line=dict(color=config.COLORS['primary'], width=2.5, dash='dash'),
    ))
    fig_comp.add_hline(y=100, line_dash="dot", line_color="#D1D5DB")

    fig_comp.update_layout(
        title=dict(text='Performance Relative (Base 100)', font=dict(size=16)),
        xaxis_title='Date',
        yaxis_title='Performance normalisée',
        height=450,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=40),
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # ── Tableau comparatif ──
    st.markdown("### 📋 Tableau Comparatif")

    comp_data = {
        'Statistique': [
            'Niveau Actuel', 'Prix Minimum', 'Prix Maximum', 'Moyenne', 'Médiane',
            'Performance Cumulée', 'Volatilité Annualisée',
            'Rendement Max', 'Rendement Min', 'Skewness', 'Kurtosis',
        ],
        'MASI': [
            f"{niveau_masi:,.2f}",
            f"{stats_masi['prix_minimum']:,.2f}",
            f"{stats_masi['prix_maximum']:,.2f}",
            f"{stats_masi['moyenne']:,.2f}",
            f"{stats_masi['mediane']:,.2f}",
            f"{stats_masi['performance_cumulee']:+.2f}%",
            f"{stats_masi['volatilite_annualisee']:.2f}%",
            f"{stats_masi['rendement_maximum']:+.2f}%",
            f"{stats_masi['rendement_minimum']:+.2f}%",
            f"{stats_masi['skewness']:.4f}",
            f"{stats_masi['kurtosis']:.4f}",
        ],
        'MASI20': [
            f"{niveau_masi20:,.2f}",
            f"{stats_masi20['prix_minimum']:,.2f}",
            f"{stats_masi20['prix_maximum']:,.2f}",
            f"{stats_masi20['moyenne']:,.2f}",
            f"{stats_masi20['mediane']:,.2f}",
            f"{stats_masi20['performance_cumulee']:+.2f}%",
            f"{stats_masi20['volatilite_annualisee']:.2f}%",
            f"{stats_masi20['rendement_maximum']:+.2f}%",
            f"{stats_masi20['rendement_minimum']:+.2f}%",
            f"{stats_masi20['skewness']:.4f}",
            f"{stats_masi20['kurtosis']:.4f}",
        ],
    }

    df_comp = pd.DataFrame(comp_data)
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    # ── Interprétation comparative ──
    with st.expander("📘 Interprétation de la Comparaison"):
        vol_masi = stats_masi['volatilite_annualisee']
        vol_masi20 = stats_masi20['volatilite_annualisee']
        plus_volatile = "MASI20" if vol_masi20 > vol_masi else "MASI"

        perf_masi = stats_masi['performance_cumulee']
        perf_masi20 = stats_masi20['performance_cumulee']
        plus_performant = "MASI20" if perf_masi20 > perf_masi else "MASI"

        st.markdown(f"""
            **Volatilité :** Le **{plus_volatile}** est plus volatile 
            ({vol_masi20:.2f}% vs {vol_masi:.2f}% annualisée). 
            Cela s'explique par la concentration du MASI20 sur 20 titres seulement, 
            contrairement au MASI qui est plus diversifié.

            **Performance :** Le **{plus_performant}** a mieux performé sur la période 
            ({perf_masi20:+.2f}% vs {perf_masi:+.2f}%).

            **Implication pour les Futures :** Le MASI20 étant le sous-jacent du contrat future, 
            sa volatilité plus élevée implique des appels de marge potentiellement plus importants 
            et des opportunités d'arbitrage plus fréquentes entre le prix spot et le prix future.
        """)


# ════════════════════════════════════════════
# 4. ACTUALITÉS
# ════════════════════════════════════════════
st.markdown("---")
render_news_widget(max_news=5)

# ════════════════════════════════════════════
# 5. CONCEPTS CLÉS (du PDF)
# ════════════════════════════════════════════
st.markdown("---")
st.markdown("### 📚 Concepts Clés — Marché à Terme")

col_c1, col_c2, col_c3 = st.columns(3)

concepts = [
    (col_c1, "🔄", "Convergence Spot/Future",
     "À l'approche de l'échéance, le prix future converge vers le prix spot. "
     "Si un écart persiste, les arbitragistes interviennent pour rétablir l'équilibre."),
    (col_c2, "💰", "Appels de Marge",
     "Le marking-to-market quotidien ajuste les comptes des positions. "
     "Si le solde descend sous la marge de maintenance, un appel de marge est déclenché."),
    (col_c3, "📐", "Formule de Pricing",
     "F₀ = S₀ × e^((r-q)×T) où r est le taux sans risque BKAM "
     "et q le rendement en dividende du MASI20."),
]

for col, icon, title, desc in concepts:
    with col:
        st.markdown(f"""
            <div style='
                padding: 20px;
                background: {config.COLORS["card"]};
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                min-height: 180px;
            '>
                <div style='font-size: 2em; margin-bottom: 8px;'>{icon}</div>
                <h4 style='color: {config.COLORS["primary"]}; margin: 0 0 8px 0; font-size: 1em;'>{title}</h4>
                <p style='color: {config.COLORS["text_muted"]}; margin: 0; font-size: 0.85em; line-height: 1.6;'>
                    {desc}
                </p>
            </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════
render_footer()
