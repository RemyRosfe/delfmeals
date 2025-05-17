# init_db.py - Script d'initialisation de la base de données
import os
import sys

# Ajouter le répertoire racine au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models.recette import Recette, Ingredient, Etape  # Adaptez selon vos modèles
from models.database import init_database

def initialiser_base():
    """Initialise la base de données avec les données des fichiers sources"""
    print("🗃️ Initialisation de la base de données...")
    
    # Créer une instance de l'application
    app = create_app('production')
    
    with app.app_context():
        # Recréer toutes les tables
        db.create_all()
        
        # Vérifier si des données existent déjà
        if Recette.query.count() > 0:
            print("✅ La base contient déjà des données")
            return
        
        # Charger les recettes de test
        try:
            # Méthode 1: Depuis recettes_test.py
            from data.recettes_test import RECETTES_TEST
            for recette_data in RECETTES_TEST:
                recette = Recette(**recette_data)
                db.session.add(recette)
            
            # Méthode 2: Depuis les fichiers JSON (si applicable)
            import json
            import glob
            
            json_files = glob.glob('recettes_json/**/*.json', recursive=True)
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        recette_data = json.load(f)
                        # Adapter selon votre structure JSON
                        recette = Recette(**recette_data)
                        db.session.add(recette)
                except Exception as e:
                    print(f"⚠️ Erreur avec {json_file}: {e}")
            
            # Confirmer les changements
            db.session.commit()
            print(f"✅ {Recette.query.count()} recettes importées avec succès")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de l'initialisation: {e}")
            sys.exit(1)

if __name__ == '__main__':
    initialiser_base()
