# import_recettes_scannees.py
# Script pour importer les recettes numérisées dans DelfMeals

import json
import os
from pathlib import Path
from app import create_app
from core.database_manager import DatabaseManager

def valider_recette_scannee(recette):
    """Valide et corrige une recette scannée avant import"""
    
    # Validation des champs obligatoires
    if not recette.get("Recette"):
        recette["Recette"] = "Recette scannée"
    
    # S'assurer que les types sont corrects
    recette["Nombre de personnes"] = int(recette.get("Nombre de personnes", 4))
    recette["Temps de préparation"] = int(recette.get("Temps de préparation", 30))
    
    # Valider les listes prédéfinies
    categories_valides = ["Viande rouge", "Volaille", "Poisson", "Végétarien"]
    if recette.get("Catégorie") not in categories_valides:
        recette["Catégorie"] = "Végétarien"
    
    difficultes_valides = ["Rapide", "Normal", "Élaboré"]
    if recette.get("Difficulté") not in difficultes_valides:
        recette["Difficulté"] = "Normal"
    
    # S'assurer que les ingrédients et préparation sont des listes
    if not isinstance(recette.get("Ingrédients"), list):
        recette["Ingrédients"] = []
    
    if not isinstance(recette.get("Préparation"), list):
        recette["Préparation"] = []
    
    if not isinstance(recette.get("Saison"), list):
        recette["Saison"] = ["Toutes saisons"]
    
    return recette

def afficher_recette_preview(recette):
    """Affiche un aperçu de la recette pour validation"""
    print(f"\n📋 {recette['Recette']}")
    print(f"   📂 Catégorie: {recette['Catégorie']}")
    print(f"   ⏱️  Temps: {recette['Temps de préparation']} min")
    print(f"   👥 Personnes: {recette['Nombre de personnes']}")
    print(f"   📊 Difficulté: {recette['Difficulté']}")
    print(f"   🥕 Ingrédients: {len(recette['Ingrédients'])} éléments")
    print(f"   👨‍🍳 Étapes: {len(recette['Préparation'])} étapes")

def verifier_et_corriger_recette(chemin_json):
    """Interface interactive pour vérifier et corriger une recette"""
    print(f"\n{'='*60}")
    print(f"🔍 Vérification de {os.path.basename(chemin_json)}")
    print(f"{'='*60}")
    
    with open(chemin_json, 'r', encoding='utf-8') as f:
        recette = json.load(f)
    
    # Valider la recette
    recette = valider_recette_scannee(recette)
    
    # Afficher l'aperçu
    afficher_recette_preview(recette)
    
    # Demander confirmation/modifications
    while True:
        print(f"\n🔧 Actions possibles:")
        print(f"  1. ✅ Importer cette recette telle quelle")
        print(f"  2. ✏️  Modifier le nom de la recette")
        print(f"  3. 🔄 Changer la catégorie")
        print(f"  4. 📝 Voir/modifier les ingrédients")
        print(f"  5. 👨‍🍳 Voir/modifier la préparation")
        print(f"  6. ⏭️  Passer cette recette")
        print(f"  7. 💾 Sauvegarder les modifications et continuer")
        
        choix = input(f"\nVotre choix (1-7): ").strip()
        
        if choix == "1":
            return recette
        
        elif choix == "2":
            nouveau_nom = input(f"Nouveau nom (actuel: {recette['Recette']}): ").strip()
            if nouveau_nom:
                recette["Recette"] = nouveau_nom
                print(f"✅ Nom modifié")
        
        elif choix == "3":
            print(f"Catégories disponibles:")
            categories = ["Viande rouge", "Volaille", "Poisson", "Végétarien"]
            for i, cat in enumerate(categories, 1):
                print(f"  {i}. {cat}")
            choix_cat = input(f"Votre choix (1-4): ").strip()
            try:
                recette["Catégorie"] = categories[int(choix_cat)-1]
                print(f"✅ Catégorie modifiée: {recette['Catégorie']}")
            except:
                print(f"❌ Choix invalide")
        
        elif choix == "4":
            print(f"\n🥕 Ingrédients actuels:")
            for i, ing in enumerate(recette["Ingrédients"], 1):
                print(f"  {i}. {ing['quantité']} {ing['unité']} {ing['nom']}")
            input(f"\nAppuyez sur Entrée pour continuer...")
        
        elif choix == "5":
            print(f"\n👨‍🍳 Étapes de préparation:")
            for i, etape in enumerate(recette["Préparation"], 1):
                print(f"  {i}. {etape}")
            input(f"\nAppuyez sur Entrée pour continuer...")
        
        elif choix == "6":
            return None
        
        elif choix == "7":
            # Sauvegarder les modifications
            with open(chemin_json, 'w', encoding='utf-8') as f:
                json.dump(recette, f, indent=2, ensure_ascii=False)
            print(f"💾 Modifications sauvegardées")
        
        else:
            print(f"❌ Choix invalide")

def importer_recettes_numerisees(dossier_recettes="recettes_numerisees"):
    """Import interactif des recettes numérisées"""
    
    if not os.path.exists(dossier_recettes):
        print(f"❌ Dossier {dossier_recettes} introuvable")
        return
    
    # Trouver tous les fichiers JSON de recettes
    fichiers_json = [f for f in os.listdir(dossier_recettes) if f.endswith('_recette.json')]
    
    if not fichiers_json:
        print(f"❌ Aucune recette trouvée dans {dossier_recettes}")
        return
    
    print(f"🔍 {len(fichiers_json)} recettes trouvées pour import")
    
    # Créer l'application Flask
    app = create_app()
    
    recettes_importees = 0
    recettes_ignorees = 0
    
    with app.app_context():
        with DatabaseManager() as db:
            for fichier_json in fichiers_json:
                chemin_complet = os.path.join(dossier_recettes, fichier_json)
                
                # Vérifier et éventuellement corriger la recette
                recette_finale = verifier_et_corriger_recette(chemin_complet)
                
                if recette_finale:
                    try:
                        # Importer dans la base
                        recette_id = db.add_recette(recette_finale)
                        print(f"✅ Recette importée: {recette_finale['Recette']} (ID: {recette_id})")
                        recettes_importees += 1
                    except Exception as e:
                        print(f"❌ Erreur lors de l'import: {e}")
                        recettes_ignorees += 1
                else:
                    print(f"⏭️  Recette ignorée")
                    recettes_ignorees += 1
    
    print(f"\n📊 Résumé de l'import:")
    print(f"  ✅ Importées: {recettes_importees}")
    print(f"  ⏭️  Ignorées: {recettes_ignorees}")
    print(f"  📍 Total: {len(fichiers_json)}")

if __name__ == "__main__":
    print("📤 Import de recettes scannées dans DelfMeals")
    print("============================================")
    
    # Vérifier que le dossier existe
    dossier = "recettes_numerisees"
    if not os.path.exists(dossier):
        print(f"💡 Créez d'abord le dossier '{dossier}' avec les recettes numérisées")
        print(f"   Utilisez le script ocr_recettes.py pour numériser vos recettes")
    else:
        # Lancer l'import interactif
        importer_recettes_numerisees(dossier)
