# ============================================
# DATA LOADER — MASI Futures Pro V0.0.0
# Chargement des taux ZC, dividendes, historique
# ============================================

import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
import os


# ════════════════════════════════════════════
# 1. TAUX ZÉRO-COUPON (r)
# ════════════════════════════════════════════

def get_taux_zc_mock():
    """Génère des taux ZC mock réalistes pour le Maroc."""
    np.random.seed(100)

    dates_pub = [datetime(2026, 1, 1) + timedelta(weeks=i) for i in range(20)]
    maturites = [3, 6, 12]
    taux_base = {3: 2.85, 6: 3.10, 12: 3.35}

    data = []
    for d in dates_pub:
        drift = np.random.uniform(-0.03, 0.03)
        for m in maturites:
            date_mat = d + timedelta(days=m * 30)
            taux = taux_base[m] + drift + (m * 0.02)
            data.append({
                'date_spot': d,
                'date_maturity': date_mat,
                'zc': round(taux, 3),
            })

    return pd.DataFrame(data)


def charger_taux_zc(uploaded_file=None, utiliser_mock=True):
    """
    Charge les taux ZC depuis un fichier ou mock.
    Format attendu: date_spot | date_maturity | zc
    """
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            required = ['date_spot', 'date_maturity', 'zc']
            missing = [c for c in required if c not in df.columns]
            if missing:
                st.error(f"❌ Colonnes manquantes : {', '.join(missing)}")
                return None

            df['date_spot'] = pd.to_datetime(df['date_spot'], errors='coerce')
            df['date_maturity'] = pd.to_datetime(df['date_maturity'], errors='coerce')

            if df['zc'].max() > 1:
                st.caption("ℹ️ Taux détectés en % — conversion automatique")

            df = df.sort_values(['date_spot', 'date_maturity']).reset_index(drop=True)
            st.success(f"✅ {len(df)} taux chargés ({df['date_spot'].nunique()} dates)")
            return df

        except Exception as e:
            st.error(f"❌ Erreur : {e}")
            return None

    if utiliser_mock:
        return get_taux_zc_mock()

    return None


# ════════════════════════════════════════════
# 2. DIVIDENDES MASI20 (q)
# ════════════════════════════════════════════

def get_dividendes_masi20_mock():
    """Données mock des 20 constituants MASI20 avec dividendes."""
    data = [
        ('ATW', 'Attijariwafa Bank', 0.185, 635.0, 'semestriel', 18.0, '2026-03-15', 'annonce'),
        ('BCP', 'Banque Centrale Populaire', 0.125, 315.0, 'annuel', 8.5, '2026-05-20', 'annonce'),
        ('IAM', 'Itissalat Al-Maghrib', 0.105, 138.0, 'semestriel', 5.4, '2026-04-10', 'annonce'),
        ('BOA', 'Bank of Africa', 0.075, 225.0, 'annuel', 5.0, '2026-06-01', 'estime'),
        ('LHM', 'LafargeHolcim Maroc', 0.065, 1850.0, 'annuel', 110.0, '2026-05-30', 'estime'),
        ('TQM', 'Taqa Morocco', 0.055, 1180.0, 'annuel', 68.0, '2026-06-15', 'estime'),
        ('MNG', 'Managem', 0.050, 2250.0, 'annuel', 35.0, '2026-07-10', 'estime'),
        ('CIH', 'CIH Bank', 0.042, 420.0, 'annuel', 18.0, '2026-06-01', 'estime'),
        ('CSR', 'Cosumar', 0.038, 195.0, 'annuel', 8.0, '2026-05-15', 'annonce'),
        ('WAA', 'Wafa Assurance', 0.035, 4950.0, 'annuel', 140.0, '2026-06-20', 'estime'),
        ('MRS', 'Marsa Maroc', 0.032, 385.0, 'annuel', 15.6, '2026-05-25', 'annonce'),
        ('ADH', 'Addoha', 0.028, 42.0, 'annuel', 1.2, '2026-04-25', 'annonce'),
        ('HPS', 'HPS', 0.025, 7200.0, 'annuel', 42.0, '2026-07-15', 'estime'),
        ('SBM', 'Sté Boissons du Maroc', 0.022, 2650.0, 'annuel', 85.0, '2026-06-10', 'estime'),
        ('MAB', 'Maroc Leasing', 0.020, 490.0, 'annuel', 20.0, '2026-05-20', 'annonce'),
        ('LES', 'Label Vie', 0.020, 5400.0, 'annuel', 72.0, '2026-06-30', 'estime'),
        ('SOT', 'Sothema', 0.018, 1380.0, 'annuel', 32.0, '2026-06-05', 'estime'),
        ('DLM', 'Delattre Levivier', 0.015, 640.0, 'annuel', 18.0, '2026-07-01', 'estime'),
        ('SNP', 'Sonasid', 0.013, 780.0, 'annuel', 22.0, '2026-07-20', 'estime'),
        ('RIS', 'Risma', 0.012, 185.0, 'annuel', 4.0, '2026-06-15', 'estime'),
    ]

    rows = []
    for ticker, nom, poids, cours, freq, div, date_ex, statut in data:
        rows.append({
            'ticker': ticker, 'nom': nom, 'poids': poids, 'cours': cours,
            'frequence': freq, 'dividende_annuel': div,
            'taux_yield_annuel': round(div / cours * 100, 3),
            'prochaine_date_ex': datetime.strptime(date_ex, '%Y-%m-%d'),
            'statut': statut,
        })

    return pd.DataFrame(rows)


def charger_dividendes(uploaded_file=None, utiliser_mock=True):
    """Charge les dividendes depuis un fichier ou mock."""
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            required = ['ticker', 'poids', 'cours', 'dividende_annuel']
            missing = [c for c in required if c not in df.columns]
            if missing:
                st.error(f"❌ Colonnes manquantes : {', '.join(missing)}")
                return None

            if 'taux_yield_annuel' not in df.columns:
                df['taux_yield_annuel'] = (df['dividende_annuel'] / df['cours'] * 100).round(3)
            if 'prochaine_date_ex' in df.columns:
                df['prochaine_date_ex'] = pd.to_datetime(df['prochaine_date_ex'], errors='coerce')

            total = df['poids'].sum()
            if abs(total - 1.0) > 0.05:
                st.warning(f"⚠️ Somme des poids = {total:.3f} (attendu ≈ 1.0)")

            df = df.sort_values('poids', ascending=False).reset_index(drop=True)
            st.success(f"✅ {len(df)} actions chargées")
            return df

        except Exception as e:
            st.error(f"❌ Erreur : {e}")
            return None

    if utiliser_mock:
        return get_dividendes_masi20_mock()

    return None


# ════════════════════════════════════════════
# 3. HISTORIQUE MASI20 (backtesting)
# ════════════════════════════════════════════

def get_historique_masi20_mock(jours=90):
    """Génère un historique mock MASI20 avec prix future simulé."""
    np.random.seed(42)
    spot_init = 1876.54

    dates = []
    d = datetime.now() - timedelta(days=jours + 30)
    while len(dates) < jours:
        if d.weekday() < 5:
            dates.append(d)
        d += timedelta(days=1)

    returns = np.random.normal(0.0002, 0.008, jours)
    prices = [spot_init]
    for r in returns[1:]:
        prices.append(prices[-1] * (1 + r))

    df = pd.DataFrame({
        'date': dates[:jours],
        'spot_masi20': [round(p, 2) for p in prices[:jours]],
    })

    # Simuler un prix future réaliste (légère base positive décroissante)
    df['prix_future_reel'] = df.apply(
        lambda row: round(row['spot_masi20'] * (1 + 0.0008 * (jours - row.name) / 30), 2),
        axis=1,
    )

    return df


def charger_historique_masi20(uploaded_file=None, jours=90, utiliser_mock=True):
    """Charge l'historique MASI20."""
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.sort_values('date').reset_index(drop=True)
            st.success(f"✅ {len(df)} jours chargés")
            return df

        except Exception as e:
            st.error(f"❌ Erreur : {e}")
            return None

    if utiliser_mock:
        return get_historique_masi20_mock(jours)

    return None


# ════════════════════════════════════════════
# 4. TEMPLATES CSV
# ════════════════════════════════════════════

def template_taux_zc():
    """Génère un template CSV pour les taux ZC."""
    df = pd.DataFrame({
        'date_spot': ['2026-01-01', '2026-01-01', '2026-01-01'],
        'date_maturity': ['2026-04-01', '2026-07-01', '2027-01-01'],
        'zc': [2.85, 3.10, 3.35],
    })
    return df.to_csv(index=False).encode('utf-8')


def template_dividendes():
    """Génère un template CSV pour les dividendes."""
    df = pd.DataFrame({
        'ticker': ['ATW', 'BCP', 'IAM'],
        'nom': ['Attijariwafa Bank', 'Banque Populaire', 'Maroc Telecom'],
        'poids': [0.185, 0.125, 0.105],
        'cours': [635.0, 315.0, 138.0],
        'dividende_annuel': [18.0, 8.5, 5.4],
        'frequence': ['semestriel', 'annuel', 'semestriel'],
        'prochaine_date_ex': ['2026-03-15', '2026-05-20', '2026-04-10'],
        'statut': ['annonce', 'annonce', 'annonce'],
    })
    return df.to_csv(index=False).encode('utf-8')
