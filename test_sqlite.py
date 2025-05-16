# test_sqlite.py
# Test de la migration SQLite pour DelfMeals

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.migration import migration_complete, verifier_migration
from core.database_manager import DatabaseManager, get_recettes_from_db
from core.generateur import generer_menu_semaine
from models.database import init_database

def test_complet_sqlite():
    """Test complet du système SQLite"""
    print("🧪 TEST COMPLET DU SYSTÈME SQLITE")
    print("="*50)
    
    # 1. Initialisation et migration
    print("\n1️⃣ Migration des données...")
    try:
        migration_complete()
        print("✅ Migration réussie")
    except Exception as e:
        print(f"❌ Erreur migration: {e}")
        return False
    
    # 2. Test de récupération des recettes
    print("\n2️⃣ Test de récupération des recettes...")
    try:
        recettes = get_recettes_from_db()
        print(f"✅ {len(recettes)} recettes récupérées")
        print(f"  Exemple: {recettes[0]['Recette']}")
    except Exception as e:
        print(f"❌ Erreur récupération: {e}")
        return False
    
    # 3. Test de génération de menu avec données SQLite
    print("\n3️⃣ Test de génération de menu...")
    try:
        menu, saison, rapport = generer_menu_semaine(recettes, optimise=True)
        print(f"✅ Menu généré pour la saison {saison}")
        print(f"  Score d'équilibrage: {rapport.get('score', 'N/A')}")
        
        # Compter les repas générés
        nb_repas = sum(1 for jour, repas in menu.items() 
                      for moment, recette in repas.items() if recette)
        print(f"  {nb_repas} repas générés")
    except Exception as e:
        print(f"❌ Erreur génération: {e}")
        return False
    
    # 4. Test du DatabaseManager
    print("\n4️⃣ Test du DatabaseManager...")
    try:
        with DatabaseManager() as db:
            # Test de recherche
            vegetariens = db.search_recettes(categorie="Végétarien")
            print(f"✅ {len(vegetariens)} recettes végétariennes trouvées")
            
            # Test de sauvegarde de menu
            menu_id = db.save_menu(menu, "Menu de test SQLite", 4, "Test automatique")
            print(f"✅ Menu sauvegardé avec ID: {menu_id}")
            
            # Test de récupération du menu
            menu_recupere = db.get_menu_by_id(menu_id)
            print(f"✅ Menu récupéré: {len(menu_recupere)} jours")
            
            # Test des statistiques
            stats = db.get_statistiques()
            print(f"✅ Statistiques: {stats['nb_recettes']} recettes, {stats['nb_menus']} menus")
    except Exception as e:
        print(f"❌ Erreur DatabaseManager: {e}")
        return False
    
    # 5. Vérification finale
    print("\n5️⃣ Vérification finale...")
    try:
        verifier_migration()
        print("✅ Tous les tests passés avec succès!")
        return True
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
        return False

def test_performances():
    """Test des performances du système SQLite"""
    print("\n🚀 TEST DE PERFORMANCES")
    print("-"*30)
    
    import time
    
    with DatabaseManager() as db:
        # Test vitesse de récupération
        start = time.time()
        recettes = db.get_all_recettes()
        end = time.time()
        print(f"Récupération de {len(recettes)} recettes: {(end-start)*1000:.1f}ms")
        
        # Test vitesse de recherche
        start = time.time()
        results = db.search_recettes(categorie="Végétarien", difficulte="Rapide")
        end = time.time()
        print(f"Recherche complexe ({len(results)} résultats): {(end-start)*1000:.1f}ms")
        
        # Test génération de menu
        start = time.time()
        menu, _, _ = generer_menu_semaine(recettes)
        end = time.time()
        print(f"Génération de menu: {(end-start)*1000:.1f}ms")
        
        # Test sauvegarde menu
        start = time.time()
        menu_id = db.save_menu(menu, "Menu performance test")
        end = time.time()
        print(f"Sauvegarde de menu: {(end-start)*1000:.1f}ms")

def demo_interactif():
    """Démonstration interactive du système SQLite"""
    print("\n🎮 DÉMONSTRATION INTERACTIVE")
    print("-"*30)
    
    with DatabaseManager() as db:
        while True:
            print("\nOptions:")
            print("1. Voir toutes les recettes")
            print("2. Rechercher une recette")
            print("3. Générer un menu")
            print("4. Voir les statistiques")
            print("5. Quitter")
            
            choix = input("Votre choix (1-5): ").strip()
            
            if choix == "1":
                recettes = db.get_all_recettes()
                print(f"\n📚 {len(recettes)} recettes trouvées:")
                for i, r in enumerate(recettes[:10], 1):
                    print(f"  {i}. {r['Recette']} ({r['Catégorie']}, {r['Difficulté']})")
                if len(recettes) > 10:
                    print(f"  ... et {len(recettes)-10} autres")
            
            elif choix == "2":
                terme = input("Terme de recherche: ").strip()
                if terme:
                    recettes = db.search_recettes(nom=terme)
                    print(f"\n🔍 {len(recettes)} résultat(s) pour '{terme}':")
                    for r in recettes:
                        print(f"  • {r['Recette']}")
            
            elif choix == "3":
                print("\n🗓️ Génération de menu...")
                recettes = db.get_all_recettes()
                menu, saison, rapport = generer_menu_semaine(recettes, optimise=True)
                
                nom_menu = input("Nom du menu (optionnel): ").strip() or "Menu généré"
                menu_id = db.save_menu(menu, nom_menu)
                print(f"✅ Menu '{nom_menu}' sauvegardé (ID: {menu_id})")
                print(f"  Saison: {saison}")
            
            elif choix == "4":
                stats = db.get_statistiques()
                print(f"\n📊 Statistiques de la base:")
                print(f"  • Recettes: {stats['nb_recettes']}")
                print(f"  • Menus: {stats['nb_menus']}")
                print(f"  • Catégories: {len(stats['categories'])}")
                print(f"  • Origines: {len(stats['origines'])}")
            
            elif choix == "5":
                break
            
            else:
                print("Choix invalide")

if __name__ == "__main__":
    print("DelfMeals - Test du système SQLite")
    print("\nChoisissez un test:")
    print("1. Test complet")
    print("2. Test de performances")
    print("3. Démonstration interactive")
    print("4. Tout faire")
    
    choix = input("Votre choix (1-4): ").strip()
    
    if choix == "1":
        success = test_complet_sqlite()
        print(f"\n{'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    elif choix == "2":
        test_performances()
    elif choix == "3":
        demo_interactif()
    elif choix == "4":
        print("🚀 EXÉCUTION DE TOUS LES TESTS")
        success = test_complet_sqlite()
        if success:
            test_performances()
            demo_interactif()
    else:
        print("Choix invalide")