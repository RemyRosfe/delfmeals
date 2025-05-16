# main.py
# Point d'entrée principal pour DelfMeals

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports des modules DelfMeals
from models.recette import valider_recette, creer_recette_vide
from core.saisons import detecter_saison_actuelle
from core.filtres import filtrer_recettes, rechercher_recettes, grouper_par_critere
from core.generateur import generer_menu_semaine, analyser_equilibrage_menu, creer_liste_courses
from core.quantites import ajuster_quantites_recette, ajuster_menu_personnes
from ui.affichage import (afficher_recette, afficher_menu_semaine, afficher_liste_courses,
                         lister_recettes, afficher_rapport_menu, afficher_recommandations,
                         afficher_recette_ajustee)
from utils.validation import generer_rapport_base, valider_recettes
from data.recettes_test import get_recettes_test

def main():
    """Fonction principale d'exécution de DelfMeals"""
    print("🍽️ DELFMEALS - Générateur de menus intelligent")
    print("="*60)
    
    # Charger les recettes de test
    recettes = get_recettes_test()
    print(f"📚 {len(recettes)} recettes chargées")
    
    # Menu principal
    while True:
        print(f"\n{'='*60}")
        print("🏠 MENU PRINCIPAL")
        print("="*60)
        print("1. 🗓️  Générer un menu de la semaine")
        print("2. 🔍 Rechercher une recette")
        print("3. 📋 Afficher une recette")
        print("4. 📊 Rapport sur la base de recettes")
        print("5. 🧪 Tests et démonstrations")
        print("6. ❌ Quitter")
        
        choix = input("\nVotre choix (1-6): ").strip()
        
        if choix == "1":
            menu_generation(recettes)
        elif choix == "2":
            menu_recherche(recettes)
        elif choix == "3":
            menu_affichage(recettes)
        elif choix == "4":
            generer_rapport_base(recettes)
        elif choix == "5":
            menu_tests(recettes)
        elif choix == "6":
            print("👋 Au revoir et bon appétit !")
            break
        else:
            print("❌ Choix invalide")

def menu_generation(recettes):
    """Menu de génération de menus"""
    print(f"\n🗓️ GÉNÉRATION DE MENU")
    print("-"*30)
    
    print("1. Menu standard (7j avec weekend)")
    print("2. Menu semaine uniquement (5j)")
    print("3. Menu optimisé (plusieurs tentatives)")
    print("4. Retour")
    
    choix = input("\nVotre choix (1-4): ").strip()
    
    if choix == "1":
        menu, saison, rapport = generer_menu_semaine(recettes, inclure_weekend=True)
        afficher_resultat_menu(menu, saison, rapport)
    elif choix == "2":
        menu, saison, rapport = generer_menu_semaine(recettes, inclure_weekend=False)
        afficher_resultat_menu(menu, saison, rapport)
    elif choix == "3":
        print("⚙️ Génération optimisée en cours...")
        menu, saison, rapport = generer_menu_semaine(recettes, optimise=True, tentatives=5)
        print("🏆 Menu optimisé généré !")
        afficher_resultat_menu(menu, saison, rapport)
    elif choix == "4":
        return

def afficher_resultat_menu(menu, saison, rapport):
    """Affiche le résultat complet d'une génération de menu"""
    # Afficher le menu
    afficher_menu_semaine(menu)
    
    # Demander ajustement de personnes
    print(f"\n🔢 Ajustement du nombre de personnes ?")
    reponse = input("Entrez le nombre de personnes (défaut=4, Enter pour ignorer): ").strip()
    
    nb_personnes = None
    if reponse:
        try:
            nb_personnes = int(reponse)
            if nb_personnes <= 0:
                print("❌ Nombre invalide, utilisation par défaut")
                nb_personnes = None
        except ValueError:
            print("❌ Nombre invalide, utilisation par défaut")
            nb_personnes = None
    
    # Générer et afficher la liste de courses
    print(f"\n🛒 Génération de la liste de courses...")
    if nb_personnes:
        print(f"📏 Ajustement pour {nb_personnes} personnes")
        ingredients = creer_liste_courses(menu, nb_personnes)
    else:
        ingredients = creer_liste_courses(menu)
    
    afficher_liste_courses(ingredients)
    
    # Afficher le rapport d'équilibrage
    afficher_rapport_menu(rapport)
    
    # Afficher les recommandations
    afficher_recommandations(rapport)

def menu_recherche(recettes):
    """Menu de recherche de recettes"""
    print(f"\n🔍 RECHERCHE DE RECETTES")
    print("-"*30)
    
    # Recherche simple par nom
    terme = input("Terme de recherche (nom de recette): ").strip()
    
    # Filtres optionnels
    print(f"\nFiltres optionnels (Enter pour ignorer):")
    categorie = input("Catégorie (Viande rouge/Volaille/Poisson/Végétarien): ").strip()
    difficulte = input("Difficulté (Rapide/Normal/Élaboré): ").strip()
    origine = input("Origine (ex: Cuisine italienne): ").strip()
    temps_max = input("Temps maximum (minutes): ").strip()
    
    # Construire les filtres
    filtres = {}
    if categorie:
        filtres['categorie'] = categorie
    if difficulte:
        filtres['difficulte'] = difficulte
    if origine:
        filtres['origine'] = origine
    if temps_max:
        try:
            filtres['temps_max'] = int(temps_max)
        except ValueError:
            print("⚠️ Temps invalide, ignoré")
    
    # Effectuer la recherche
    resultats = rechercher_recettes(recettes, terme, **filtres)
    
    # Afficher les résultats
    print(f"\n📋 RÉSULTATS DE RECHERCHE")
    print(f"Found {len(resultats)} recette(s)")
    print("-"*40)
    
    if resultats:
        for i, recette in enumerate(resultats, 1):
            print(f"{i}. {recette['Recette']} ({recette['Catégorie']}, {recette['Difficulté']}, {recette['Temps de préparation']}min)")
        
        # Demander si affichage détaillé
        choix = input(f"\nAfficher une recette en détail (1-{len(resultats)}, Enter pour ignorer): ").strip()
        if choix:
            try:
                index = int(choix) - 1
                if 0 <= index < len(resultats):
                    afficher_recette(resultats[index])
                else:
                    print("❌ Index invalide")
            except ValueError:
                print("❌ Index invalide")
    else:
        print("Aucune recette trouvée avec ces critères")

def menu_affichage(recettes):
    """Menu d'affichage des recettes"""
    print(f"\n📋 AFFICHAGE DE RECETTES")
    print("-"*30)
    
    # Lister toutes les recettes
    lister_recettes(recettes)
    
    # Demander le choix
    choix = input(f"Choisir une recette (1-{len(recettes)}, Enter pour retour): ").strip()
    
    if choix:
        try:
            index = int(choix) - 1
            if 0 <= index < len(recettes):
                recette = recettes[index]
                
                # Demander ajustement de personnes
                print(f"\n🔢 Ajustement du nombre de personnes ?")
                nb_personnes = input(f"Nombre de personnes (défaut={recette.get('Nombre de personnes', 4)}): ").strip()
                
                if nb_personnes:
                    try:
                        nb_personnes = int(nb_personnes)
                        afficher_recette_ajustee(recette, nb_personnes)
                    except ValueError:
                        print("❌ Nombre invalide, affichage normal")
                        afficher_recette(recette)
                else:
                    afficher_recette(recette)
            else:
                print("❌ Index invalide")
        except ValueError:
            print("❌ Index invalide")

def menu_tests(recettes):
    """Menu de tests et démonstrations"""
    print(f"\n🧪 TESTS ET DÉMONSTRATIONS")
    print("-"*30)
    
    print("1. Test de détection des saisons")
    print("2. Test de filtrage avancé")
    print("3. Test d'ajustement des quantités")
    print("4. Test de génération optimisée")
    print("5. Validation complète des recettes")
    print("6. Retour")
    
    choix = input("\nVotre choix (1-6): ").strip()
    
    if choix == "1":
        test_saisons()
    elif choix == "2":
        test_filtrage(recettes)
    elif choix == "3":
        test_quantites(recettes)
    elif choix == "4":
        test_optimisation(recettes)
    elif choix == "5":
        erreurs = valider_recettes(recettes)
        if erreurs:
            print(f"❌ {len(erreurs)} erreurs trouvées:")
            for erreur in erreurs[:10]:
                print(f"  • {erreur}")
        else:
            print("✅ Toutes les recettes sont valides")
    elif choix == "6":
        return

def test_saisons():
    """Test de détection des saisons"""
    print(f"\n🌍 TEST DE DÉTECTION DES SAISONS")
    print("-"*40)
    
    saison_actuelle, saisons_disponibles = detecter_saison_actuelle()
    print(f"Saison actuelle: {saison_actuelle}")
    print(f"Saisons disponibles: {', '.join(saisons_disponibles)}")
    
    from core.saisons import est_periode_transition
    if est_periode_transition():
        print("📅 Nous sommes en période de transition")
    else:
        print("📅 Saison stable")

def test_filtrage(recettes):
    """Test de filtrage avancé"""
    print(f"\n🔍 TEST DE FILTRAGE AVANCÉ")
    print("-"*40)
    
    # Test de différents filtres
    tests = [
        ("Recettes rapides", {'difficulte': 'Rapide'}),
        ("Plats végétariens", {'categorie': 'Végétarien'}),
        ("Cuisine asiatique/méditerranéenne", {'origines': ['Cuisine asiatique', 'Cuisine méditerranéenne']}),
        ("Plats ≤ 25 min", {'temps_max': 25}),
        ("Viandes (rouge + volaille)", {'categories': ['Viande rouge', 'Volaille']})
    ]
    
    for nom_test, filtres in tests:
        resultats = filtrer_recettes(recettes, **filtres)
        print(f"{nom_test}: {len(resultats)} recette(s)")

def test_quantites(recettes):
    """Test d'ajustement des quantités"""
    print(f"\n🔢 TEST D'AJUSTEMENT DES QUANTITÉS")
    print("-"*40)
    
    # Prendre la première recette comme exemple
    recette = recettes[0]
    print(f"Recette test: {recette['Recette']}")
    print(f"Original pour {recette['Nombre de personnes']} personnes")
    
    # Afficher quelques ingrédients originaux
    print("Ingrédients originaux:")
    for ing in recette['Ingrédients'][:3]:
        if ing['quantité']:
            print(f"  • {ing['quantité']} {ing['unité']} {ing['nom']}")
    
    # Ajuster pour 6 personnes
    recette_ajustee = ajuster_quantites_recette(recette, 6)
    print(f"\nAjusté pour 6 personnes:")
    for ing in recette_ajustee['Ingrédients'][:3]:
        if ing['quantité']:
            print(f"  • {ing['quantité']} {ing['unité']} {ing['nom']}")

def test_optimisation(recettes):
    """Test de génération optimisée"""
    print(f"\n🎯 TEST DE GÉNÉRATION OPTIMISÉE")
    print("-"*40)
    
    print("Comparaison entre génération simple et optimisée...")
    
    # Génération simple
    menu_simple, _, rapport_simple = generer_menu_semaine(recettes, inclure_weekend=False)
    score_simple = analyser_equilibrage_menu(menu_simple)
    
    # Génération optimisée
    menu_opti, _, rapport_opti = generer_menu_semaine(recettes, inclure_weekend=False, optimise=True, tentatives=3)
    
    print(f"\nRésultats:")
    print(f"Menu simple - Contraintes viande: {'✓' if rapport_simple['contraintes_respectees']['viandes'] else '✗'}")
    print(f"Menu optimisé - Contraintes viande: {'✓' if rapport_opti['contraintes_respectees']['viandes'] else '✗'}")

if __name__ == "__main__":
    main()