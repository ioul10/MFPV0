# ============================================
# CONFIGURATION - MASI Futures Pro V0.0.0
# Plateforme de Pricing Futures MASI / MASI20
# ============================================

APP_NAME = "MASI Futures Pro"
APP_VERSION = "0.0.0"
APP_SUBTITLE = "Plateforme de Pricing des Contrats Futures MASI & MASI20"

# ── Auteurs ──
AUTHORS = [
    {"nom": "OULMADANI Ilyas", "email": "ioulmadani@gmail.com"},
    {"nom": "ATANANE Oussama", "email": ""},
]

# ── Couleurs ──
COLORS = {
    'primary': '#1E3A5F',
    'secondary': '#2E5C8A',
    'accent': '#3E7CAD',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'info': '#3B82F6',
    'background': '#F5F7FA',
    'card': '#FFFFFF',
    'text': '#1F2937',
    'text_muted': '#6B7280',
    'border': '#E5E7EB',
}

# ── Paramètres Contrat Future (selon PDF CDG Capital) ──
FUTURES_CONFIG = {
    'multiplicateur': 10,           # 10 MAD par point d'indice
    'devise': 'MAD',
    'pas_cotation': 0.1,            # 0.1 point d'indice = 1 MAD
    'mode_cotation': 'continu',     # En continu par point d'indice
    'echeances': ['Mars', 'Juin', 'Septembre', 'Décembre'],  # Trimestrielles
    'dernier_jour': 'Dernier vendredi du mois d\'échéance',
    'mode_denouement': 'Cash',
    'depot_garantie': 1000,         # 1000 MAD révisable
    'sous_jacent': 'MASI20',       # Composition revue yearly
}

# ── Indices suivis ──
INDICES = ["MASI", "MASI20"]

# ── Durées de cache (secondes) ──
CACHE_DURATION = {
    'indices': 300,         # 5 minutes
    'bkam_rates': 3600,     # 1 heure
    'news': 1800,           # 30 minutes
    'constituents': 86400,  # 24 heures
}

# ── URLs sources ──
URLS = {
    'bourse_casa': 'https://www.casablanca-bourse.com',
    'ilboursa': 'https://www.ilboursa.com',
    'bkam': 'https://www.bkam.ma',
}

# ── Raccourcis ──
MULTIPLICATEUR = FUTURES_CONFIG['multiplicateur']
DEVISE = FUTURES_CONFIG['devise']
