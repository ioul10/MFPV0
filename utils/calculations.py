# ============================================
# CALCULATIONS — MASI Futures Pro V0.0.0
# Formules de Pricing conformes au PDF CDG Capital
# et à l'Instruction BAM N° IN-2026-01
#
# Formule centrale : F₀ = S₀ × e^((r - q) × T)
# ============================================

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


# ════════════════════════════════════════════
# 1. PRICING — FORMULE BAM
# ════════════════════════════════════════════

def prix_future_theorique(spot, r, q, T):
    """
    F₀ = S₀ × e^((r − q) × T)

    Args:
        spot (float): Prix spot S₀ de l'indice
        r (float): Taux sans risque (décimal, ex: 0.035 pour 3.5%)
        q (float): Taux de dividende (décimal)
        T (float): Temps à maturité en années (jours/360)

    Returns:
        float: Prix théorique du future F₀
    """
    return spot * np.exp((r - q) * T)


def calculer_base(F0, S0):
    """
    Base = F₀ − S₀
    Contango si Base > 0, Backwardation si Base < 0.
    """
    pts = F0 - S0
    pct = (pts / S0) * 100 if S0 != 0 else 0
    return {'points': pts, 'pct': pct}


def calculer_cout_portage(r, q, T):
    """
    Coût de portage = (r − q) × T
    Représente le coût net de financement moins les dividendes.
    """
    return (r - q) * T


def valeur_notionnelle(prix_future, multiplicateur=10):
    """
    Valeur du contrat = Prix Future × Taille du contrat
    (PDF section 5 : "Valeur du contrat future = Prix future × Taille du contrat")
    """
    return prix_future * multiplicateur


def gain_perte_position(F_cloture, F_ouverture, nb_contrats, multiplicateur=10):
    """
    Gain = (F_clôture − F_ouverture) × Taille du contrat × Nb contrats
    (PDF section 4.2 : formule de gain/perte)

    Positif = gain pour position longue, perte pour position courte.
    """
    return (F_cloture - F_ouverture) * multiplicateur * nb_contrats


# ════════════════════════════════════════════
# 2. TAUX DE DIVIDENDE (q)
# ════════════════════════════════════════════

def calculer_taux_dividende_indice(constituents, date_echeance=None):
    """
    q = Σ(Pᵢ × Dᵢ/Cᵢ)

    Args:
        constituents: list of dicts ou DataFrame avec ticker, poids, cours, dividende_annuel
        date_echeance: datetime optionnel pour filtrer les dividendes ex-date

    Returns:
        (q_total, df_details)
    """
    if isinstance(constituents, pd.DataFrame):
        constituents = constituents.to_dict('records')

    q_total = 0
    details = []

    for c in constituents:
        poids = c.get('poids', 0)
        div = c.get('dividende_annuel', 0)
        cours = c.get('cours', 1)
        date_ex = c.get('prochaine_date_ex', None)

        # Filtrage par date d'échéance
        inclus = True
        if date_echeance is not None and date_ex is not None:
            try:
                if isinstance(date_ex, str):
                    date_ex_dt = pd.to_datetime(date_ex)
                else:
                    date_ex_dt = pd.to_datetime(date_ex)
                if isinstance(date_echeance, str):
                    date_ech_dt = pd.to_datetime(date_echeance)
                else:
                    date_ech_dt = pd.to_datetime(date_echeance)
                inclus = date_ex_dt <= date_ech_dt
            except Exception:
                inclus = True

        div_effectif = div if inclus else 0
        div_yield = div_effectif / cours if cours > 0 else 0
        contribution = poids * div_yield
        q_total += contribution

        details.append({
            'Ticker': c.get('ticker', ''),
            'Nom': c.get('nom', c.get('ticker', '')),
            'Poids': f"{poids * 100:.2f}%",
            'Cours': f"{cours:,.2f}",
            'Dividende': f"{div:,.2f}",
            'Yield': f"{div_yield * 100:.3f}%",
            'Contribution': f"{contribution * 100:.4f}%",
            'Inclus': '✅' if inclus else '❌',
        })

    return q_total, pd.DataFrame(details)


# ════════════════════════════════════════════
# 3. TAUX SANS RISQUE (r) — COURBE ZC
# ════════════════════════════════════════════

def get_taux_zc(date_calcul, date_echeance, df_taux_zc):
    """
    Interpole le taux ZC le plus proche pour une date de calcul et une échéance.

    Args:
        date_calcul: datetime
        date_echeance: datetime
        df_taux_zc: DataFrame [date_spot, date_maturity, zc]

    Returns:
        float: taux en décimal (ex: 0.0285)
    """
    df = df_taux_zc.copy()

    # Normaliser les dates
    df['date_spot'] = pd.to_datetime(df['date_spot'])
    df['date_maturity'] = pd.to_datetime(df['date_maturity'])
    date_calcul = pd.to_datetime(date_calcul)
    date_echeance = pd.to_datetime(date_echeance)

    # Filtrer : taux publiés avant ou le jour du calcul
    df_filtre = df[df['date_spot'] <= date_calcul].copy()
    if df_filtre.empty:
        return 0.03  # fallback

    # Trouver la maturité la plus proche de l'échéance
    df_filtre['ecart'] = abs((df_filtre['date_maturity'] - date_echeance).dt.days)
    meilleure = df_filtre.loc[df_filtre['ecart'].idxmin()]

    taux = float(meilleure['zc'])
    # Si en % (>1), convertir en décimal
    return taux / 100 if taux > 1 else taux


# ════════════════════════════════════════════
# 4. TERM STRUCTURE
# ════════════════════════════════════════════

def calcul_term_structure(spot, r, q, echeances_jours=None):
    """
    Calcule la structure par terme des prix futures.

    Args:
        spot: prix spot
        r: taux sans risque
        q: taux de dividende
        echeances_jours: list d'échéances en jours (défaut: trimestrielles)

    Returns:
        DataFrame avec colonnes Jours, Mois, T, F0, Base_pts, Base_pct, Regime
    """
    if echeances_jours is None:
        echeances_jours = [30, 60, 90, 120, 150, 180, 270, 360]

    results = []
    for j in echeances_jours:
        T = j / 360
        F0 = prix_future_theorique(spot, r, q, T)
        base_pts = F0 - spot
        base_pct = (base_pts / spot) * 100 if spot != 0 else 0
        regime = "Contango" if base_pts > 0 else "Backwardation"

        results.append({
            'Jours': j,
            'Mois': round(j / 30, 1),
            'T (années)': round(T, 4),
            'F₀': round(F0, 2),
            'Base (pts)': round(base_pts, 2),
            'Base (%)': round(base_pct, 3),
            'Régime': regime,
        })

    return pd.DataFrame(results)


# ════════════════════════════════════════════
# 5. SENSIBILITÉS (GRECQUES)
# ════════════════════════════════════════════

def calculer_sensibilites(spot, r, q, T, F0=None):
    """
    Calcule les sensibilités du prix future aux paramètres.

    ∂F/∂r = F₀ × T         (sensibilité au taux)
    ∂F/∂q = −F₀ × T        (sensibilité aux dividendes)
    ∂F/∂T = F₀ × (r − q)   (sensibilité au temps / theta)
    ∂F/∂S = e^((r−q)T)      (delta)

    Returns:
        dict de sensibilités
    """
    if F0 is None:
        F0 = prix_future_theorique(spot, r, q, T)

    delta = np.exp((r - q) * T)

    return {
        'F0': F0,
        'delta': delta,
        'sens_r': F0 * T,               # impact de +1% sur r
        'sens_q': -F0 * T,              # impact de +1% sur q
        'theta_mois': F0 * (r - q) / 12,  # variation par mois
        'gamma': 0,                       # future linéaire → gamma = 0
    }


# ════════════════════════════════════════════
# 6. ARBITRAGE
# ════════════════════════════════════════════

def detecter_arbitrage(prix_marche, prix_theorique, seuil_pct=0.5):
    """
    Détecte les opportunités d'arbitrage (PDF section 7.2).

    Si F_marché > F_théorique : vendre future + acheter spot (cash-and-carry)
    Si F_marché < F_théorique : acheter future + vendre spot (reverse cash-and-carry)

    Args:
        prix_marche: prix observé du future
        prix_theorique: prix théorique F₀
        seuil_pct: seuil en % pour déclencher l'alerte

    Returns:
        dict avec signal, stratégie, écart
    """
    ecart = prix_marche - prix_theorique
    ecart_pct = (ecart / prix_theorique) * 100 if prix_theorique != 0 else 0

    if abs(ecart_pct) > seuil_pct:
        if ecart > 0:
            return {
                'signal': '🔴 Surévalué',
                'strategie': 'Cash-and-Carry : Vendre Future + Acheter Spot',
                'ecart_pts': round(ecart, 2),
                'ecart_pct': round(ecart_pct, 3),
                'arbitrage': True,
            }
        else:
            return {
                'signal': '🟢 Sous-évalué',
                'strategie': 'Reverse Cash-and-Carry : Acheter Future + Vendre Spot',
                'ecart_pts': round(ecart, 2),
                'ecart_pct': round(ecart_pct, 3),
                'arbitrage': True,
            }
    else:
        return {
            'signal': '⚖️ Équilibre',
            'strategie': 'Aucune opportunité significative',
            'ecart_pts': round(ecart, 2),
            'ecart_pct': round(ecart_pct, 3),
            'arbitrage': False,
        }


# ════════════════════════════════════════════
# 7. BACKTESTING
# ════════════════════════════════════════════

def calculer_mae(y_reel, y_pred):
    """Mean Absolute Error."""
    return float(np.mean(np.abs(np.array(y_reel) - np.array(y_pred))))


def calculer_mape(y_reel, y_pred):
    """Mean Absolute Percentage Error (%)."""
    y_r, y_p = np.array(y_reel), np.array(y_pred)
    mask = y_r != 0
    if mask.sum() == 0:
        return 0
    return float(np.mean(np.abs((y_r[mask] - y_p[mask]) / y_r[mask])) * 100)


def calculer_r2(y_reel, y_pred):
    """Coefficient de détermination R²."""
    y_r, y_p = np.array(y_reel), np.array(y_pred)
    ss_res = np.sum((y_r - y_p) ** 2)
    ss_tot = np.sum((y_r - np.mean(y_r)) ** 2)
    return float(1 - (ss_res / ss_tot)) if ss_tot != 0 else 0


def backtesting_complet(df_donnees, col_spot, col_future_reel, r, q, col_date='date', echeance_jours=90):
    """
    Backtesting du modèle sur données historiques.

    Pour chaque jour, calcule F₀ théorique et compare au prix réel.

    Returns:
        dict avec métriques (mae, mape, r2) et DataFrame détaillé
    """
    resultats = []

    for idx, row in df_donnees.iterrows():
        spot = row[col_spot]
        future_reel = row[col_future_reel]
        jours_restants = max(echeance_jours - idx, 1)
        T = jours_restants / 360

        F0 = prix_future_theorique(spot, r, q, T)

        resultats.append({
            'date': row.get(col_date, idx),
            'spot': round(spot, 2),
            'future_reel': round(future_reel, 2),
            'future_theo': round(F0, 2),
            'ecart': round(F0 - future_reel, 2),
            'ecart_pct': round((F0 - future_reel) / future_reel * 100, 3) if future_reel != 0 else 0,
            'jours_restants': jours_restants,
        })

    df = pd.DataFrame(resultats)

    return {
        'mae': calculer_mae(df['future_reel'], df['future_theo']),
        'mape': calculer_mape(df['future_reel'], df['future_theo']),
        'r2': calculer_r2(df['future_reel'], df['future_theo']),
        'df': df,
    }


# ════════════════════════════════════════════
# 8. COUVERTURE — N* (PDF section 6)
# ════════════════════════════════════════════

def calculer_N_star(beta, valeur_portefeuille, prix_future, multiplicateur=10):
    """
    N* = β × P / A
    où A = Prix Future × Multiplicateur (valeur notionnelle)

    (PDF section 6.2)
    """
    A = prix_future * multiplicateur
    if A == 0:
        return 0
    return round(beta * valeur_portefeuille / A)


def calculer_beta(rendements_ptf, rendements_benchmark):
    """β = Cov(Rp, Rb) / Var(Rb)"""
    cov = np.cov(rendements_ptf, rendements_benchmark)[0, 1]
    var = np.var(rendements_benchmark, ddof=1)
    return cov / var if var != 0 else 1.0


# ════════════════════════════════════════════
# 9. UTILITAIRES
# ════════════════════════════════════════════

def jours_vers_annees(jours, base=360):
    """Convention BAM : base 360."""
    return jours / base


def prochaine_echeance_trimestrielle(date_ref=None):
    """
    Retourne la prochaine échéance trimestrielle (Mars, Juin, Sept, Déc).
    Dernier vendredi du mois d'échéance.
    """
    if date_ref is None:
        date_ref = datetime.now()

    mois_echeances = [3, 6, 9, 12]

    for m in mois_echeances:
        year = date_ref.year if m >= date_ref.month else date_ref.year + 1
        # Dernier jour du mois
        if m == 12:
            dernier_jour = datetime(year, 12, 31)
        else:
            dernier_jour = datetime(year, m + 1, 1) - timedelta(days=1)

        # Reculer jusqu'au vendredi
        while dernier_jour.weekday() != 4:  # 4 = vendredi
            dernier_jour -= timedelta(days=1)

        if dernier_jour > date_ref:
            return dernier_jour

    # Fallback : mars de l'année suivante
    return datetime(date_ref.year + 1, 3, 27)
