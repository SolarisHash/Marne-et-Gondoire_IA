
import time
import sys
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class AIProgressTracker:
    """
    Système de barre de progression temps réel pour l'Agent IA
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
        self.update_interval = 0.5  # Mise à jour toutes les 0.5 secondes
    
    def start(self):
        """Démarre le tracking avec affichage temps réel"""
        self.start_time = datetime.now()
        self.last_update = self.start_time
        self.is_running = True
        
        # Affichage initial
        self._clear_lines(3)
        print(f"\n🚀 {self.task_name} - Démarrage")
        print("=" * 60)
        
        # Démarrer thread de mise à jour
        self.update_thread = threading.Thread(target=self._update_display_loop, daemon=True)
        self.update_thread.start()
        
        # Affichage initial de la barre
        self._update_display()
    
    def update(self, success: bool = True, item_name: str = ""):
        """Met à jour la progression"""
        self.current_item += 1
        
        if success:
            self.successful += 1
        else:
            self.failed += 1
        
        self.last_update = datetime.now()
        
        # Log de l'item traité (optionnel)
        if item_name:
            status = "✅" if success else "❌"
            print(f"\r{' ' * 80}\r{status} {item_name[:50]}", end="", flush=True)
            time.sleep(0.3)  # Laisser le temps de voir le nom
    
    def finish(self):
        """Termine le tracking"""
        self.is_running = False
        
        if self.update_thread:
            self.update_thread.join(timeout=1)
        
        # Affichage final
        self._update_display()
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\n\n🎉 {self.task_name} terminé !")
        print(f"⏱️  Durée totale: {self._format_duration(total_time)}")
        print(f"📊 Résultats: {self.successful} succès, {self.failed} échecs")
        print(f"🎯 Taux de réussite: {(self.successful / self.total_items * 100):.1f}%")
        print("=" * 60)
    
    def _update_display_loop(self):
        """Boucle de mise à jour continue de l'affichage"""
        while self.is_running:
            time.sleep(self.update_interval)
            if self.is_running:
                self._update_display()
    
    def _update_display(self):
        """Met à jour l'affichage de la barre de progression"""
        if not self.start_time:
            return
        
        # Calculs temporels
        now = datetime.now()
        elapsed = (now - self.start_time).total_seconds()
        
        # Progression
        progress = self.current_item / self.total_items if self.total_items > 0 else 0
        percentage = progress * 100
        
        # Estimation temps restant
        if self.current_item > 0 and progress > 0:
            estimated_total_time = elapsed / progress
            remaining_time = estimated_total_time - elapsed
        else:
            remaining_time = 0
        
        # Vitesse de traitement
        items_per_second = self.current_item / elapsed if elapsed > 0 else 0
        
        # Construction de la barre
        filled_length = int(self.bar_width * progress)
        bar = "█" * filled_length + "░" * (self.bar_width - filled_length)
        
        # Effacer les lignes précédentes et afficher
        self._clear_lines(3)
        
        # Ligne 1: Barre de progression
        print(f"\r🤖 {self.task_name}")
        
        # Ligne 2: Barre visuelle avec pourcentage
        print(f"[{bar}] {percentage:5.1f}% ({self.current_item}/{self.total_items})")
        
        # Ligne 3: Statistiques temps réel
        stats = (
            f"⏱️  {self._format_duration(elapsed)} écoulé | "
            f"🕐 {self._format_duration(remaining_time)} restant | "
            f"⚡ {items_per_second:.1f}/s | "
            f"✅ {self.successful} | ❌ {self.failed}"
        )
        print(stats)
        
        sys.stdout.flush()
    
    def _clear_lines(self, num_lines: int):
        """Efface les lignes précédentes dans le terminal"""
        for _ in range(num_lines):
            # Déplacer le curseur vers le haut et effacer la ligne
            sys.stdout.write('\033[A\033[K')
        sys.stdout.flush()
    
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