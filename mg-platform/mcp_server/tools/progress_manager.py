import time
import sys
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class AIProgressTracker:
    """
    Système de barre de progression temps réel pour l'Agent IA - VERSION CORRIGÉE
    Affiche progression, temps écoulé, temps restant, et statistiques live
    """
    
    def __init__(self, total_items: int, task_name: str = "Enrichissement IA"):
        self.total_items = total_items
        self.task_name = task_name
        self.current_item = 0
        self.successful = 0
        self.failed = 0
        
        # Timing
        self.start_time = None
        self.last_update = None
        
        # Threading pour mise à jour temps réel
        self.is_running = False
        self.update_thread = None
        
        # Configuration affichage
        self.bar_width = 40
        self.update_interval = 1.0  # Mise à jour toutes les 1 seconde
        
        # Contrôle thread-safe
        self._lock = threading.Lock()
    
    def start(self):
        """Démarre le tracking avec affichage temps réel"""
        self.start_time = datetime.now()
        self.last_update = self.start_time
        self.is_running = True
        
        # Affichage initial sécurisé
        try:
            print(f"\n🚀 {self.task_name} - Démarrage", flush=True)
            print("=" * 60, flush=True)
            
            # Démarrer thread de mise à jour seulement si on est dans un terminal
            if sys.stdout.isatty():
                self.update_thread = threading.Thread(target=self._update_display_loop, daemon=True)
                self.update_thread.start()
            
            # Affichage initial de la barre
            self._update_display()
            
        except Exception as e:
            print(f"⚠️ Affichage progression limité: {e}")
    
    def update(self, success: bool = True, item_name: str = ""):
        """Met à jour la progression de façon thread-safe"""
        with self._lock:
            self.current_item += 1
            
            if success:
                self.successful += 1
            else:
                self.failed += 1
            
            self.last_update = datetime.now()
        
        # Log de l'item traité (version sécurisée)
        if item_name:
            status = "✅" if success else "❌"
            try:
                # Affichage simple et sûr
                print(f"{status} [{self.current_item}/{self.total_items}] {item_name[:50]}", flush=True)
            except Exception:
                # Fallback silencieux si problème d'affichage
                pass
    
    def finish(self):
        """Termine le tracking"""
        self.is_running = False
        
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=2)
        
        # Affichage final sécurisé
        try:
            total_time = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
            
            print(f"\n🎉 {self.task_name} terminé !", flush=True)
            print(f"⏱️  Durée totale: {self._format_duration(total_time)}", flush=True)
            print(f"📊 Résultats: {self.successful} succès, {self.failed} échecs", flush=True)
            
            if self.total_items > 0:
                success_rate = (self.successful / self.total_items * 100)
                print(f"🎯 Taux de réussite: {success_rate:.1f}%", flush=True)
            
            print("=" * 60, flush=True)
            
        except Exception as e:
            print(f"⚠️ Erreur affichage final: {e}")
    
    def _update_display_loop(self):
        """Boucle de mise à jour continue - VERSION SÉCURISÉE"""
        while self.is_running:
            try:
                time.sleep(self.update_interval)
                if self.is_running:
                    self._update_display_safe()
            except Exception:
                # Continue silencieusement en cas d'erreur
                pass
    
    def _update_display_safe(self):
        """Version sécurisée de l'affichage"""
        try:
            if not self.start_time or not sys.stdout.isatty():
                return
            
            with self._lock:
                current = self.current_item
                successful = self.successful
                failed = self.failed
            
            # Calculs temporels
            now = datetime.now()
            elapsed = (now - self.start_time).total_seconds()
            
            # Progression
            progress = current / self.total_items if self.total_items > 0 else 0
            percentage = progress * 100
            
            # Construction simple de la barre
            filled_length = int(30 * progress)  # Barre plus courte pour compatibilité
            bar = "█" * filled_length + "░" * (30 - filled_length)
            
            # Affichage sur une ligne
            status_line = f"\r🤖 [{bar}] {percentage:5.1f}% ({current}/{self.total_items}) ✅{successful} ❌{failed}"
            
            print(status_line, end='', flush=True)
            
        except Exception:
            # Échec silencieux pour éviter de casser l'exécution
            pass
    
    def _update_display(self):
        """Affichage initial simple"""
        try:
            print(f"🤖 Traitement de {self.total_items} entreprises...", flush=True)
        except Exception:
            pass
    
    def _format_duration(self, seconds: float) -> str:
        """Formate une durée en secondes vers un format lisible"""
        if seconds < 0:
            return "0s"
        
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes:.0f}m{secs:02.0f}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours:.0f}h{minutes:02.0f}m"