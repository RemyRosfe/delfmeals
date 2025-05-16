# routes/recettes.py
# Routes pour la gestion des recettes

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from core.database_manager import DatabaseManager
from models.recette import CATEGORIES, ORIGINES, DIFFICULTES, SAISONS, TYPE_PLATS

# Créer le blueprint
recettes = Blueprint('recettes', __name__)

@recettes.route('/')
def list_recettes():
    """Liste toutes les recettes avec pagination et filtres"""
    
    # Récupérer les paramètres de filtrage
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    # Filtres
    categorie = request.args.get('categorie')
    difficulte = request.args.get('difficulte')
    origine = request.args.get('origine')
    saison = request.args.get('saison')
    temps_max = request.args.get('temps_max', type=int)
    
    # Construire les critères de filtrage
    filtres = {}
    if categorie and categorie != 'all':
        filtres['categorie'] = categorie
    if difficulte and difficulte != 'all':
        filtres['difficulte'] = difficulte
    if origine and origine != 'all':
        filtres['origine'] = origine
    if saison and saison != 'all':
        filtres['saisons'] = [saison]
    if temps_max:
        filtres['temps_max'] = temps_max
    
    with DatabaseManager() as db:
        # Récupérer les recettes avec leurs IDs
        if filtres:
            # Récupérer toutes les recettes avec IDs puis filtrer
            recettes_objets = db.get_all_recettes(as_dict=False)
            recettes_with_ids = []
            for recette_obj in recettes_objets:
                recette_dict = recette_obj.to_dict()
                recette_dict['id'] = recette_obj.id
                recettes_with_ids.append(recette_dict)
            
            # Appliquer les filtres manuellement
            from core.filtres import filtrer_recettes
            recettes_data = filtrer_recettes(recettes_with_ids, **filtres)
        else:
            # Récupérer toutes les recettes avec leurs IDs
            recettes_objets = db.get_all_recettes(as_dict=False)
            recettes_data = []
            for recette_obj in recettes_objets:
                recette_dict = recette_obj.to_dict()
                recette_dict['id'] = recette_obj.id  # Ajouter l'ID de la base de données
                recettes_data.append(recette_dict)
        
        # Pagination manuelle (à améliorer)
        total = len(recettes_data)
        start = (page - 1) * per_page
        end = start + per_page
        recettes_paginated = recettes_data[start:end]
        
        # Informations de pagination
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_prev': page > 1,
            'has_next': page * per_page < total,
            'prev_num': page - 1 if page > 1 else None,
            'next_num': page + 1 if page * per_page < total else None
        }
    
    return render_template('recettes/list.html',
                         recettes=recettes_paginated,
                         pagination=pagination_info,
                         # Pour les filtres dans le template
                         categories=CATEGORIES,
                         difficultes=DIFFICULTES,
                         origines=ORIGINES,
                         saisons=SAISONS,
                         # Filtres actuels
                         current_filters={
                             'categorie': categorie,
                             'difficulte': difficulte,
                             'origine': origine,
                             'saison': saison,
                             'temps_max': temps_max
                         })

@recettes.route('/<int:recette_id>')
def detail_recette(recette_id):
    """Affiche le détail d'une recette"""
    
    with DatabaseManager() as db:
        recette = db.get_recette_by_id(recette_id)
        
        if not recette:
            flash('Recette introuvable', 'error')
            return redirect(url_for('recettes.list_recettes'))
    
    # Récupérer le nombre de personnes depuis l'URL (pour ajustement)
    nb_personnes = request.args.get('personnes', type=int)
    
    return render_template('recettes/detail.html',
                         recette=recette,
                         recette_id=recette_id,  # Passer l'ID explicitement
                         nb_personnes_ajuste=nb_personnes)

@recettes.route('/add', methods=['GET', 'POST'])
def add_recette():
    """Ajoute une nouvelle recette"""
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        recette_data = {
            'Recette': request.form.get('nom'),
            'Type de plat': request.form.get('type_plat'),
            'Origine': request.form.get('origine'),
            'Catégorie': request.form.get('categorie'),
            'Nombre de personnes': int(request.form.get('nb_personnes', 4)),
            'Temps de préparation': int(request.form.get('temps_preparation')),
            'Difficulté': request.form.get('difficulte'),
            'Note': request.form.get('note', ''),
            'Saison': request.form.getlist('saisons'),
            'Préparation': request.form.get('preparation', '').split('\n'),
            'Ingrédients': []
        }
        
        # Récupérer les ingrédients
        ingredients_noms = request.form.getlist('ingredient_nom')
        ingredients_quantites = request.form.getlist('ingredient_quantite')
        ingredients_unites = request.form.getlist('ingredient_unite')
        
        for nom, quantite, unite in zip(ingredients_noms, ingredients_quantites, ingredients_unites):
            if nom.strip():  # Ignorer les ingrédients vides
                recette_data['Ingrédients'].append({
                    'nom': nom.strip(),
                    'quantité': quantite.strip(),
                    'unité': unite.strip()
                })
        
        # Valider et sauvegarder
        try:
            with DatabaseManager() as db:
                recette_id = db.add_recette(recette_data)
                flash(f'Recette "{recette_data["Recette"]}" ajoutée avec succès!', 'success')
                return redirect(url_for('recettes.detail_recette', recette_id=recette_id))
        except Exception as e:
            flash(f'Erreur lors de l\'ajout: {str(e)}', 'error')
    
    return render_template('recettes/form.html',
                         recette=None,
                         categories=CATEGORIES,
                         difficultes=DIFFICULTES,
                         origines=ORIGINES,
                         saisons=SAISONS,
                         types_plats=TYPE_PLATS)

@recettes.route('/<int:recette_id>/edit', methods=['GET', 'POST'])
def edit_recette(recette_id):
    """Édite une recette existante"""
    
    with DatabaseManager() as db:
        recette = db.get_recette_by_id(recette_id)
        
        if not recette:
            flash('Recette introuvable', 'error')
            return redirect(url_for('recettes.list_recettes'))
        
        if request.method == 'POST':
            # Récupérer les données du formulaire (même logique que add_recette)
            recette_data = {
                'Recette': request.form.get('nom'),
                'Type de plat': request.form.get('type_plat'),
                'Origine': request.form.get('origine'),
                'Catégorie': request.form.get('categorie'),
                'Nombre de personnes': int(request.form.get('nb_personnes', 4)),
                'Temps de préparation': int(request.form.get('temps_preparation')),
                'Difficulté': request.form.get('difficulte'),
                'Note': request.form.get('note', ''),
                'Saison': request.form.getlist('saisons'),
                'Préparation': request.form.get('preparation', '').split('\n'),
                'Ingrédients': []
            }
            
            # Récupérer les ingrédients
            ingredients_noms = request.form.getlist('ingredient_nom')
            ingredients_quantites = request.form.getlist('ingredient_quantite')
            ingredients_unites = request.form.getlist('ingredient_unite')
            
            for nom, quantite, unite in zip(ingredients_noms, ingredients_quantites, ingredients_unites):
                if nom.strip():
                    recette_data['Ingrédients'].append({
                        'nom': nom.strip(),
                        'quantité': quantite.strip(),
                        'unité': unite.strip()
                    })
            
            # Sauvegarder les modifications
            try:
                db.update_recette(recette_id, recette_data)
                flash(f'Recette "{recette_data["Recette"]}" mise à jour avec succès!', 'success')
                return redirect(url_for('recettes.detail_recette', recette_id=recette_id))
            except Exception as e:
                flash(f'Erreur lors de la mise à jour: {str(e)}', 'error')
    
    return render_template('recettes/form.html',
                         recette=recette,
                         recette_id=recette_id,
                         categories=CATEGORIES,
                         difficultes=DIFFICULTES,
                         origines=ORIGINES,
                         saisons=SAISONS,
                         types_plats=TYPE_PLATS)

@recettes.route('/<int:recette_id>/delete', methods=['POST'])
def delete_recette(recette_id):
    """Supprime une recette"""
    
    with DatabaseManager() as db:
        if db.delete_recette(recette_id):
            flash('Recette supprimée avec succès', 'success')
        else:
            flash('Erreur lors de la suppression', 'error')
    
    return redirect(url_for('recettes.list_recettes'))

@recettes.route('/api/search')
def api_search():
    """API de recherche pour l'autocomplete"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify([])
    
    with DatabaseManager() as db:
        results = db.search_recettes(nom=query)
        suggestions = [{'id': r['Recette'], 'text': r['Recette']} for r in results[:10]]
    
    return jsonify(suggestions)