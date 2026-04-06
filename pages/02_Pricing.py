# ============================================
# PAGE 2: PRICING — MASI Futures Pro V0.0.0
# Valorisation des Contrats Futures MASI20
# Conforme Instruction BAM N° IN-2026-01
#
# F₀ = S₀ × e^((r − q) × T)
# ============================================

import streamlit as st
import config
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

from utils.calculations import (
    prix_future_theorique,
    calculer_base,
    calculer_cout_portage,
    calculer_sensibilites,
    calculer_taux_dividende_indice,
    get_taux_zc,
    calcul_term_structure,
    detecter_arbitrage,
    backtesting_complet,
    calculer_mae,
    calculer_mape,
    calculer_r2,
    valeur_notionnelle,
    prochaine_echeance_trimestrielle,
)
from utils.data_loader import (
    charger_taux_zc,
    charger_dividendes,
    charger_historique_masi20,
    template_taux_zc,
    template_dividendes,
)
from components.footer import render_footer

# ════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════
st.markdown("""
<style>
    .pricing-card {
        padding: 22px; border-radius: 12px;
        background: linear-gradient(135deg, #f8f9fa 0%, #eef1f5 100%);
        border-left: 5px solid #1E3A5F;
        margin: 8px 0; box-shadow: 0 2px 8px rgba(30,58,95,0.08);
    }
    .pricing-card h4 { margin: 0 0 8px 0; color: #1E3A5F; font-size: 0.9em; }
    .pricing-card .value {
        font-size: 1.8em; font-weight: 700; margin: 0;
        font-family: 'SF Mono', 'Fira Code', monospace;
    }
    .pricing-card .sub { margin: 4px 0 0 0; color: #6B7280; font-size: 0.82em; }
    .alert-card { padding: 18px; border-radius: 10px; margin: 8px 0; }
    .alert-success { background: linear-gradient(135deg, #ecfdf5, #d1fae5); border-left: 5px solid #10B981; }
    .alert-warning { background: linear-gradient(135deg, #fffbeb, #fef3c7); border-left: 5px solid #F59E0B; }
    .alert-danger  { background: linear-gradient(135deg, #fef2f2, #fee2e2); border-left: 5px solid #EF4444; }
    .alert-info    { background: linear-gradient(135deg, #eff6ff, #dbeafe); border-left: 5px solid #3B82F6; }
    .param-box {
        padding: 14px 18px; background: white; border-radius: 10px;
        border: 1px solid #E5E7EB; margin: 6px 0; font-size: 0.9em;
    }
    .param-box strong { color: #1E3A5F; }
    .formula-box {
        padding: 18px 24px; background: linear-gradient(135deg, #1E3A5F, #2E5C8A);
        border-radius: 12px; text-align: center; margin: 15px 0;
    }
    .formula-box p { color: white; margin: 0; font-size: 1.4em; font-weight: 600; font-family: Georgia, serif; }
    .formula-box .label { font-size: 0.75em; color: rgba(255,255,255,0.7); margin-top: 6px; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════
# EN-TETE
# ════════════════════════════════════════════
st.title("🧮 Pricing des Futures MASI20")
st.caption("Module de valorisation — Conforme Instruction BAM N° IN-2026-01")

st.markdown("""
<div class='formula-box'>
    <p>F₀ = S₀ × e<sup>(r − q) × T</sup></p>
    <p class='label'>Formule du prix théorique — Absence d'arbitrage</p>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════
for k, v in {'donnees_valides': False, 'date_reference': None, 'df_taux': None,
             'df_div': None, 'q_mode_auto': False, 'q_manual': 0.87, 'q_calculated': 0.0087}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════════
# ONGLETS
# ════════════════════════════════════════════
tab_import, tab_pricing, tab_term, tab_backtest, tab_arb = st.tabs([
    "📥 Import des Données", "📈 Pricing F₀", "📊 Term Structure", "🧪 Backtesting", "🚨 Arbitrage",
])

# ──────────────────────────────────────
# ONGLET 1 — IMPORT
# ──────────────────────────────────────
with tab_import:
    with st.expander("📘 Guide — Données nécessaires", expanded=False):
        st.markdown("""
            | Input | Variable | Source | Format |
            |-------|----------|--------|--------|
            | **Taux sans risque** | r | BKAM | `date_spot, date_maturity, zc` |
            | **Taux de dividende** | q | MASI20 | `ticker, poids, cours, dividende_annuel` |
            | **Prix spot** | S₀ | Bourse Casa | Saisie manuelle |
        """)

    st.markdown("---")
    st.markdown("### 🏦 Taux Zéro-Coupon (r)")

    col_u, col_t = st.columns([4, 1])
    with col_u:
        uploaded_taux = st.file_uploader("Fichier Taux ZC", type=['csv', 'xlsx'], key="taux_up")
    with col_t:
        st.download_button("📄 Template", data=template_taux_zc(), file_name="template_taux_zc.csv", mime="text/csv")

    if uploaded_taux:
        df_taux = charger_taux_zc(uploaded_taux, utiliser_mock=False)
    else:
        df_taux = charger_taux_zc(utiliser_mock=True)
        st.caption("🟡 Données mock")

    if df_taux is not None:
        st.session_state['df_taux'] = df_taux
        with st.expander("Aperçu taux ZC"):
            st.dataframe(df_taux.head(12), use_container_width=True)

        dates_spot = sorted(df_taux['date_spot'].unique(), reverse=True)
        if dates_spot:
            date_ref = st.selectbox("📅 Date Spot de Référence", dates_spot,
                format_func=lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else str(x))
            st.session_state['date_reference'] = date_ref
            nb_mat = len(df_taux[df_taux['date_spot'] == date_ref])
            st.markdown(f"""<div class='pricing-card'><h4>📅 Date de Référence</h4>
                <p class='value'>{date_ref.strftime('%d/%m/%Y') if hasattr(date_ref, 'strftime') else date_ref}</p>
                <p class='sub'>{nb_mat} maturités</p></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💰 Taux de Dividende (q)")

    q_mode = st.radio("Mode", ["📁 Import fichier", "✏️ Saisie manuelle"], horizontal=True)

    if q_mode == "📁 Import fichier":
        col_u2, col_t2 = st.columns([4, 1])
        with col_u2:
            uploaded_div = st.file_uploader("Fichier Dividendes", type=['csv', 'xlsx'], key="div_up")
        with col_t2:
            st.download_button("📄 Template", data=template_dividendes(), file_name="template_div.csv", mime="text/csv")

        if uploaded_div:
            df_div = charger_dividendes(uploaded_div, utiliser_mock=False)
        else:
            df_div = charger_dividendes(utiliser_mock=True)
            st.caption("🟡 Données mock")

        if df_div is not None:
            st.session_state['df_div'] = df_div
            constituents = df_div.to_dict('records')
            date_ech_f = st.session_state.get('date_reference')
            if date_ech_f:
                date_ech_f = pd.to_datetime(date_ech_f) + timedelta(days=90)
            q_calc, df_q = calculer_taux_dividende_indice(constituents, date_ech_f)
            st.session_state['q_calculated'] = q_calc

            st.markdown(f"""<div class='pricing-card' style='border-left-color:#10B981;'>
                <h4>💰 q calculé</h4><p class='value' style='color:#10B981;'>q = {q_calc*100:.4f}%</p>
                <p class='sub'>Σ(Pᵢ × Dᵢ/Cᵢ) — {len(constituents)} titres</p></div>""", unsafe_allow_html=True)
            with st.expander("📊 Détail"):
                st.dataframe(df_q, use_container_width=True, hide_index=True)
    else:
        q_m = st.number_input("q (%)", 0.0, 10.0, st.session_state['q_manual'], 0.01, "%.4f")
        st.session_state['q_calculated'] = q_m / 100
        st.session_state['q_manual'] = q_m

    st.markdown("---")
    is_valid = st.session_state['df_taux'] is not None and st.session_state['date_reference'] is not None
    st.session_state['donnees_valides'] = is_valid
    if is_valid:
        st.markdown("<div class='alert-card alert-success'><strong>✅ Données prêtes</strong></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='alert-card alert-warning'><strong>⚠️ Importez les taux ZC et sélectionnez une date</strong></div>", unsafe_allow_html=True)

# ──────────────────────────────────────
# ONGLET 2 — PRICING F₀
# ──────────────────────────────────────
with tab_pricing:
    if not st.session_state['donnees_valides']:
        st.warning("⚠️ Importez d'abord les données.")
        st.stop()

    st.markdown("### 📈 Calcul du Prix Théorique")
    col_s, col_j = st.columns(2)
    with col_s:
        spot = st.number_input("Spot S₀", min_value=100.0, value=1876.54, step=10.0, format="%.2f")
    with col_j:
        prochaine = prochaine_echeance_trimestrielle()
        date_ref = st.session_state['date_reference']
        j_def = max(30, min(360, (prochaine - pd.to_datetime(date_ref)).days if date_ref else 90))
        jours_echeance = st.slider("Échéance (jours)", 7, 360, j_def, 1)

    date_calcul = pd.to_datetime(st.session_state['date_reference'])
    date_echeance = date_calcul + timedelta(days=jours_echeance)
    r = get_taux_zc(date_calcul, date_echeance, st.session_state['df_taux'])
    q = st.session_state['q_calculated']
    T = jours_echeance / 360

    F0 = prix_future_theorique(spot, r, q, T)
    base = calculer_base(F0, spot)
    cout = calculer_cout_portage(r, q, T)
    notionnel = valeur_notionnelle(F0, config.MULTIPLICATEUR)
    sensib = calculer_sensibilites(spot, r, q, T, F0)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class='pricing-card'><h4>📊 Prix Théorique F₀</h4>
            <p class='value' style='color:#1E3A5F;'>{F0:,.2f}</p><p class='sub'>Points d'indice</p></div>""", unsafe_allow_html=True)
    with c2:
        bc = "#10B981" if base['points'] >= 0 else "#EF4444"
        reg = "Contango" if base['points'] >= 0 else "Backwardation"
        st.markdown(f"""<div class='pricing-card' style='border-left-color:{bc};'><h4>📐 Base</h4>
            <p class='value' style='color:{bc};'>{base['points']:+,.2f} pts</p>
            <p class='sub'>{reg} ({base['pct']:+.3f}%)</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='pricing-card' style='border-left-color:#F59E0B;'><h4>💰 Notionnel</h4>
            <p class='value' style='color:#F59E0B;'>{notionnel:,.0f}</p>
            <p class='sub'>MAD (×{config.MULTIPLICATEUR})</p></div>""", unsafe_allow_html=True)

    st.markdown("---")
    cp, cs = st.columns(2)
    with cp:
        st.markdown("#### 🔧 Paramètres")
        st.markdown(f"""<div class='param-box'>
            <strong>S₀</strong> = {spot:,.2f}<br><strong>r</strong> = {r*100:.4f}%<br>
            <strong>q</strong> = {q*100:.4f}%<br><strong>T</strong> = {T:.4f} ({jours_echeance}j/360)<br>
            <strong>r−q</strong> = {(r-q)*100:.4f}%<br><strong>Coût portage</strong> = {cout*100:.4f}%</div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class='param-box' style='margin-top:8px;'>
            <strong>Échéance:</strong> {date_echeance.strftime('%d/%m/%Y')}<br>
            <strong>Prochaine trim.:</strong> {prochaine.strftime('%d/%m/%Y')}</div>""", unsafe_allow_html=True)
    with cs:
        st.markdown("#### 📊 Sensibilités")
        st.markdown(f"""<div class='param-box'><strong>Delta</strong> = {sensib['delta']:.6f}<br>
            <em>Si S₀ +1pt → F₀ +{sensib['delta']:.4f}</em></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class='param-box'><strong>∂F/∂r</strong> = {sensib['sens_r']:.2f} pts/1%<br>
            <em>Si r +1% → F₀ +{sensib['sens_r']:.2f}</em></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class='param-box'><strong>∂F/∂q</strong> = {sensib['sens_q']:.2f} pts/1%<br>
            <em>Si q +1% → F₀ {sensib['sens_q']:.2f}</em></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class='param-box'><strong>Theta</strong> = {sensib['theta_mois']:+.2f} pts/mois</div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📈 Suivi jusqu'à l'Échéance")
    if st.button("🚀 Lancer la simulation", type="primary", key="btn_suivi"):
        dates_s = []
        d = date_calcul
        while d <= date_echeance:
            if d.weekday() < 5:
                dates_s.append(d)
            d += timedelta(days=1)
        res = []
        sp = spot
        np.random.seed(42)
        for i, dt in enumerate(dates_s):
            if i > 0:
                sp *= (1 + np.random.normal(0.0002, 0.008))
            rj = get_taux_zc(dt, date_echeance, st.session_state['df_taux'])
            jr = (date_echeance - dt).days
            Fj = prix_future_theorique(sp, rj, q, max(jr, 1) / 360)
            res.append({'date': dt, 'spot': round(sp, 2), 'F0': round(Fj, 2),
                        'base': round(Fj - sp, 2), 'r': round(rj * 100, 3), 'jours_restants': jr})
        dfs = pd.DataFrame(res)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dfs['date'], y=dfs['F0'], name='F₀', line=dict(color='#1E3A5F', width=2.5)))
        fig.add_trace(go.Scatter(x=dfs['date'], y=dfs['spot'], name='Spot', line=dict(color='#10B981', width=2, dash='dash')))
        fig.update_layout(title="Convergence Spot ↔ Future", height=420, template='plotly_white', hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=dfs['date'], y=dfs['base'],
            marker_color=['#10B981' if b >= 0 else '#EF4444' for b in dfs['base']]))
        fig2.update_layout(title="Base", height=300, template='plotly_white')
        st.plotly_chart(fig2, use_container_width=True)
        with st.expander("📋 Données"):
            st.dataframe(dfs, use_container_width=True)

# ──────────────────────────────────────
# ONGLET 3 — TERM STRUCTURE
# ──────────────────────────────────────
with tab_term:
    if not st.session_state['donnees_valides']:
        st.warning("⚠️ Importez d'abord les données.")
        st.stop()
    st.markdown("### 📊 Structure par Terme")
    spot_ts = st.number_input("Spot S₀", value=1876.54, step=10.0, format="%.2f", key="spot_ts")
    q_ts = st.session_state['q_calculated']
    echeances = [30, 60, 90, 120, 150, 180, 270, 360]
    drt = pd.to_datetime(st.session_state['date_reference'])
    ts = []
    for j in echeances:
        de = drt + timedelta(days=j)
        rj = get_taux_zc(drt, de, st.session_state['df_taux'])
        Fj = prix_future_theorique(spot_ts, rj, q_ts, j / 360)
        bj = Fj - spot_ts
        ts.append({'Jours': j, 'Mois': round(j/30, 1), 'r(%)': round(rj*100, 3),
                   'F₀': round(Fj, 2), 'Base(pts)': round(bj, 2),
                   'Base(%)': round(bj/spot_ts*100, 3), 'Régime': 'Contango' if bj > 0 else 'Backwardation'})
    dfts = pd.DataFrame(ts)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dfts['Jours'], y=dfts['F₀'], name='F₀', mode='lines+markers',
        line=dict(color='#1E3A5F', width=2.5), marker=dict(size=8)))
    fig.add_hline(y=spot_ts, line_dash="dot", line_color="#10B981", annotation_text=f"Spot={spot_ts:,.2f}")
    fig.update_layout(title="Courbe des Prix Futures", height=450, template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(dfts, use_container_width=True, hide_index=True)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=[f"{r['Mois']}M" for _, r in dfts.iterrows()], y=dfts['Base(pts)'],
        marker_color=['#10B981' if b >= 0 else '#EF4444' for b in dfts['Base(pts)']],
        text=[f"{b:+.2f}" for b in dfts['Base(pts)']], textposition='outside'))
    fig2.update_layout(title="Base par Échéance", height=350, template='plotly_white')
    st.plotly_chart(fig2, use_container_width=True)

# ──────────────────────────────────────
# ONGLET 4 — BACKTESTING
# ──────────────────────────────────────
with tab_backtest:
    if not st.session_state['donnees_valides']:
        st.warning("⚠️ Importez d'abord les données.")
        st.stop()
    st.markdown("### 🧪 Backtesting")
    st.caption("Validation de F₀ = S₀ × e^((r−q)×T) sur historique")
    up_h = st.file_uploader("Historique MASI20", type=['csv', 'xlsx'], key="hist_up")
    dfh = charger_historique_masi20(up_h, 90, up_h is None)
    if up_h is None:
        st.caption("🟡 Données mock")
    if dfh is not None and 'prix_future_reel' in dfh.columns:
        rb = get_taux_zc(st.session_state['date_reference'],
            pd.to_datetime(st.session_state['date_reference']) + timedelta(days=90), st.session_state['df_taux'])
        bt = backtesting_complet(dfh, 'spot_masi20', 'prix_future_reel', rb, st.session_state['q_calculated'])
        m1, m2, m3 = st.columns(3)
        cr2 = "#10B981" if bt['r2'] > 0.95 else "#F59E0B" if bt['r2'] > 0.8 else "#EF4444"
        with m1:
            st.markdown(f"""<div class='pricing-card' style='border-left-color:{cr2};text-align:center;'>
                <h4>R²</h4><p class='value' style='color:{cr2};'>{bt['r2']:.4f}</p></div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class='pricing-card' style='text-align:center;'>
                <h4>MAE</h4><p class='value'>{bt['mae']:.2f} pts</p></div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""<div class='pricing-card' style='text-align:center;'>
                <h4>MAPE</h4><p class='value'>{bt['mape']:.3f}%</p></div>""", unsafe_allow_html=True)
        dfbt = bt['df']
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dfbt['date'], y=dfbt['future_reel'], name='Réel', line=dict(color='#1E3A5F', width=2)))
        fig.add_trace(go.Scatter(x=dfbt['date'], y=dfbt['future_theo'], name='Théorique', line=dict(color='#10B981', width=2, dash='dash')))
        fig.update_layout(title="Backtest: Réel vs Théorique", height=420, template='plotly_white', hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=dfbt['date'], y=dfbt['ecart'],
            marker_color=['#10B981' if e >= 0 else '#EF4444' for e in dfbt['ecart']]))
        fig2.update_layout(title="Écarts", height=300, template='plotly_white')
        st.plotly_chart(fig2, use_container_width=True)
        with st.expander("📋 Données"):
            st.dataframe(dfbt, use_container_width=True)
    else:
        st.info("ℹ️ Importez un historique avec `date`, `spot_masi20`, `prix_future_reel`.")

# ──────────────────────────────────────
# ONGLET 5 — ARBITRAGE
# ──────────────────────────────────────
with tab_arb:
    if not st.session_state['donnees_valides']:
        st.warning("⚠️ Importez d'abord les données.")
        st.stop()
    st.markdown("### 🚨 Détection d'Arbitrage")
    st.caption("PDF section 7.2 — Arbitrage sur indices MASI/MASI20")
    with st.expander("📘 Principe", expanded=False):
        st.markdown("""
            **F_marché > F₀** → Surévalué → *Cash-and-Carry* : Vendre Future + Acheter Spot  
            **F_marché < F₀** → Sous-évalué → *Reverse* : Acheter Future + Vendre Spot
        """)
    dca = pd.to_datetime(st.session_state['date_reference'])
    dea = dca + timedelta(days=90)
    ra = get_taux_zc(dca, dea, st.session_state['df_taux'])
    qa = st.session_state['q_calculated']
    F0a = prix_future_theorique(1876.54, ra, qa, 90/360)
    ca1, ca2, ca3 = st.columns(3)
    with ca1:
        pm = st.number_input("Prix Marché", value=round(F0a, 2), step=1.0, format="%.2f")
    with ca2:
        sa = st.slider("Seuil (%)", 0.1, 3.0, 0.5, 0.1)
    with ca3:
        st.markdown(f"<div class='param-box'><strong>F₀</strong> = {F0a:,.2f}</div>", unsafe_allow_html=True)
    arb = detecter_arbitrage(pm, F0a, sa)
    if arb['arbitrage']:
        cls = 'alert-danger' if 'Surévalué' in arb['signal'] else 'alert-success'
        st.markdown(f"""<div class='alert-card {cls}'><h4 style='margin:0 0 8px 0;'>{arb['signal']}</h4>
            <p><strong>Écart:</strong> {arb['ecart_pts']:+.2f} pts ({arb['ecart_pct']:+.3f}%)</p>
            <p><strong>Stratégie:</strong> {arb['strategie']}</p></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class='alert-card alert-info'><h4 style='margin:0;'>{arb['signal']}</h4>
            <p>Écart: {arb['ecart_pct']:+.3f}% (seuil: {sa}%)</p></div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### 📊 Carte d'Arbitrage")
    pr = np.linspace(F0a * 0.97, F0a * 1.03, 50)
    ec = [(p - F0a) / F0a * 100 for p in pr]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=pr, y=ec, marker_color=['#EF4444' if abs(e) > sa else '#10B981' for e in ec]))
    fig.add_hline(y=sa, line_dash="dot", line_color="#EF4444", annotation_text=f"+{sa}%")
    fig.add_hline(y=-sa, line_dash="dot", line_color="#EF4444", annotation_text=f"-{sa}%")
    fig.add_vline(x=F0a, line_dash="dot", line_color="#1E3A5F", annotation_text="F₀")
    fig.update_layout(title="Zone d'Arbitrage", height=380, template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)

render_footer()
