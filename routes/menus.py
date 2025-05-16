# routes/menus.py
# Routes pour la gestion des menus

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from core.database_manager import DatabaseManager, get_recettes_from_db
from core.generateur import generer_menu_semaine, creer_liste_courses, analyser_equilibrage_menu
from core.quantites import ajuster_menu_personnes
from datetime import datetime, timedelta

# Créer le blueprint
menus = Blueprint('menus', __name__)

@menus.route('/')
def list_menus():
    """Liste tous les menus sauvegardés"""
    
    page = request.args.get('page', 1, type=int)
    
    with DatabaseManager() as db:
        menus_data = db.get_all_menus(limit=20)
    
    return render_template('menus/list.html', menus=menus_data)

@menus.route('/generate', methods=['GET', 'POST'])
def generate_menu():
    """Génère un nouveau menu pour la semaine"""
    
    if request.method == 'POST':
        # Récupérer les options de génération
        inclure_weekend = request.form.get('inclure_weekend') == 'on'
        optimise = request.form.get('optimise') == 'on'
        nom_menu = request.form.get('nom_menu', '').strip()
        nb_personnes = int(request.form.get('nb_personnes', 4))
        
        # Générer un nom par défaut si vide
        if not nom_menu:
            date_str = datetime.now().strftime('%d/%m/%Y')
            nom_menu = f"Menu du {date_str}"
        
        try:
            # Récupérer les recettes et générer le menu
            recettes = get_recettes_from_db()
            
            if not recettes:
                flash('Aucune recette trouvée. Veuillez d\'abord ajouter des recettes.', 'error')
                return redirect(url_for('recettes.list_recettes'))
            
            # Générer le menu
            menu_dict, saison, rapport = generer_menu_semaine(
                recettes, 
                inclure_weekend=inclure_weekend,
                optimise=optimise
            )
            
            # Ajuster pour le nombre de personnes si différent de 4
            if nb_personnes != 4:
                menu_dict = ajuster_menu_personnes(menu_dict, nb_personnes)
            
            # Sauvegarder en base
            with DatabaseManager() as db:
                notes = f"Généré automatiquement pour la saison {saison}. "
                if optimise:
                    score = rapport.get('score', 'N/A')
                    notes += f"Menu optimisé (score: {score}). "
                notes += f"Contraintes respectées: {rapport.get('contraintes_respectees', {})}"
                
                menu_id = db.save_menu(menu_dict, nom_menu, nb_personnes, notes)
                
                flash(f'Menu "{nom_menu}" généré avec succès!', 'success')
                return redirect(url_for('menus.detail_menu', menu_id=menu_id))
                
        except Exception as e:
            flash(f'Erreur lors de la génération: {str(e)}', 'error')
    
    # GET - Afficher le formulaire de génération
    with DatabaseManager() as db:
        stats = db.get_statistiques()
    
    return render_template('menus/generate.html', stats=stats)

@menus.route('/<int:menu_id>')
def detail_menu(menu_id):
    """Affiche le détail d'un menu"""
    
    with DatabaseManager() as db:
        menu = db.get_menu_by_id(menu_id, as_dict=False)  # Récupérer l'objet SQLAlchemy
        
        if not menu:
            flash('Menu introuvable', 'error')
            return redirect(url_for('menus.list_menus'))
        
        # Convertir en dictionnaire pour la compatibilité
        menu_dict = menu.to_dict()
        
        # Récupérer le nombre de personnes pour l'ajustement si demandé
        nb_personnes_ajuste = request.args.get('personnes', type=int)
        
        # Ajuster les quantités si demandé
        if nb_personnes_ajuste and nb_personnes_ajuste != menu.nb_personnes:
            menu_dict = ajuster_menu_personnes(menu_dict, nb_personnes_ajuste)
            menu_info = {
                'nom': menu.nom,
                'nb_personnes': nb_personnes_ajuste,
                'date_creation': menu.date_creation,
                'notes': menu.notes
            }
        else:
            menu_info = {
                'nom': menu.nom,
                'nb_personnes': menu.nb_personnes,
                'date_creation': menu.date_creation,
                'notes': menu.notes
            }
        
        # Générer le rapport d'équilibrage actuel
        recettes_menu = []
        for jour, repas in menu_dict.items():
            for moment, recette in repas.items():
                if recette:
                    recettes_menu.append(recette)
        
        rapport = analyser_equilibrage_menu(menu_dict)
    
    return render_template('menus/detail.html',
                         menu=menu_dict,
                         menu_info=menu_info,
                         menu_id=menu_id,
                         rapport=rapport)

@menus.route('/<int:menu_id>/courses')
def liste_courses(menu_id):
    """Génère et affiche la liste de courses pour un menu"""
    
    with DatabaseManager() as db:
        menu = db.get_menu_by_id(menu_id, as_dict=False)
        
        if not menu:
            flash('Menu introuvable', 'error')
            return redirect(url_for('menus.list_menus'))
        
        menu_dict = menu.to_dict()
        
        # Récupérer le nombre de personnes pour l'ajustement
        nb_personnes = request.args.get('personnes', menu.nb_personnes, type=int)
        
        # Générer la liste de courses
        ingredients_totaux = creer_liste_courses(menu_dict, nb_personnes if nb_personnes != menu.nb_personnes else None)
    
    return render_template('menus/courses.html',
                         menu_info={
                             'nom': menu.nom,
                             'id': menu_id,
                             'nb_personnes': nb_personnes
                         },
                         ingredients=ingredients_totaux)

@menus.route('/<int:menu_id>/delete', methods=['POST'])
def delete_menu(menu_id):
    """Supprime un menu"""
    
    with DatabaseManager() as db:
        if db.delete_menu(menu_id):
            flash('Menu supprimé avec succès', 'success')
        else:
            flash('Erreur lors de la suppression', 'error')
    
    return redirect(url_for('menus.list_menus'))

@menus.route('/<int:menu_id>/duplicate', methods=['POST'])
def duplicate_menu(menu_id):
    """Duplique un menu existant"""
    
    with DatabaseManager() as db:
        menu_original = db.get_menu_by_id(menu_id, as_dict=False)
        
        if not menu_original:
            flash('Menu introuvable', 'error')
            return redirect(url_for('menus.list_menus'))
        
        # Créer un nouveau nom
        nouveau_nom = f"{menu_original.nom} - Copie"
        
        # Récupérer le dict du menu et le sauvegarder
        menu_dict = menu_original.to_dict()
        nouveau_menu_id = db.save_menu(menu_dict, nouveau_nom, menu_original.nb_personnes, 
                                      f"Copie du menu '{menu_original.nom}'")
        
        flash(f'Menu dupliqué sous le nom "{nouveau_nom}"', 'success')
        return redirect(url_for('menus.detail_menu', menu_id=nouveau_menu_id))

@menus.route('/api/<int:menu_id>/ingredients')
def api_ingredients(menu_id):
    """API pour récupérer les ingrédients d'un menu (AJAX)"""
    
    with DatabaseManager() as db:
        menu = db.get_menu_by_id(menu_id, as_dict=False)
        
        if not menu:
            return jsonify({'error': 'Menu introuvable'}), 404
        
        menu_dict = menu.to_dict()
        nb_personnes = request.args.get('personnes', menu.nb_personnes, type=int)
        
        ingredients = creer_liste_courses(menu_dict, nb_personnes if nb_personnes != menu.nb_personnes else None)
        
        # Formater pour JSON
        ingredients_formatted = {}
        for nom, details in ingredients.items():
            ingredients_formatted[nom] = {
                'quantite': details['quantite'],
                'unite': details['unite'],
                'recettes': details['recettes']
            }
    
    return jsonify(ingredients_formatted)