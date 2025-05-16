# models/database.py
# Modèles de base de données pour DelfMeals

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, DateTime, Integer, String, Text, JSON
from datetime import datetime
import json

# Instance SQLAlchemy
db = SQLAlchemy()

class Recette(db.Model):
    """Modèle SQLAlchemy pour les recettes"""
    
    __tablename__ = 'recettes'
    
    id = db.Column(Integer, primary_key=True)
    nom = db.Column(String(200), nullable=False)
    type_plat = db.Column(String(50), nullable=False)
    origine = db.Column(String(100))
    categorie = db.Column(String(50), nullable=False)
    nb_personnes = db.Column(Integer, default=4)
    temps_preparation = db.Column(Integer, nullable=False)
    difficulte = db.Column(String(50), nullable=False)
    saisons = db.Column(Text)  # JSON stringifié
    preparation = db.Column(Text)  # JSON stringifié
    ingredients = db.Column(Text)  # JSON stringifié
    note = db.Column(Text)
    date_creation = db.Column(DateTime, default=datetime.utcnow)
    date_modification = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convertit la recette en dictionnaire"""
        try:
            return {
                'Recette': self.nom,
                'Type de plat': self.type_plat,
                'Origine': self.origine,
                'Catégorie': self.categorie,
                'Nombre de personnes': self.nb_personnes,
                'Temps de préparation': self.temps_preparation,
                'Difficulté': self.difficulte,
                'Saison': json.loads(self.saisons) if self.saisons else [],
                'Préparation': json.loads(self.preparation) if self.preparation else [],
                'Ingrédients': json.loads(self.ingredients) if self.ingredients else [],
                'Note': self.note or ''
            }
        except (json.JSONDecodeError, Exception) as e:
            # En cas d'erreur, retourner des valeurs par défaut
            return {
                'Recette': self.nom,
                'Type de plat': self.type_plat,
                'Origine': self.origine,
                'Catégorie': self.categorie,
                'Nombre de personnes': self.nb_personnes,
                'Temps de préparation': self.temps_preparation,
                'Difficulté': self.difficulte,
                'Saison': [],
                'Préparation': [],
                'Ingrédients': [],
                'Note': self.note or ''
            }
    
    def __repr__(self):
        return f'<Recette {self.nom}>'

class Menu(db.Model):
    """Modèle pour les menus sauvegardés"""
    
    __tablename__ = 'menus'
    
    id = db.Column(Integer, primary_key=True)
    nom = db.Column(String(200), nullable=False)
    menu_data = db.Column(Text, nullable=False)  # JSON stringifié
    nb_personnes = db.Column(Integer, default=4)
    notes = db.Column(Text)
    date_creation = db.Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convertit le menu en dictionnaire avec recettes complètes"""
        try:
            # Charger les données du menu
            menu_data = json.loads(self.menu_data)
            
            # Enrichir avec les données complètes des recettes depuis la DB
            menu_enrichi = {}
            for jour, repas in menu_data.items():
                menu_enrichi[jour] = {}
                for moment, recette_info in repas.items():
                    if recette_info and isinstance(recette_info, dict):
                        # Si la recette a un ID, récupérer les données complètes
                        if 'id' in recette_info:
                            recette_complete = Recette.query.get(recette_info['id'])
                            if recette_complete:
                                recette_dict = recette_complete.to_dict()
                                recette_dict['id'] = recette_complete.id
                                menu_enrichi[jour][moment] = recette_dict
                            else:
                                # Fallback si la recette n'existe plus
                                menu_enrichi[jour][moment] = recette_info
                        else:
                            # Pas d'ID, utiliser les données telles quelles
                            menu_enrichi[jour][moment] = recette_info
                    else:
                        menu_enrichi[jour][moment] = None
            
            return menu_enrichi
            
        except (json.JSONDecodeError, Exception) as e:
            # En cas d'erreur, retourner les données brutes
            print(f"Erreur lors du décodage du menu {self.id}: {e}")
            try:
                return json.loads(self.menu_data)
            except:
                return {}
    
    def __repr__(self):
        return f'<Menu {self.nom}>'

def init_database():
    """Initialise la base de données en créant toutes les tables"""
    try:
        db.create_all()
        print("✅ Base de données initialisée avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base : {e}")
        return False

def reset_database():
    """Remet à zéro la base de données (ATTENTION: supprime tout!)"""
    try:
        db.drop_all()
        db.create_all()
        print("✅ Base de données remise à zéro")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la remise à zéro : {e}")
        return False