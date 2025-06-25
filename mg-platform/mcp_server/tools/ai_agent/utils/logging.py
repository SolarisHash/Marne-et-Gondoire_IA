# ============================================================================
# CONFIGURATION LOGGING
# mg-platform/mcp_server/tools/ai_agent/utils/logging.py
# ============================================================================

"""
Configuration du logging pour l'Agent IA
Responsabilités:
- Configuration logging détaillé avec session ID
- Format compatible Windows/Linux
- Niveau de détail configurable
- Rotation des logs
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any


def setup_session_logging(session_id: str, config: Dict[str, Any]) -> logging.Logger:
    """
    Configure le logging pour une session d'enrichissement
    
    Args:
        session_id: ID unique de la session
        config: Configuration de l'agent
        
    Returns:
        Logger configuré
    """
    
    try:
        # Créer le dossier logs
        log_dir = Path(config.get("logs_dir", "logs"))
        log_dir.mkdir(exist_ok=True)
        
        # Nom du fichier de log
        log_file = log_dir / f'ai_agent_{session_id}.log'
        
        # Créer un logger spécifique à cette session
        logger_name = f"ai_agent_{session_id}"
        logger = logging.getLogger(logger_name)
        
        # Éviter la duplication si le logger existe déjà
        if logger.handlers:
            return logger
        
        # Configuration du niveau
        log_level = getattr(logging, config.get("log_level", "INFO").upper())
        logger.setLevel(log_level)
        
        # Format détaillé pour les logs
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler pour fichier
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Handler pour console (optionnel)
        if config.get("detailed_logging", True):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # Empêcher la propagation vers le logger root
        logger.propagate = False
        
        return logger
        
    except Exception as e:
        # Fallback vers logging basique
        print(f"⚠️ Configuration logging avancée échouée: {e}")
        return _get_basic_logger()


def _get_basic_logger() -> logging.Logger:
    """Logger de fallback en cas d'erreur"""
    
    logger = logging.getLogger("ai_agent_fallback")
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Handler console basique
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        logger.propagate = False
    
    return logger


def setup_rotating_logs(log_dir: str, max_files: int = 10, max_size_mb: int = 10) -> logging.Logger:
    """
    Configure des logs rotatifs pour éviter l'accumulation
    
    Args:
        log_dir: Répertoire des logs
        max_files: Nombre maximum de fichiers
        max_size_mb: Taille maximum par fichier en MB
        
    Returns:
        Logger avec rotation
    """
    
    try:
        log_path = Path(log_dir) / "ai_agent_rotating.log"
        log_path.parent.mkdir(exist_ok=True)
        
        logger = logging.getLogger("ai_agent_rotating")
        logger.setLevel(logging.INFO)
        
        # Handler rotatif
        handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_size_mb * 1024 * 1024,
            backupCount=max_files,
            encoding='utf-8'
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.propagate = False
        
        return logger
        
    except Exception:
        return _get_basic_logger()


def log_enrichment_start(logger: logging.Logger, sample_size: int, session_id: str):
    """Log standardisé de début d'enrichissement"""
    
    logger.info(f"🚀 Démarrage Agent IA - Session: {session_id}")
    logger.info(f"📊 Échantillon: {sample_size} entreprises")
    logger.info("=" * 50)


def log_enrichment_end(logger: logging.Logger, results: Dict[str, Any]):
    """Log standardisé de fin d'enrichissement"""
    
    success_count = results.get("enriched", 0)
    total_count = results.get("processed", 0)
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    logger.info("=" * 50)
    logger.info(f"🎯 Enrichissement terminé: {success_count}/{total_count} succès ({success_rate:.1f}%)")


def log_company_processing(logger: logging.Logger, idx: int, total: int, company_name: str):
    """Log standardisé de traitement d'entreprise"""
    
    logger.info(f"🔍 [{idx}/{total}] Traitement: {company_name[:50]}{'...' if len(company_name) > 50 else ''}")


def log_enrichment_success(logger: logging.Logger, company_name: str, score: float, website: str = None):
    """Log standardisé de succès d'enrichissement"""
    
    msg = f"✅ Succès - {company_name[:30]} - Score: {score}%"
    if website:
        msg += f" - Site: {website}"
    
    logger.info(msg)


def log_enrichment_failure(logger: logging.Logger, company_name: str, reason: str):
    """Log standardisé d'échec d'enrichissement"""
    
    logger.warning(f"❌ Échec - {company_name[:30]} - Raison: {reason}")


def log_performance_metrics(logger: logging.Logger, metrics: Dict[str, Any]):
    """Log des métriques de performance"""
    
    logger.info("📊 MÉTRIQUES DE PERFORMANCE:")
    logger.info(f"   • Entreprises traitées: {metrics.get('processed', 0)}")
    logger.info(f"   • Enrichissements réussis: {metrics.get('enriched', 0)}")
    logger.info(f"   • Échecs: {metrics.get('failed', 0)}")
    
    if metrics.get('quality_scores'):
        avg_quality = sum(metrics['quality_scores']) / len(metrics['quality_scores'])
        logger.info(f"   • Score qualité moyen: {avg_quality:.1f}%")
    
    if metrics.get('processing_times'):
        avg_time = sum(metrics['processing_times']) / len(metrics['processing_times'])
        logger.info(f"   • Temps moyen par entreprise: {avg_time:.1f}s")


def cleanup_old_logs(log_dir: str, days_to_keep: int = 30):
    """Nettoie les anciens logs"""
    
    try:
        import time
        from datetime import datetime, timedelta
        
        log_path = Path(log_dir)
        if not log_path.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_timestamp = cutoff_date.timestamp()
        
        deleted_count = 0
        for log_file in log_path.glob("ai_agent_*.log"):
            if log_file.stat().st_mtime < cutoff_timestamp:
                log_file.unlink()
                deleted_count += 1
        
        if deleted_count > 0:
            print(f"🧹 Nettoyage: {deleted_count} anciens logs supprimés")
            
    except Exception as e:
        print(f"⚠️ Erreur nettoyage logs: {e}")