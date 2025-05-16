# routes/main.py
# Routes principales de DelfMeals

from flask import Blueprint, render_template, request, flash, redirect, url_for
from core.database_manager import DatabaseManager

# Créer le blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Page d'accueil de DelfMeals"""
    
    # Récupérer quelques statistiques pour l'accueil
    with DatabaseManager() as db:
        stats = db.get_statistiques()
        recettes_objets = db.get_all_recettes(as_dict=False)[:6]  # 6 dernières
        recettes_recentes = []
        for recette_obj in recettes_objets:
            recette_dict = recette_obj.to_dict()
            recette_dict['id'] = recette_obj.id  # Ajouter l'ID
            recettes_recentes.append(recette_dict)   
                       
        menus_recents = db.get_all_menus(limit=3)  # 3 derniers menus
    
    return render_template('index.html', 
                         stats=stats,
                         recettes_recentes=recettes_recentes,
                         menus_recents=menus_recents)

@main.route('/about')
def about():
    """Page à propos de DelfMeals"""
    return render_template('about.html')

@main.route('/search')
def search():
    """Recherche globale dans les recettes"""
    
    query = request.args.get('q', '')
    results = []
    
    if query:
        with DatabaseManager() as db:
            # Récupérer toutes les recettes avec leurs IDs
            recettes_objets = db.get_all_recettes(as_dict=False)
            recettes_with_ids = []
            for recette_obj in recettes_objets:
                recette_dict = recette_obj.to_dict()
                recette_dict['id'] = recette_obj.id
                recettes_with_ids.append(recette_dict)
            
            # Filtrer par nom
            query_lower = query.lower()
            results = [r for r in recettes_with_ids 
                      if query_lower in r['Recette'].lower()]
            
            # Si peu de résultats, rechercher aussi dans d'autres champs
            if len(results) < 5:
                # Recherche par catégorie, origine, etc.
                from models.recette import CATEGORIES, ORIGINES, DIFFICULTES
                
                # Vérifier si le terme correspond à une catégorie
                if query.title() in CATEGORIES:
                    extra_results = [r for r in recettes_with_ids 
                                   if r['Catégorie'] == query.title()]
                    # Ajouter sans doublons
                    existing_names = {r['Recette'] for r in results}
                    for r in extra_results:
                        if r['Recette'] not in existing_names:
                            results.append(r)
                            existing_names.add(r['Recette'])
                
                # Recherche par origine
                if query.title() in ORIGINES or f"Cuisine {query.lower()}" in ORIGINES:
                    origine = query.title() if query.title() in ORIGINES else f"Cuisine {query.lower()}"
                    extra_results = [r for r in recettes_with_ids 
                                   if r.get('Origine') == origine]
                    existing_names = {r['Recette'] for r in results}
                    for r in extra_results:
                        if r['Recette'] not in existing_names:
                            results.append(r)
                            existing_names.add(r['Recette'])
    
    return render_template('search_results.html', 
                         query=query,
                         results=results)

@main.route('/api/stats')
def api_stats():
    """API pour récupérer les statistiques (pour AJAX)"""
    with DatabaseManager() as db:
        stats = db.get_statistiques()
    
    from flask import jsonify
    return jsonify(stats)

# Fonctions utilitaires pour les templates
@main.app_template_filter('pluralize')
def pluralize_filter(count, singular, plural):
    """Filtre pour pluraliser les mots"""
    return singular if count == 1 else plural

@main.app_template_global('format_temps')
def format_temps(minutes):
    """Formate le temps en heures et minutes"""
    if minutes < 60:
        return f"{minutes} min"
    else:
        heures = minutes // 60
        mins = minutes % 60
        if mins == 0:
            return f"{heures}h"
        else:
            return f"{heures}h{mins:02d}"