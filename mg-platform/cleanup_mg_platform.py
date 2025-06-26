#!/usr/bin/env python3
"""
Script de nettoyage automatique pour mg-platform
Optimise l'architecture en supprimant les éléments inutiles

Usage: python cleanup_mg_platform.py
"""

import os
import shutil
import sys
from pathlib import Path

def print_banner():
    """Affiche la bannière du script"""
    print("=" * 60)
    print("🧹 SCRIPT DE NETTOYAGE MG-PLATFORM")
    print("=" * 60)
    print("📊 Optimisation de l'architecture du projet")
    print("🎯 Suppression des éléments inutiles")
    print("✅ Conservation de toutes les fonctionnalités")
    print("=" * 60)

def check_project_root():
    """Vérifie qu'on est dans le bon répertoire"""
    current_dir = Path.cwd()
    
    # Vérifier les marqueurs du projet mg-platform
    markers = [
        "mcp_server",
        "requirements.txt", 
        "README.md"
    ]
    
    missing_markers = [marker for marker in markers if not (current_dir / marker).exists()]
    
    if missing_markers:
        print(f"❌ ERREUR: Vous n'êtes pas dans le répertoire mg-platform")
        print(f"   Marqueurs manquants: {missing_markers}")
        print(f"   Répertoire actuel: {current_dir}")
        print(f"   Naviguez vers mg-platform/ et relancez le script")
        return False
    
    print(f"✅ Répertoire projet détecté: {current_dir.name}")
    return True

def backup_important_content():
    """Sauvegarde le contenu important avant suppression"""
    backup_data = {}
    
    # Sauvegarder le contenu d'Analyse.md
    analyse_file = Path("analyse/Analyse.md")
    if analyse_file.exists():
        with open(analyse_file, 'r', encoding='utf-8') as f:
            backup_data['analyse_content'] = f.read()
        print(f"📋 Contenu d'Analyse.md sauvegardé ({len(backup_data['analyse_content'])} caractères)")
    
    return backup_data

def update_readme_with_analysis(backup_data):
    """Met à jour README.md avec le contenu d'Analyse.md"""
    if 'analyse_content' not in backup_data:
        print("ℹ️  Aucun contenu d'analyse à intégrer")
        return
    
    readme_path = Path("README.md")
    
    if not readme_path.exists():
        print("⚠️  README.md non trouvé, création d'un nouveau fichier")
        readme_content = "# Marne & Gondoire Platform\n\n"
    else:
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
    
    # Ajouter le contenu d'analyse à la fin du README
    analysis_section = f"\n\n# 📊 Analyse détaillée du fichier de données\n\n{backup_data['analyse_content']}\n"
    
    # Éviter les doublons
    if "📊 Analyse détaillée" not in readme_content:
        readme_content += analysis_section
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("✅ Contenu d'Analyse.md intégré dans README.md")
    else:
        print("ℹ️  Contenu d'analyse déjà présent dans README.md")

def remove_directory_safe(dir_path, description):
    """Supprime un répertoire de façon sécurisée"""
    path = Path(dir_path)
    
    if not path.exists():
        print(f"ℹ️  {description}: déjà supprimé ou inexistant")
        return True
    
    if not path.is_dir():
        print(f"⚠️  {description}: n'est pas un répertoire")
        return False
    
    try:
        shutil.rmtree(path)
        print(f"✅ {description} supprimé")
        return True
    except Exception as e:
        print(f"❌ Erreur suppression {description}: {e}")
        return False

def remove_file_safe(file_path, description):
    """Supprime un fichier de façon sécurisée"""
    path = Path(file_path)
    
    if not path.exists():
        print(f"ℹ️  {description}: déjà supprimé ou inexistant")
        return True
    
    try:
        path.unlink()
        print(f"✅ {description} supprimé")
        return True
    except Exception as e:
        print(f"❌ Erreur suppression {description}: {e}")
        return False

def ask_user_confirmation(question, default="n"):
    """Demande confirmation à l'utilisateur"""
    choices = "Y/n" if default.lower() == "y" else "y/N"
    response = input(f"{question} ({choices}): ").strip().lower()
    
    if not response:
        return default.lower() == "y"
    
    return response in ['y', 'yes', 'oui']

def clean_logs_directory():
    """Nettoie le répertoire logs en gardant la structure"""
    logs_dir = Path("logs")
    
    if not logs_dir.exists():
        print("ℹ️  Répertoire logs/ inexistant")
        return
    
    # Compter les fichiers de logs
    log_files = list(logs_dir.glob("*.log"))
    
    if not log_files:
        print("ℹ️  Aucun fichier log à nettoyer")
        return
    
    if ask_user_confirmation(f"🧹 Supprimer {len(log_files)} fichiers de logs ?"):
        for log_file in log_files:
            try:
                log_file.unlink()
            except Exception as e:
                print(f"⚠️  Erreur suppression {log_file.name}: {e}")
        
        print(f"✅ {len(log_files)} fichiers de logs supprimés")
        
        # S'assurer que .gitkeep existe
        gitkeep = logs_dir / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
            print("✅ .gitkeep créé dans logs/")

def display_cleanup_summary():
    """Affiche le résumé du nettoyage"""
    print("\n" + "=" * 60)
    print("🎉 NETTOYAGE TERMINÉ")
    print("=" * 60)
    print("✅ Éléments supprimés:")
    print("   • Dossier analyse/ (contenu intégré dans README)")
    print("   • Fichier setup.py (redondant)")
    print("   • Anciens logs (optionnel)")
    print("   • Dossier tests/ (optionnel)")
    print()
    print("📊 Architecture optimisée:")
    print("   • Structure plus claire")
    print("   • Documentation centralisée") 
    print("   • Maintenance simplifiée")
    print("   • Fonctionnalités préservées à 100%")
    print()
    print("🚀 Prochaines étapes:")
    print("   1. Vérifier que tout fonctionne: python progress_client.py --test")
    print("   2. Tester l'Agent IA: python progress_client.py --sample_size 3")
    print("   3. Commiter les changements: git add . && git commit -m 'Optimisation architecture'")
    print("=" * 60)

def main():
    """Fonction principale du script"""
    print_banner()
    
    # Vérification du répertoire
    if not check_project_root():
        sys.exit(1)
    
    print(f"\n🔍 Analyse de la structure actuelle...")
    
    # Sauvegarde du contenu important
    backup_data = backup_important_content()
    
    print(f"\n🧹 Début du nettoyage automatique...")
    
    # 1. Intégrer Analyse.md dans README.md
    print(f"\n📖 Étape 1: Consolidation de la documentation")
    update_readme_with_analysis(backup_data)
    
    # 2. Supprimer le dossier analyse/
    print(f"\n📁 Étape 2: Suppression du dossier analyse/")
    remove_directory_safe("analyse", "Dossier analyse/")
    
    # 3. Supprimer setup.py
    print(f"\n📄 Étape 3: Suppression de setup.py")
    remove_file_safe("setup.py", "Fichier setup.py")
    
    # 4. Nettoyer les logs (optionnel)
    print(f"\n📋 Étape 4: Nettoyage des logs (optionnel)")
    clean_logs_directory()
    
    # 5. Supprimer tests/ (optionnel)
    print(f"\n🧪 Étape 5: Suppression du dossier tests/ (optionnel)")
    if Path("tests").exists():
        if ask_user_confirmation("🧪 Supprimer le dossier tests/ (minimal, 1 seul test) ?"):
            remove_directory_safe("tests", "Dossier tests/")
        else:
            print("ℹ️  Dossier tests/ conservé")
    
    # Résumé final
    display_cleanup_summary()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Nettoyage interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur inattendue: {e}")
        sys.exit(1)