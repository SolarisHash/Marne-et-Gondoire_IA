import subprocess
import sys
import os

if __name__ == "__main__":
    # On force le dossier courant sur le dossier contenant scrapy.cfg
    scrapers_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(scrapers_dir)
    # Commande pour lancer le spider et sauvegarder les résultats dans result.json
    cmd = [sys.executable, '-m', 'scrapy', 'crawl', 'test_spider', '-o', 'result.json']
    print(f"Lancement du spider test_spider...")
    proc = subprocess.Popen(cmd)
    proc.wait()
    print("Terminé. Résultats dans result.json.")
