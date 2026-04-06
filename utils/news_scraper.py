# ============================================
# NEWS SCRAPER - MASI Futures Pro V0.0.0
# Sources: Ilboursa, Bourse de Casablanca
# ============================================

from datetime import datetime
from cachetools import TTLCache
import config
import pandas as pd

news_cache = TTLCache(maxsize=100, ttl=config.CACHE_DURATION['news'])


def _scrape_ilboursa_news(max_news=10):
    """
    Scrape les actualités depuis Ilboursa.
    Returns: list of dicts ou None
    """
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        }

        url = "https://www.ilboursa.com/marches/actualites"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        news_list = []

        # Chercher les articles (adapter selon la structure du site)
        articles = soup.find_all('div', class_='article-item')
        if not articles:
            articles = soup.find_all('article')
        if not articles:
            # Fallback: chercher tous les liens d'actualités
            articles = soup.find_all('a', href=True)
            articles = [a for a in articles if '/marches/' in a.get('href', '') or '/actualites/' in a.get('href', '')]

        for article in articles[:max_news]:
            try:
                titre = article.get_text(strip=True)[:200]
                url_article = article.get('href', '')
                if url_article and not url_article.startswith('http'):
                    url_article = f"https://www.ilboursa.com{url_article}"

                if titre and len(titre) > 15:
                    news_list.append({
                        'source': 'Ilboursa',
                        'titre': titre,
                        'resume': '',
                        'date': datetime.now().strftime('%d/%m/%Y'),
                        'url': url_article,
                        'categorie': 'Marché',
                    })
            except Exception:
                continue

        return news_list if news_list else None

    except Exception as e:
        print(f"⚠️ Scraping Ilboursa échoué: {e}")
        return None


def _get_mock_news():
    """Actualités mock réalistes et informatives."""
    return [
        {
            'source': 'Bourse de Casablanca',
            'titre': 'Lancement des contrats Futures sur indices MASI et MASI20',
            'resume': 'La Bourse de Casablanca annonce le lancement prochain des premiers contrats futures sur les indices MASI et MASI20, marquant une étape majeure dans la modernisation du marché financier marocain.',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'url': 'https://www.casablanca-bourse.com',
            'categorie': 'Produits Dérivés',
        },
        {
            'source': 'CDG Capital',
            'titre': 'CDG Capital se positionne sur le marché à terme marocain',
            'resume': 'CDG Capital interviendra comme investisseur, négociateur, compensateur et gestionnaire de post-trade sur le marché des futures indices.',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'url': 'https://www.cdgcapital.ma',
            'categorie': 'Institutionnel',
        },
        {
            'source': 'Bank Al-Maghrib',
            'titre': 'Publication de l\'Instruction BAM N° IN-2026-01 sur les futures',
            'resume': 'Bank Al-Maghrib publie les modalités de calcul du cours théorique des contrats futures sur indices, basé sur la formule F₀ = S₀ × e^((r-q)×T).',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'url': 'https://www.bkam.ma',
            'categorie': 'Réglementation',
        },
        {
            'source': 'Ilboursa',
            'titre': 'Les investisseurs institutionnels saluent l\'introduction des dérivés',
            'resume': 'L\'introduction des futures permettra la couverture des portefeuilles actions, l\'arbitrage et la prise d\'exposition rapide sans achat direct des actions.',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'url': 'https://www.ilboursa.com',
            'categorie': 'Marché',
        },
        {
            'source': 'AMMC',
            'titre': 'Cadre réglementaire du marché à terme finalisé',
            'resume': 'L\'AMMC finalise le cadre réglementaire encadrant les contrats futures, incluant les limites de position, les appels de marge et le marking-to-market quotidien.',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'url': 'https://www.ammc.ma',
            'categorie': 'Réglementation',
        },
    ]


def get_all_news(force_refresh=False, max_total=5):
    """
    Récupère les actualités du marché.
    Priorité: 1) Cache → 2) Scraping Ilboursa → 3) Mock
    """
    if not force_refresh and 'news_data' in news_cache:
        return news_cache['news_data']

    # Essayer le scraping live
    news_list = _scrape_ilboursa_news(max_news=max_total)

    # Fallback: mock
    if not news_list:
        news_list = _get_mock_news()

    df_news = pd.DataFrame(news_list[:max_total])
    news_cache['news_data'] = df_news

    return df_news
