#!/usr/bin/env python3
"""
Client Python SIMPLE pour lancer l'Agent IA et voir le résultat
Usage: python progress_client.py --sample_size 5
"""

import requests
import json
import time
import argparse
import sys

def launch_ai_enrichment_client(base_url="http://localhost:8080", sample_size=10):
    """
    Lance l'enrichissement IA et affiche le résultat final
    SIMPLE ET FONCTIONNEL
    """
    
    print(f"🚀 Lancement enrichissement IA - {sample_size} entreprises")
    print("📊 Traitement de vos données réelles")
    print("⏳ Patience... (regardez le terminal du serveur pour la progression)")
    print("=" * 60)
    
    url = f"{base_url}/ai-agent/enrich"
    params = {"sample_size": sample_size, "test_mode": True}
    
    start_time = time.time()
    
    try:
        print("🔄 Envoi de la requête...")
        
        # Faire la requête (peut prendre du temps)
        response = requests.post(url, params=params, timeout=600)  # 10 min max
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n🎉 Enrichissement terminé en {duration:.1f}s !")
            print("=" * 60)
            
            # Afficher le résumé
            if "execution_summary" in result:
                summary = result["execution_summary"]
                print(f"📊 Résultats:")
                print(f"   • Total traité: {summary['sample_size']}")
                print(f"   • Enrichis: {summary['enriched_count']}")
                print(f"   • Taux de succès: {summary['success_rate']}")
                print(f"   • Score qualité: {summary['avg_quality_score']}")
                print(f"   • Durée: {summary['duration_seconds']}s")
            
            # Fichier généré
            if "output_file" in result:
                print(f"📁 Fichier Excel généré: {result['output_file']}")
            
            # Sites web trouvés
            if "detailed_results" in result and "enrichment_data" in result["detailed_results"]:
                enrichment_data = result["detailed_results"]["enrichment_data"]
                
                if enrichment_data:
                    print(f"\n🌐 Sites web trouvés:")
                    for idx, data in enrichment_data.items():
                        if "website" in data:
                            website = data["website"]
                            company_name = data.get("company_name", f"Entreprise {idx}")
                            print(f"   {idx}. {company_name[:30]} → {website}")
            
            # Recommandations de l'IA
            if "advanced_analytics" in result and "recommendations" in result["advanced_analytics"]:
                recommendations = result["advanced_analytics"]["recommendations"]
                
                if recommendations:
                    print(f"\n💡 Recommandations de l'IA:")
                    for i, rec in enumerate(recommendations[:3], 1):
                        print(f"   {i}. {rec['recommendation']}")
            
            print("=" * 60)
            print("✅ Succès ! Votre fichier Excel enrichi est prêt.")
            
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Détail: {error_data.get('error', 'Erreur inconnue')}")
            except:
                print(f"   Réponse: {response.text}")
    
    except requests.exceptions.Timeout:
        print("\n⏰ Timeout - L'enrichissement prend plus de 10 minutes")
        print("   Vérifiez le terminal du serveur pour voir s'il continue")
    
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("   Vérifiez que le serveur FastAPI tourne sur http://localhost:8080")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Arrêt demandé par l'utilisateur")
    
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")

def test_connection(base_url="http://localhost:8080"):
    """Test de connexion basique"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Connexion serveur OK")
            return True
        else:
            print(f"❌ Serveur répond mais erreur: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Serveur non accessible")
        return False
    except Exception as e:
        print(f"❌ Erreur connexion: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client SIMPLE pour Agent IA")
    parser.add_argument("--sample_size", type=int, default=5, help="Nombre d'entreprises à traiter")
    parser.add_argument("--url", default="http://localhost:8080", help="URL du serveur")
    parser.add_argument("--test", action="store_true", help="Test de connexion seulement")
    
    args = parser.parse_args()
    
    if args.test:
        test_connection(args.url)
    else:
        print("🧪 Test de connexion...")
        if test_connection(args.url):
            print("🚀 Connexion OK, lancement enrichissement...\n")
            launch_ai_enrichment_client(args.url, args.sample_size)
        else:
            print("💡 Démarrez le serveur avec :")
            print("   python mcp_server/main.py")
            sys.exit(1)