# utils/migration.py
# Migration des données de DelfMeals vers SQLite

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import init_database, get_session, Recette, Ingredient, Saison, Menu, MenuJour
from data.recettes_test import get_recettes_test
from core.generateur import generer_menu_semaine
from utils.validation import valider_recettes
from datetime import datetime, timedelta

def migrer_recettes_test():
    """Migre les recettes de test vers SQLite"""
    print("📦 Migration des recettes de test vers SQLite...")
    
    # Initialiser la base si nécessaire
    init_database()
    
    session = get_session()
    try:
        # Vérifier si déjà migrés
        if session.query(Recette).count() > 0:
            print("⚠️  Des recettes existent déjà. Voulez-vous continuer ? (o/n)")
            if input().lower() != 'o':
                return
            print("🔄 Suppression des recettes existantes...")
            session.query(Recette).delete()
            session.commit()
        
        # Charger et valider les recettes test
        recettes_test = get_recettes_test()
        erreurs = valider_recettes(recettes_test)
        
        if erreurs:
            print(f"❌ {len(erreurs)} erreurs dans les recettes:")
            for erreur in erreurs[:5]:
                print(f"  • {erreur}")
            print("Migration interrompue.")
            return
        
        # Migrer chaque recette
        recettes_creees = 0
        for i, recette_dict in enumerate(recettes_test, 1):
            print(f"  {i}/{len(recettes_test)}: {recette_dict['Recette']}")
            
            # Créer la recette
            recette = Recette.from_dict(recette_dict, session)
            session.add(recette)
            recettes_creees += 1
        
        # Sauvegarder
        session.commit()
        print(f"✅ {recettes_creees} recettes migrées avec succès !")
        
        # Statistiques
        print(f"\n📊 Statistiques de migration:")
        print(f"  • Recettes: {session.query(Recette).count()}")
        print(f"  • Ingrédients: {session.query(Ingredient).count()}")
        print(f"  • Saisons utilisées: {len(session.query(Saison).filter(Saison.recettes.any()).all())}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erreur lors de la migration: {e}")
        raise
    finally:
        session.close()

def generer_menu_exemple(nom="Menu test", nb_personnes=4):
    """Génère un menu exemple et le sauvegarde en base"""
    print(f"🗓️ Génération d'un menu exemple: '{nom}'...")
    
    session = get_session()
    try:
        # Récupérer les recettes depuis la base
        recettes_db = session.query(Recette).all()
        recettes_dict = [r.to_dict() for r in recettes_db]
        
        if len(recettes_dict) < 14:
            print(f"⚠️  Seulement {len(recettes_dict)} recettes disponibles (14 recommandées)")
        
        # Générer le menu avec le système existant
        menu_dict, saison, rapport = generer_menu_semaine(recettes_dict, inclure_weekend=True, optimise=True)
        
        # Créer l'objet Menu
        menu = Menu(
            nom=nom,
            nb_personnes=nb_personnes,
            semaine_du=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),  # Semaine prochaine
            notes=f"Menu généré automatiquement pour la saison {saison}",
            inclut_weekend=1
        )
        session.add(menu)
        session.flush()  # Pour obtenir l'ID
        
        # Créer les jours du menu
        jours_ordre = {
            'Lundi': 1, 'Mardi': 2, 'Mercredi': 3, 'Jeudi': 4, 'Vendredi': 5,
            'Samedi': 6, 'Dimanche': 7
        }
        
        for nom_jour, repas in menu_dict.items():
            # Trouver les IDs des recettes
            recette_midi_id = None
            recette_soir_id = None
            
            if repas['midi']:
                recette_midi = session.query(Recette).filter_by(nom=repas['midi']['Recette']).first()
                if recette_midi:
                    recette_midi_id = recette_midi.id
            
            if repas['soir']:
                recette_soir = session.query(Recette).filter_by(nom=repas['soir']['Recette']).first()
                if recette_soir:
                    recette_soir_id = recette_soir.id
            
            # Créer le jour
            jour = MenuJour(
                menu_id=menu.id,
                nom_jour=nom_jour,
                ordre_jour=jours_ordre[nom_jour],
                recette_midi_id=recette_midi_id,
                recette_soir_id=recette_soir_id
            )
            session.add(jour)
        
        # Sauvegarder
        session.commit()
        print(f"✅ Menu '{nom}' créé avec succès (ID: {menu.id})")
        
        # Afficher résumé
        print(f"\n📋 Résumé du menu:")
        for jour in session.query(MenuJour).filter_by(menu_id=menu.id).order_by(MenuJour.ordre_jour):
            midi = jour.recette_midi.nom if jour.recette_midi else "—"
            soir = jour.recette_soir.nom if jour.recette_soir else "—"
            print(f"  {jour.nom_jour:<9} | Midi: {midi:<30} | Soir: {soir}")
        
        return menu.id
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erreur lors de la génération du menu: {e}")
        raise
    finally:
        session.close()

def verifier_migration():
    """Vérifie l'intégrité de la migration"""
    print("🔍 Vérification de la migration...")
    
    session = get_session()
    try:
        # Compter les éléments
        nb_recettes = session.query(Recette).count()
        nb_ingredients = session.query(Ingredient).count()
        nb_saisons = session.query(Saison).count()
        nb_menus = session.query(Menu).count()
        
        print(f"\n📊 État de la base de données:")
        print(f"  • Recettes: {nb_recettes}")
        print(f"  • Ingrédients: {nb_ingredients}")
        print(f"  • Saisons: {nb_saisons}")
        print(f"  • Menus: {nb_menus}")
        
        # Vérifier les relations
        print(f"\n🔗 Vérification des relations:")
        
        # Recettes avec ingrédients
        recettes_sans_ingredients = session.query(Recette).filter(~Recette.ingredients.any()).count()
        print(f"  • Recettes sans ingrédients: {recettes_sans_ingredients}")
        
        # Recettes avec saisons
        recettes_sans_saisons = session.query(Recette).filter(~Recette.saisons.any()).count()
        print(f"  • Recettes sans saisons: {recettes_sans_saisons}")
        
        # Test de reconversion
        print(f"\n🧪 Test de reconversion:")
        première_recette = session.query(Recette).first()
        if première_recette:
            recette_dict = première_recette.to_dict()
            print(f"  • Conversion réussie: {recette_dict['Recette']}")
            print(f"  • Ingrédients: {len(recette_dict['Ingrédients'])}")
            print(f"  • Saisons: {recette_dict['Saison']}")
        
        # Vérifier que toutes les recettes de test sont présentes
        print(f"\n✅ Tests de cohérence:")
        recettes_originales = get_recettes_test()
        recettes_db_noms = {r.nom for r in session.query(Recette).all()}
        recettes_originales_noms = {r['Recette'] for r in recettes_originales}
        
        manquantes = recettes_originales_noms - recettes_db_noms
        en_trop = recettes_db_noms - recettes_originales_noms
        
        if not manquantes and not en_trop:
            print("  • Toutes les recettes de test sont présentes ✓")
        else:
            if manquantes:
                print(f"  • Recettes manquantes: {manquantes}")
            if en_trop:
                print(f"  • Recettes en trop: {en_trop}")
        
        print(f"\n✅ Vérification terminée")
        
    finally:
        session.close()

def export_vers_json(fichier_sortie="data/recettes_export.json"):
    """Exporte toutes les recettes vers un fichier JSON"""
    print(f"📤 Export des recettes vers {fichier_sortie}...")
    
    session = get_session()
    try:
        recettes = session.query(Recette).all()
        recettes_dict = [r.to_dict() for r in recettes]
        
        import json
        with open(fichier_sortie, 'w', encoding='utf-8') as f:
            json.dump(recettes_dict, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {len(recettes_dict)} recettes exportées vers {fichier_sortie}")
        
    finally:
        session.close()

def migration_complete():
    """Effectue une migration complète"""
    print("🚀 MIGRATION COMPLÈTE VERS SQLITE")
    print("="*50)
    
    # 1. Migrer les recettes
    migrer_recettes_test()
    
    # 2. Générer un menu exemple
    generer_menu_exemple("Menu de démonstration")
    
    # 3. Vérifier la migration
    verifier_migration()
    
    # 4. Export de sauvegarde
    export_vers_json()
    
    print("\n🎉 Migration terminée avec succès!")
    print("La base SQLite est prête à être utilisée avec Flask")

if __name__ == "__main__":
    print("Choisissez une action:")
    print("1. Migration complète")
    print("2. Migrer seulement les recettes")
    print("3. Générer un menu exemple")
    print("4. Vérifier la migration")
    print("5. Export JSON")
    
    choix = input("Votre choix (1-5): ").strip()
    
    if choix == "1":
        migration_complete()
    elif choix == "2":
        migrer_recettes_test()
    elif choix == "3":
        generer_menu_exemple()
    elif choix == "4":
        verifier_migration()
    elif choix == "5":
        export_vers_json()
    else:
        print("Choix invalide")