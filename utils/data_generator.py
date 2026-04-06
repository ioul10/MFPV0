# ============================================
# DATA GENERATOR - MASI Futures Pro V0.0.0
# Génération de données historiques simulées
# ============================================

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generer_donnees_historiques(nom_indice, niveau_actuel, jours=90):
    """
    Génère des données OHLC historiques simulées pour un indice.

    Args:
        nom_indice: 'MASI' ou 'MASI20'
        niveau_actuel: niveau spot actuel
        jours: nombre de jours

    Returns:
        dict avec dates, prices, opens, highs, lows, volumes, returns
    """
    seed = 42 if nom_indice == 'MASI' else 43
    np.random.seed(seed)

    dates = [datetime.now() - timedelta(days=i) for i in range(jours)]
    dates.reverse()

    # Simuler des rendements log-normaux
    mu = 0.0002          # drift léger positif
    sigma = 0.012 if nom_indice == 'MASI' else 0.015  # MASI20 plus volatile (moins de titres)

    returns = np.random.normal(mu, sigma, jours)
    prices = niveau_actuel * np.exp(np.cumsum(returns))
    # Calibrer pour que le dernier prix = niveau_actuel
    prices = prices * (niveau_actuel / prices[-1])

    # Générer OHLC
    opens = prices * (1 + np.random.uniform(-0.004, 0.004, jours))
    highs = np.maximum(opens, prices) * (1 + np.random.uniform(0.001, 0.008, jours))
    lows = np.minimum(opens, prices) * (1 - np.random.uniform(0.001, 0.008, jours))

    # Volumes simulés
    base_volume = 50_000_000 if nom_indice == 'MASI' else 15_000_000
    volumes = np.random.lognormal(np.log(base_volume), 0.4, jours).astype(int)

    return {
        'dates': dates,
        'prices': prices,
        'opens': opens,
        'highs': highs,
        'lows': lows,
        'volumes': volumes,
        'returns': np.diff(prices) / prices[:-1],
    }


def calculer_statistiques(donnees):
    """
    Calcule les statistiques descriptives pour un indice.

    Args:
        donnees: dict retourné par generer_donnees_historiques

    Returns:
        dict de statistiques
    """
    prices = donnees['prices']
    returns = donnees['returns']

    return {
        'prix_minimum': float(np.min(prices)),
        'prix_maximum': float(np.max(prices)),
        'moyenne': float(np.mean(prices)),
        'mediane': float(np.median(prices)),
        'amplitude': float(np.max(prices) - np.min(prices)),
        'performance_cumulee': float(((prices[-1] - prices[0]) / prices[0]) * 100),
        'volatilite_quotidienne': float(np.std(returns) * 100),
        'volatilite_annualisee': float(np.std(returns) * np.sqrt(252) * 100),
        'rendement_minimum': float(np.min(returns) * 100),
        'rendement_maximum': float(np.max(returns) * 100),
        'etendu_rendements': float((np.max(returns) - np.min(returns)) * 100),
        'skewness': float(pd.Series(returns).skew()),
        'kurtosis': float(pd.Series(returns).kurtosis()),
    }


def build_ohlc_dataframe(donnees):
    """Construit un DataFrame OHLC formaté à partir des données historiques."""
    df = pd.DataFrame({
        'Date': [d.strftime('%d/%m/%Y') for d in donnees['dates']],
        'Open': donnees['opens'],
        'High': donnees['highs'],
        'Low': donnees['lows'],
        'Close': donnees['prices'],
        'Volume': donnees['volumes'],
        'Change %': np.concatenate([[0], np.diff(donnees['prices']) / donnees['prices'][:-1] * 100]),
    })
    return df


def build_stats_dataframe(stats):
    """Construit un DataFrame des statistiques formaté."""
    return pd.DataFrame({
        'Statistique': [
            'Prix Minimum', 'Prix Maximum', 'Prix Moyen', 'Médiane', 'Amplitude',
            'Performance Cumulée', 'Volatilité Quotidienne', 'Volatilité Annualisée',
            'Rendement Min', 'Rendement Max', 'Étendu Rendements',
            'Skewness', 'Kurtosis',
        ],
        'Valeur': [
            f"{stats['prix_minimum']:,.2f}",
            f"{stats['prix_maximum']:,.2f}",
            f"{stats['moyenne']:,.2f}",
            f"{stats['mediane']:,.2f}",
            f"{stats['amplitude']:,.2f}",
            f"{stats['performance_cumulee']:+.2f}%",
            f"{stats['volatilite_quotidienne']:.2f}%",
            f"{stats['volatilite_annualisee']:.2f}%",
            f"{stats['rendement_minimum']:+.2f}%",
            f"{stats['rendement_maximum']:+.2f}%",
            f"{stats['etendu_rendements']:.2f}%",
            f"{stats['skewness']:.4f}",
            f"{stats['kurtosis']:.4f}",
        ],
    })


def build_comparison_dataframe(stats_masi, stats_masi20):
    """Construit un DataFrame comparatif MASI vs MASI20."""
    keys = [
        ('Prix Minimum', 'prix_minimum', ':,.2f'),
        ('Prix Maximum', 'prix_maximum', ':,.2f'),
        ('Moyenne', 'moyenne', ':,.2f'),
        ('Médiane', 'mediane', ':,.2f'),
        ('Performance Cumulée', 'performance_cumulee', ':+.2f'),
        ('Volatilité Annualisée', 'volatilite_annualisee', ':.2f'),
        ('Rendement Max', 'rendement_maximum', ':+.2f'),
        ('Rendement Min', 'rendement_minimum', ':+.2f'),
        ('Skewness', 'skewness', ':.4f'),
        ('Kurtosis', 'kurtosis', ':.4f'),
    ]

    rows = []
    for label, key, fmt in keys:
        v1 = stats_masi[key]
        v2 = stats_masi20[key]
        suffix = '%' if 'cumulee' in key or 'volatilite' in key or 'rendement' in key else ''
        rows.append({
            'Statistique': label,
            'MASI': format(v1, fmt.lstrip(':')) + suffix,
            'MASI20': format(v2, fmt.lstrip(':')) + suffix,
        })

    return pd.DataFrame(rows)
