# ============================================
# APP.PY - MASI Futures Pro V0.0.0
# Page d'accueil principale
# ============================================

import streamlit as st
import streamlit.components.v1 as components
import config
from components.sidebar import render_sidebar
from components.header import render_header
from components.footer import render_footer
from components.styles import inject_global_css
from utils.scraping import update_statut_connexions
from datetime import datetime

# ── Configuration Streamlit (TOUJOURS EN PREMIER) ──
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Global ──
inject_global_css()

# ── Bandeau Développement ──
st.markdown(f"""
    <div class='dev-banner'>
        <div style='display:flex; align-items:center; gap:15px; flex-wrap:wrap;'>
            <div style='font-size:2.2em;'>🚧</div>
            <div style='flex:1;'>
                <h3 style='margin:0; color:#92400e;'>⚠️ Application en Développement</h3>
                <p style='margin:8px 0 0 0; color:#78350f; line-height:1.6; font-size:0.95em;'>
                    Cette application est en <strong>phase de développement</strong>. 
                    Les données affichées sont simulées ou issues de scraping non garanti.
                </p>
                <p style='margin:8px 0 0 0; color:#78350f; font-size:0.85em;'>
                    📅 <strong>Version :</strong> v{config.APP_VERSION}
                    &nbsp;|&nbsp; 🎯 <strong>Statut :</strong> Structure V0 — Module News
                </p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.divider()

# ── Initialisation ──
update_statut_connexions()
render_sidebar()
render_header()

# ── Horloge dynamique ──
horloge_html = """
<div style='padding: 18px 22px; background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%); 
            border-radius: 12px; margin-bottom: 20px; 
            border-left: 5px solid #1E3A5F;
            box-shadow: 0 3px 10px rgba(30,58,95,0.08);'>
    <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
        <div style='flex: 1; min-width: 180px;'>
            <p style='margin: 0; font-size: 0.8em; color: #6B7280; text-transform: uppercase; letter-spacing: 1px;'>
                📅 Date
            </p>
            <p id='date' style='margin: 4px 0 0 0; font-size: 1.15em; font-weight: 600; color: #1E3A5F;'>
                --/--/----
            </p>
        </div>
        <div style='flex: 1; min-width: 180px; text-align: center;'>
            <p style='margin: 0; font-size: 0.8em; color: #6B7280; text-transform: uppercase; letter-spacing: 1px;'>
                🕐 Heure
            </p>
            <p id='time' style='margin: 4px 0 0 0; font-size: 2.2em; font-weight: 700; 
                               color: #1E3A5F; font-family: monospace; letter-spacing: 2px;'>
                --:--:--
            </p>
        </div>
        <div style='flex: 1; min-width: 180px; text-align: right;'>
            <p style='margin: 0; font-size: 0.8em; color: #6B7280; text-transform: uppercase; letter-spacing: 1px;'>
                📊 Marché
            </p>
            <p id='status' style='margin: 8px 0 0 0; font-size: 1.1em; font-weight: 600; color: #6B7280;'>
                ○ Vérification...
            </p>
            <p id='next-session' style='margin: 4px 0 0 0; font-size: 0.8em; color: #9CA3AF;'>--</p>
        </div>
    </div>
    <div style='margin-top: 12px; background: #e5e7eb; border-radius: 10px; height: 6px; overflow: hidden;'>
        <div id='progress-bar' style='width: 0%; height: 100%; 
                                      background: linear-gradient(90deg, #10B981, #34D399);
                                      transition: width 1s ease;'></div>
    </div>
</div>

<script>
function updateClock() {
    const now = new Date();
    document.getElementById('date').textContent = now.toLocaleDateString('fr-FR', { 
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
    });
    document.getElementById('time').textContent = now.toLocaleTimeString('fr-FR', { 
        hour: '2-digit', minute: '2-digit', second: '2-digit' 
    });
    
    const day = now.getDay();
    const hour = now.getHours() + now.getMinutes() / 60;
    const statusEl = document.getElementById('status');
    const nextEl = document.getElementById('next-session');
    const bar = document.getElementById('progress-bar');
    
    if (day >= 1 && day <= 5) {
        if (hour >= 10 && hour < 15.5) {
            statusEl.innerHTML = '● Marché Ouvert';
            statusEl.style.color = '#10B981';
            bar.style.width = ((hour - 10) / 5.5 * 100) + '%';
            nextEl.textContent = 'Fermeture dans ' + Math.ceil(15.5 - hour) + 'h';
        } else if (hour < 10) {
            statusEl.innerHTML = '○ Pré-ouverture';
            statusEl.style.color = '#F59E0B';
            bar.style.width = '0%';
            nextEl.textContent = 'Ouverture dans ' + (10 - hour).toFixed(1) + 'h';
        } else {
            statusEl.innerHTML = '○ Marché Fermé';
            statusEl.style.color = '#6B7280';
            bar.style.width = '100%';
            bar.style.background = 'linear-gradient(90deg, #6B7280, #9CA3AF)';
            nextEl.textContent = 'Prochaine séance demain 10h00';
        }
    } else {
        statusEl.innerHTML = '○ Week-end';
        statusEl.style.color = '#6B7280';
        bar.style.width = '0%';
        const mon = new Date(now);
        mon.setDate(now.getDate() + (1 - now.getDay() + 7) % 7 || 7);
        nextEl.textContent = 'Reprise lundi à 10h00';
    }
}
updateClock();
setInterval(updateClock, 1000);
</script>
"""
components.html(horloge_html, height=165)

# ── Titre ──
st.title(f"Bienvenue sur {config.APP_NAME}")

# ── Objectif ──
st.markdown(f"""
    <div style='padding: 28px; background: linear-gradient(135deg, {config.COLORS["card"]} 0%, #f8fafc 100%); 
                border-radius: 14px; margin: 15px 0; box-shadow: 0 3px 10px rgba(0,0,0,0.06);'>
        <h2 style='color: {config.COLORS["primary"]}; margin-top: 0; font-size: 1.4em;'>🎯 Objectif de l'Application</h2>
        <p style='font-size: 1.05em; line-height: 1.8; margin-bottom: 12px;'>
            <strong>{config.APP_NAME}</strong> est une plateforme professionnelle de pricing des contrats futures 
            sur les indices <strong>MASI</strong> et <strong>MASI20</strong> de la Bourse de Casablanca.
        </p>
        <p style='font-size: 1.05em; line-height: 1.8; margin-bottom: 0;'>
            Conforme à l'<strong>Instruction BAM N° IN-2026-01</strong>, cette application permet de calculer 
            le prix théorique des futures (F₀ = S₀·e<sup>(r-q)·T</sup>), d'analyser les opportunités d'arbitrage, 
            de gérer la couverture de portefeuille et de suivre les risques en temps réel.
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# ── Résumé BAM ──
with st.expander("📚 Instruction BAM N° IN-2026-01 — Résumé"):
    st.markdown("""
        ### 📐 Formule du Cours Théorique
        
        **F₀ = S₀ × e^((r - q) × T)**
        
        | Variable | Signification | Source |
        |----------|---------------|--------|
        | **S₀** | Prix spot de l'indice | Bourse de Casablanca |
        | **r** | Taux sans risque | BKAM (Bons du Trésor) |
        | **q** | Taux de dividende | Calculé selon composition MASI20 |
        | **T** | Temps à maturité (jours/360) | Selon échéance du contrat |
        
        ### 📋 Hiérarchie des Cours de Clôture
        
        1. **Cours du fixing** (priorité)
        2. **Dernier cours traité** (si pas de fixing)
        3. **Cours théorique** (si aucun cours traité)
        
        ### 📊 Caractéristiques du Contrat
        
        | Paramètre | Valeur |
        |-----------|--------|
        | Sous-jacent | MASI20 (composition revue annuellement) |
        | Multiplicateur | 10 MAD par point d'indice |
        | Pas de cotation | 0,1 point (≡ 1 MAD) |
        | Échéances | Trimestrielles (Mars, Juin, Sept, Déc) |
        | Dénouement | Cash settlement |
        | Dépôt de garantie | 1 000 MAD (révisable) |
    """)

st.divider()

# ── Accès rapide ──
st.markdown("### 🚀 Accès Rapide")

col1, col2, col3, col4 = st.columns(4)

pages_info = [
    (col1, "📰", "News & Indices", "Niveaux MASI/MASI20, Évolution, Statistiques, Actualités", config.COLORS['success']),
    (col2, "🧮", "Pricing", "Prix théorique F₀, Term Structure, Arbitrage", config.COLORS['primary']),
    (col3, "📊", "Suivi Risques", "VaR, P&L, Marges, Alertes, Stress Testing", config.COLORS['warning']),
    (col4, "🛡️", "Couverture", "Hedging, Bêta, Nombre de contrats N*", config.COLORS['info']),
]

for col, icon, title, desc, color in pages_info:
    with col:
        st.markdown(f"""
            <div class='metric-card' style='border-top: 4px solid {color}; text-align:center; min-height:180px;'>
                <div style='font-size: 2.5em; margin-bottom: 8px;'>{icon}</div>
                <h4 style='margin: 0 0 8px 0; color: {config.COLORS["primary"]}; font-size:1em;'>{title}</h4>
                <p style='color: {config.COLORS["text_muted"]}; margin: 0; font-size: 0.82em; line-height:1.5;'>
                    {desc}
                </p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("")

col_b1, col_b2 = st.columns(2)
with col_b1:
    if st.button("📰 Accéder aux News & Indices", use_container_width=True, type="primary"):
        st.switch_page("pages/01_News.py")
with col_b2:
    if st.button("🧮 Accéder au Module de Pricing", use_container_width=True):
        st.switch_page("pages/02_Pricing.py")

# ── Footer ──
render_footer()
