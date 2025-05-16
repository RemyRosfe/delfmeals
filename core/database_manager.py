# core/database_manager.py
# Gestion de la base de données SQLite avec conservation des IDs des recettes dans les menus

import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager
from models.database import db, Menu, Recette

class DatabaseManager:
    """Gestionnaire de base de données pour DelfMeals"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            # Utiliser le chemin par défaut
            from config import Config
            self.db_path = Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
        else:
            self.db_path = db_path
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    # ============================================================================
    # GESTION DES RECETTES
    # ============================================================================
    
    def add_recette(self, recette_data):
        """Ajoute une nouvelle recette"""
        try:
            recette = Recette(
                nom=recette_data['Recette'],
                type_plat=recette_data['Type de plat'],
                origine=recette_data.get('Origine'),
                categorie=recette_data['Catégorie'],
                nb_personnes=recette_data.get('Nombre de personnes', 4),
                temps_preparation=recette_data['Temps de préparation'],
                difficulte=recette_data['Difficulté'],
                saisons=json.dumps(recette_data.get('Saison', [])),
                preparation=json.dumps(recette_data.get('Préparation', [])),
                ingredients=json.dumps(recette_data.get('Ingrédients', [])),
                note=recette_data.get('Note', '')
            )
            
            db.session.add(recette)
            db.session.commit()
            return recette.id
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_all_recettes(self, as_dict=True):
        """Récupère toutes les recettes"""
        recettes = Recette.query.all()
        
        if as_dict:
            # Retourner des dictionnaires avec IDs
            result = []
            for recette in recettes:
                recette_dict = recette.to_dict()
                recette_dict['id'] = recette.id
                result.append(recette_dict)
            return result
        else:
            return recettes
    
    def get_recette_by_id(self, recette_id, as_dict=True):
        """Récupère une recette par son ID"""
        recette = Recette.query.get(recette_id)
        
        if recette is None:
            return None
        
        if as_dict:
            recette_dict = recette.to_dict()
            recette_dict['id'] = recette.id
            return recette_dict
        else:
            return recette
    
    def update_recette(self, recette_id, recette_data):
        """Met à jour une recette existante"""
        try:
            recette = Recette.query.get(recette_id)
            if not recette:
                raise ValueError(f"Recette {recette_id} non trouvée")
            
            # Mettre à jour les champs
            recette.nom = recette_data['Recette']
            recette.type_plat = recette_data['Type de plat']
            recette.origine = recette_data.get('Origine')
            recette.categorie = recette_data['Catégorie']
            recette.nb_personnes = recette_data.get('Nombre de personnes', 4)
            recette.temps_preparation = recette_data['Temps de préparation']
            recette.difficulte = recette_data['Difficulté']
            recette.saisons = json.dumps(recette_data.get('Saison', []))
            recette.preparation = json.dumps(recette_data.get('Préparation', []))
            recette.ingredients = json.dumps(recette_data.get('Ingrédients', []))
            recette.note = recette_data.get('Note', '')
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete_recette(self, recette_id):
        """Supprime une recette"""
        try:
            recette = Recette.query.get(recette_id)
            if recette:
                db.session.delete(recette)
                db.session.commit()
                return True
            return False
            
        except Exception as e:
            db.session.rollback()
            return False
    
    def search_recettes(self, nom=None, categorie=None, origine=None, difficulte=None, 
                       saison=None, as_dict=True):
        """Recherche les recettes selon des critères"""
        query = Recette.query
        
        if nom:
            query = query.filter(Recette.nom.ilike(f'%{nom}%'))
        if categorie:
            query = query.filter(Recette.categorie == categorie)
        if origine:
            query = query.filter(Recette.origine == origine)
        if difficulte:
            query = query.filter(Recette.difficulte == difficulte)
        if saison:
            query = query.filter(Recette.saisons.like(f'%{saison}%'))
        
        recettes = query.all()
        
        if as_dict:
            result = []
            for recette in recettes:
                recette_dict = recette.to_dict()
                recette_dict['id'] = recette.id
                result.append(recette_dict)
            return result
        else:
            return recettes
    
    # ============================================================================
    # GESTION DES MENUS AVEC CONSERVATION DES IDS RECETTES
    # ============================================================================
    
    def save_menu(self, menu_dict, nom, nb_personnes, notes=""):
        """Sauvegarde un menu avec conservation des IDs des recettes"""
        try:
            # Créer une version du menu qui préserve les IDs des recettes
            menu_with_ids = {}
            for jour, repas in menu_dict.items():
                menu_with_ids[jour] = {}
                for moment, recette in repas.items():
                    if recette:
                        # S'assurer que la recette a un ID
                        if 'id' not in recette:
                            # Essayer de trouver l'ID par le nom
                            recette_obj = Recette.query.filter_by(nom=recette['Recette']).first()
                            if recette_obj:
                                recette['id'] = recette_obj.id
                            else:
                                print(f"Warning: Impossible de trouver l'ID pour {recette['Recette']}")
                        
                        # Stocker avec l'ID préservé
                        menu_with_ids[jour][moment] = recette
                    else:
                        menu_with_ids[jour][moment] = None
            
            # Sauvegarder en base
            menu = Menu(
                nom=nom,
                menu_data=json.dumps(menu_with_ids),
                nb_personnes=nb_personnes,
                notes=notes,
                date_creation=datetime.now()
            )
            
            db.session.add(menu)
            db.session.commit()
            return menu.id
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_menu_by_id(self, menu_id, as_dict=True):
        """Récupère un menu par son ID avec les recettes complètes"""
        menu = Menu.query.get(menu_id)
        
        if not menu:
            return None
        
        if as_dict:
            return menu
        else:
            return menu
    
    def get_all_menus(self, limit=None, as_dict=True):
        """Récupère tous les menus"""
        query = Menu.query.order_by(Menu.date_creation.desc())
        
        if limit:
            query = query.limit(limit)
        
        menus = query.all()
        
        if as_dict:
            return menus
        else:
            return menus
    
    def delete_menu(self, menu_id):
        """Supprime un menu"""
        try:
            menu = Menu.query.get(menu_id)
            if menu:
                db.session.delete(menu)
                db.session.commit()
                return True
            return False
            
        except Exception as e:
            db.session.rollback()
            return False
    
    # ============================================================================
    # STATISTIQUES
    # ============================================================================
    
    def get_statistiques(self):
        """Calcule les statistiques pour l'accueil"""
        from collections import Counter
        
        # Compter les recettes
        nb_recettes = Recette.query.count()
        nb_menus = Menu.query.count()
        
        # Répartition par catégorie
        recettes = Recette.query.all()
        categories = Counter([r.categorie for r in recettes])
        
        # Répartition par difficulté
        difficultes = Counter([r.difficulte for r in recettes])
        
        # Répartition par origine
        origines = Counter([r.origine for r in recettes if r.origine])
        
        return {
            'nb_recettes': nb_recettes,
            'nb_menus': nb_menus,
            'categories': dict(categories),
            'difficultes': dict(difficultes),
            'origines': dict(origines)
        }

# ============================================================================
# FONCTION UTILITAIRE POUR RÉCUPÉRER LES RECETTES
# ============================================================================

def get_recettes_from_db():
    """Fonction utilitaire pour récupérer toutes les recettes avec leurs IDs"""
    with DatabaseManager() as db:
        return db.get_all_recettes(as_dict=True)
