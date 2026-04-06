# ============================================
# SCRAPING - MASI Futures Pro V0.0.0
# Sources: Bourse de Casablanca, BKAM
# ============================================

import json
import os
import random
from datetime import datetime, timedelta
from cachetools import TTLCache
import config

CACHE_DIR = "data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)

cache_indices = TTLCache(maxsize=100, ttl=config.CACHE_DURATION['indices'])
cache_bkam = TTLCache(maxsize=100, ttl=config.CACHE_DURATION['bkam_rates'])

# ────────────────────────────────────────────
# INDICES MASI / MASI20
# ────────────────────────────────────────────

def _scrape_indices_live():
    """
    Tente de scraper les indices en temps réel depuis la Bourse de Casablanca.
    Returns: dict ou None si échec
    """
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        }

        url = "https://www.casablanca-bourse.com/bourseweb/Cours-Indices.aspx"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        data = {}
        table = soup.find('table', {'class': 'table'})
        if table:
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    nom = cols[0].text.strip().upper()
                    if nom in ('MASI', 'MASI20', 'MASI 20'):
                        key = 'MASI20' if '20' in nom else 'MASI'
                        try:
                            niveau = float(cols[1].text.strip().replace(' ', '').replace(',', '.'))
                            variation_str = cols[2].text.strip().replace(',', '.')
                            data[key] = {
                                'nom': key,
                                'niveau': niveau,
                                'variation': variation_str if variation_str.startswith(('+', '-')) else f"+{variation_str}",
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'source': 'live',
                            }
                        except (ValueError, IndexError):
                            continue

        return data if data else None

    except Exception as e:
        print(f"⚠️ Scraping live échoué: {e}")
        return None


def _load_cached_indices():
    """Charge les dernières données depuis le cache fichier."""
    cache_file = os.path.join(CACHE_DIR, "indices_cache.json")
    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            return cached.get('indices', None)
    except Exception:
        pass
    return None


def _generate_mock_indices():
    """
    Génère des données mock réalistes.
    Clairement marquées comme [MOCK] dans le timestamp.
    """
    return {
        'MASI': {
            'nom': 'MASI',
            'niveau': round(16500 + random.uniform(-200, 200), 2),
            'variation': f"{random.uniform(-1.5, 1.5):+.2f}%",
            'timestamp': f"[MOCK] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            'source': 'mock',
        },
        'MASI20': {
            'nom': 'MASI20',
            'niveau': round(1870 + random.uniform(-30, 30), 2),
            'variation': f"{random.uniform(-1.5, 1.5):+.2f}%",
            'timestamp': f"[MOCK] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            'source': 'mock',
        }
    }


def _save_indices_cache(data):
    """Sauvegarde les indices dans le cache fichier."""
    cache_file = os.path.join(CACHE_DIR, "indices_cache.json")
    try:
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'indices': data,
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def get_indices_bourse(force_refresh=False):
    """
    Récupère les niveaux MASI et MASI20.
    Priorité: 1) Cache mémoire → 2) Scraping live → 3) Cache fichier → 4) Mock
    """
    if not force_refresh and 'indices_data' in cache_indices:
        return cache_indices['indices_data']

    # Essayer le scraping live
    data = _scrape_indices_live()

    # Fallback: cache fichier
    if not data:
        data = _load_cached_indices()

    # Fallback: mock
    if not data:
        data = _generate_mock_indices()

    cache_indices['indices_data'] = data
    _save_indices_cache(data)

    return data


def get_spot_indice(indice='MASI', force_refresh=False):
    """Récupère le niveau spot d'un indice spécifique."""
    data = get_indices_bourse(force_refresh)
    if data and indice in data:
        return data[indice]['niveau']
    # Fallback réaliste
    return 16500.0 if indice == 'MASI' else 1870.0


# ────────────────────────────────────────────
# TAUX BKAM
# ────────────────────────────────────────────

def _scrape_taux_bkam():
    """Tente de scraper les taux depuis BKAM."""
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }

        url = "https://www.bkam.ma/Marches/Principaux-indicateurs/Marche-obligataire/Marche-des-bons-de-tresor/Marche-secondaire/Taux-de-reference-des-bons-du-tresor"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        # Tenter d'extraire les taux depuis le tableau BKAM
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            taux = {}
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    label = cols[0].text.strip().lower()
                    try:
                        val = float(cols[1].text.strip().replace('%', '').replace(',', '.')) / 100
                        if '10' in label or 'dix' in label:
                            taux['taux_10ans'] = val
                        elif '5' in label or 'cinq' in label:
                            taux['taux_5ans'] = val
                        elif '1' in label or 'an' in label:
                            taux['taux_1an'] = val
                    except ValueError:
                        continue

            if taux:
                taux['date'] = datetime.now().strftime('%Y-%m-%d')
                taux['source'] = 'BKAM (live)'
                return taux

        return None

    except Exception as e:
        print(f"⚠️ Scraping BKAM échoué: {e}")
        return None


def _get_mock_taux():
    """Taux mock réalistes pour le Maroc."""
    return {
        'taux_10ans': 0.035,
        'taux_5ans': 0.030,
        'taux_2ans': 0.027,
        'taux_1an': 0.025,
        'taux_6mois': 0.023,
        'taux_3mois': 0.022,
        'date': f"[MOCK] {datetime.now().strftime('%Y-%m-%d')}",
        'source': 'mock',
    }


def get_taux_bkam(force_refresh=False):
    """
    Récupère les taux de référence BKAM.
    Priorité: 1) Cache mémoire → 2) Scraping → 3) Mock
    """
    if not force_refresh and 'bkam_rates' in cache_bkam:
        return cache_bkam['bkam_rates']

    data = _scrape_taux_bkam()

    if not data:
        data = _get_mock_taux()

    cache_bkam['bkam_rates'] = data

    # Cache fichier
    cache_file = os.path.join(CACHE_DIR, "bkam_cache.json")
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'rates': data}, f, indent=2)
    except Exception:
        pass

    return data


def get_taux_sans_risque(maturite='3mois'):
    """
    Récupère le taux sans risque pour une maturité donnée.
    Utilisé dans la formule: F₀ = S₀ × e^((r-q)×T)
    """
    data = get_taux_bkam()
    key = f'taux_{maturite}'
    return data.get(key, 0.025)


# ────────────────────────────────────────────
# STATUT DES CONNEXIONS
# ────────────────────────────────────────────

def update_statut_connexions():
    """Met à jour le statut des connexions dans session_state."""
    import streamlit as st

    try:
        indices = get_indices_bourse()
        is_live = any(v.get('source') == 'live' for v in indices.values())
        st.session_state['statut_bourse'] = '🟢' if is_live else '🟡'
    except Exception:
        st.session_state['statut_bourse'] = '🔴'

    try:
        taux = get_taux_bkam()
        is_live = taux.get('source', '').startswith('BKAM')
        st.session_state['statut_bkam'] = '🟢' if is_live else '🟡'
    except Exception:
        st.session_state['statut_bkam'] = '🔴'

    st.session_state['statut_news'] = '🟡'
