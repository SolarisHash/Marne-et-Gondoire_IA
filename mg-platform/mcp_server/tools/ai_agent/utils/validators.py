# ============================================================================
# VALIDATEURS UTILITAIRES
# mg-platform/mcp_server/tools/ai_agent/utils/validators.py
# ============================================================================

"""
Fonctions utilitaires de validation
"""

import re
from typing import Any


def is_valid_business_website(url: str) -> bool:
    """Valide qu'une URL est potentiellement un site d'entreprise"""
    
    if not url or not isinstance(url, str):
        return False
    
    # Doit être une URL complète
    if not url.startswith(('http://', 'https://')):
        return False
    
    # Domaines à exclure
    excluded_domains = [
        'google.', 'bing.', 'yahoo.', 'duckduckgo.',
        'facebook.', 'twitter.', 'instagram.', 'tiktok.',
        'youtube.', 'wikipedia.', 'wikimedia.',
        'societe.com', 'verif.com', 'infogreffe.',
        'pages-jaunes.', 'pagesjaunes.', 'kompass.',
        'amazon.', 'ebay.', 'leboncoin.'
    ]
    
    url_lower = url.lower()
    
    if any(domain in url_lower for domain in excluded_domains):
        return False
    
    # Accepter les domaines business courants
    business_indicators = [
        '.fr', '.com', '.net', '.org', '.eu',
        'wix.', 'wordpress.', 'jimdo.', 'shopify.',
        'business.site', 'sites.google.'
    ]
    
    if any(indicator in url_lower for indicator in business_indicators):
        return True
    
    return False


def is_valid_siret(siret: str) -> bool:
    """Valide un numéro SIRET"""
    
    if not siret or not isinstance(siret, str):
        return False
    
    # Nettoyer le SIRET
    siret_clean = re.sub(r'[^\d]', '', siret)
    
    # Doit avoir 14 chiffres
    if len(siret_clean) != 14:
        return False
    
    # Vérification basique (tous les chiffres identiques = invalide)
    if len(set(siret_clean)) == 1:
        return False
    
    return True


def is_valid_email(email: str) -> bool:
    """Valide une adresse email"""
    
    if not email or not isinstance(email, str):
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))


def clean_company_name(name: str) -> str:
    """Nettoie un nom d'entreprise"""
    
    if not name:
        return ""
    
    # Supprimer les formes juridiques
    name_clean = re.sub(r'\s+(SARL|SAS|EURL|SA|SNC|SCI|SASU)$', '', name, flags=re.IGNORECASE)
    
    # Normaliser les espaces
    name_clean = ' '.join(name_clean.split())
    
    return name_clean.strip()


def normalize_commune_name(commune: str) -> str:
    """Normalise un nom de commune"""
    
    if not commune:
        return ""
    
    # Supprimer les accents et normaliser
    commune_clean = commune.strip().title()
    
    # Remplacer les caractères spéciaux
    commune_clean = re.sub(r'[^\w\s\-]', ' ', commune_clean)
    commune_clean = ' '.join(commune_clean.split())
    
    return commune_clean