# ============================================
# BOURSE DE CASABLANCA SCRAPER - V0.0.0
# Composition MASI20, Dividendes, Cours
# ============================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from cachetools import TTLCache
import config

cache_masi20 = TTLCache(maxsize=100, ttl=config.CACHE_DURATION['constituents'])

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'fr-FR,fr;q=0.9',
}


def get_masi20_constituents():
    """
    Récupère la composition du MASI20.
    Priorité: 1) Cache → 2) Scraping → 3) Mock
    """
    if 'constituents' in cache_masi20:
        return cache_masi20['constituents']

    data = _scrape_masi20_live()
    if not data:
        data = _get_masi20_mock()

    cache_masi20['constituents'] = data
    return data


def _scrape_masi20_live():
    """Tente de scraper la composition MASI20 depuis la Bourse de Casablanca."""
    try:
        url = "https://www.casablanca-bourse.com/bourseweb/Indices-Composition"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('table')

        if not table:
            return None

        constituents = []
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                try:
                    constituents.append({
                        'ticker': cols[0].text.strip(),
                        'nom': cols[1].text.strip(),
                        'poids': float(cols[2].text.strip().replace('%', '').replace(',', '.')) / 100,
                        'cours': float(cols[3].text.strip().replace(' ', '').replace(',', '.')),
                        'dividende_annuel': 0,
                    })
                except (ValueError, IndexError):
                    continue

        return constituents if constituents else None

    except Exception as e:
        print(f"⚠️ Scraping composition MASI20 échoué: {e}")
        return None


def _get_masi20_mock():
    """
    Composition mock du MASI20 — 20 titres les plus liquides.
    Données approximatives basées sur la composition réelle.
    """
    return [
        {'ticker': 'ATW', 'nom': 'Attijariwafa Bank', 'poids': 0.185, 'cours': 635.0, 'dividende_annuel': 18.0},
        {'ticker': 'BCP', 'nom': 'Banque Centrale Populaire', 'poids': 0.125, 'cours': 315.0, 'dividende_annuel': 8.5},
        {'ticker': 'IAM', 'nom': 'Itissalat Al-Maghrib', 'poids': 0.105, 'cours': 138.0, 'dividende_annuel': 5.4},
        {'ticker': 'BOA', 'nom': 'Bank of Africa', 'poids': 0.075, 'cours': 225.0, 'dividende_annuel': 5.0},
        {'ticker': 'LHM', 'nom': 'LafargeHolcim Maroc', 'poids': 0.065, 'cours': 1850.0, 'dividende_annuel': 110.0},
        {'ticker': 'TQM', 'nom': 'Taqa Morocco', 'poids': 0.055, 'cours': 1180.0, 'dividende_annuel': 68.0},
        {'ticker': 'MNG', 'nom': 'Managem', 'poids': 0.050, 'cours': 2250.0, 'dividende_annuel': 35.0},
        {'ticker': 'CIH', 'nom': 'CIH Bank', 'poids': 0.042, 'cours': 420.0, 'dividende_annuel': 18.0},
        {'ticker': 'CSR', 'nom': 'Cosumar', 'poids': 0.038, 'cours': 195.0, 'dividende_annuel': 8.0},
        {'ticker': 'WAA', 'nom': 'Wafa Assurance', 'poids': 0.035, 'cours': 4950.0, 'dividende_annuel': 140.0},
        {'ticker': 'MRS', 'nom': 'Marsa Maroc', 'poids': 0.032, 'cours': 385.0, 'dividende_annuel': 15.6},
        {'ticker': 'ADH', 'nom': 'Addoha', 'poids': 0.028, 'cours': 42.0, 'dividende_annuel': 1.2},
        {'ticker': 'HPS', 'nom': 'HPS', 'poids': 0.025, 'cours': 7200.0, 'dividende_annuel': 42.0},
        {'ticker': 'SBM', 'nom': 'Société de Boissons du Maroc', 'poids': 0.022, 'cours': 2650.0, 'dividende_annuel': 85.0},
        {'ticker': 'MAB', 'nom': 'Maroc Leasing', 'poids': 0.020, 'cours': 490.0, 'dividende_annuel': 20.0},
        {'ticker': 'LES', 'nom': 'Label Vie', 'poids': 0.020, 'cours': 5400.0, 'dividende_annuel': 72.0},
        {'ticker': 'SOT', 'nom': 'Sothema', 'poids': 0.018, 'cours': 1380.0, 'dividende_annuel': 32.0},
        {'ticker': 'DLM', 'nom': 'Delattre Levivier Maroc', 'poids': 0.015, 'cours': 640.0, 'dividende_annuel': 18.0},
        {'ticker': 'SNP', 'nom': 'Sonasid', 'poids': 0.013, 'cours': 780.0, 'dividende_annuel': 22.0},
        {'ticker': 'RIS', 'nom': 'Risma', 'poids': 0.012, 'cours': 185.0, 'dividende_annuel': 4.0},
    ]


def calculer_taux_dividende_masi20(constituents=None):
    """
    Calcule le taux de dividende de l'indice MASI20.
    Selon la formule: d = Σ(Pi × Di/Ci)

    Args:
        constituents: Liste des constituants (si None, utilise get_masi20_constituents)

    Returns:
        (taux_dividende, df_details)
    """
    if constituents is None:
        constituents = get_masi20_constituents()

    taux_total = 0
    details = []

    for c in constituents:
        poids = c['poids']
        dividende = c.get('dividende_annuel', 0)
        cours = c.get('cours', 1)

        div_yield = dividende / cours if cours > 0 else 0
        contribution = poids * div_yield

        taux_total += contribution

        details.append({
            'Ticker': c['ticker'],
            'Nom': c['nom'],
            'Poids': f"{poids * 100:.2f}%",
            'Cours': f"{cours:,.2f} MAD",
            'Dividende': f"{dividende:,.2f} MAD",
            'Yield': f"{div_yield * 100:.2f}%",
            'Contribution': f"{contribution * 100:.4f}%",
        })

    return taux_total, pd.DataFrame(details)
