# core/generateur.py
# Génération de menus équilibrés avec conservation des IDs

import datetime
import random
from collections import defaultdict, Counter
from core.database_manager import get_recettes_from_db
from core.saisons import detecter_saison_actuelle, filtrer_par_saison
from core.filtres import filtrer_recettes

def generer_menu_semaine(recettes=None, inclure_weekend=True, optimise=False, tentatives=3):
    """
    Génère un menu équilibré pour la semaine (14 plats principaux)
    
    Args:
        recettes: Liste de recettes (ou None pour récupérer de la DB)
        inclure_weekend: Inclure sam/dim
        optimise: Générer plusieurs menus et choisir le meilleur
        tentatives: Nombre de tentatives pour l'optimisation
    
    Returns:
        (menu_dict, saison, rapport) where menu_dict contient des recettes avec IDs
    """
    
    # Récupérer les recettes si pas fournies
    if recettes is None:
        recettes = get_recettes_from_db()
    
    # S'assurer que les recettes ont leurs IDs
    recettes_with_ids = []
    for recette in recettes:
        if isinstance(recette, dict):
            # Si c'est déjà un dict, vérifier qu'il a un ID
            if 'id' not in recette:
                # Essayer de récupérer l'ID depuis la DB
                # Pour l'instant, on garde sans ID mais on devra corriger ça
                pass
            recettes_with_ids.append(recette)
        else:
            # Si c'est un objet SQLAlchemy, convertir en dict avec ID
            recette_dict = recette.to_dict()
            recette_dict['id'] = recette.id
            recettes_with_ids.append(recette_dict)
    
    recettes = recettes_with_ids
    
    # Détection de la saison actuelle
    saison_principale, saisons_disponibles = detecter_saison_actuelle()
    
    # Filtrer les recettes selon la saison
    recettes_saison = filtrer_par_saison(recettes, saisons_disponibles)
    plats_principaux = [r for r in recettes_saison if r['Type de plat'] == 'Plats']
    
    if not plats_principaux:
        raise ValueError("Aucun plat principal disponible pour la saison courante")
    
    # Générer le/les menus
    if optimise and tentatives > 1:
        menu_dict, rapport = _generer_menu_optimise(plats_principaux, inclure_weekend, tentatives)
    else:
        menu_dict, rapport = _generer_menu_simple(plats_principaux, inclure_weekend)
    
    # S'assurer que toutes les recettes dans le menu ont leurs IDs
    _verifier_ids_menu(menu_dict)
    
    return menu_dict, saison_principale, rapport

def _generer_menu_simple(plats_principaux, inclure_weekend):
    """Génère un seul menu avec l'algorithme d'équilibrage"""
    
    # Séparer les recettes par contraintes temporelles
    recettes_midi = filtrer_recettes(plats_principaux, temps_max=30)
    recettes_soir_semaine = [r for r in plats_principaux if r['Difficulté'] in ['Rapide', 'Normal']]
    recettes_weekend = plats_principaux
    
    # Organiser par catégories pour l'équilibrage
    par_origine = defaultdict(list)
    par_categorie = defaultdict(list)
    
    for recette in plats_principaux:
        par_origine[recette['Origine']].append(recette)
        par_categorie[recette['Catégorie']].append(recette)
    
    # Générer le menu
    menu = {}
    jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    jours_weekend = ["Samedi", "Dimanche"]
    jours_total = jours_semaine + (jours_weekend if inclure_weekend else [])
    
    # Compteurs pour l'équilibrage
    recettes_utilisees = []  # Liste pour éviter les répétitions
    recettes_ids_utilises = set()  # Set pour vérification rapide des ID
    elabores_utilises = 0
    compteur_origines = defaultdict(int)
    compteur_categories = defaultdict(int)
    viande_rouge_utilisee = False
    volaille_utilisee = False
    viandes_utilisees = 0
    poissons_utilises = 0  # NOUVEAU: Compteur pour les poissons
    
    # Pool pondéré pour surpondérer asiatique et méditerranéenne
    def creer_pool_pondere(pool_recettes):
        pool_pondere = []
        for recette in pool_recettes:
            pool_pondere.append(recette)
            # Surpondération x2 pour asiatique et méditerranéenne
            if recette['Origine'] in ['Cuisine asiatique', 'Cuisine méditerranéenne']:
                pool_pondere.append(recette)
        return pool_pondere
    
    # Phase 1: S'assurer d'avoir nos 2 viandes (1 rouge + 1 volaille)
    viandes_a_placer = []
    if par_categorie['Viande rouge']:
        viandes_a_placer.append(random.choice(par_categorie['Viande rouge']))
    if par_categorie['Volaille']:
        viandes_a_placer.append(random.choice(par_categorie['Volaille']))
    
    # Mélanger l'ordre de placement
    repas_ordre = []
    for jour in jours_total:
        repas_ordre.append((jour, "midi"))
        repas_ordre.append((jour, "soir"))
    random.shuffle(repas_ordre)
    
    # Placer les viandes en priorité
    viandes_placees = 0
    for jour, moment in repas_ordre:
        if viandes_placees < len(viandes_a_placer):
            if moment == "midi":
                pool = recettes_midi
            elif jour in jours_semaine:
                pool = recettes_soir_semaine
            else:
                pool = recettes_weekend
            
            viande_candidate = None
            for viande in viandes_a_placer:
                # Vérification stricte: pas dans les recettes utilisées ET pas d'ID déjà utilisé
                if (viande in pool and 
                    viande not in recettes_utilisees and 
                    viande.get('id') not in recettes_ids_utilises):
                    viande_candidate = viande
                    break
            
            if viande_candidate:
                if jour not in menu:
                    menu[jour] = {}
                menu[jour][moment] = viande_candidate
                recettes_utilisees.append(viande_candidate)
                if viande_candidate.get('id'):
                    recettes_ids_utilises.add(viande_candidate['id'])
                viandes_a_placer.remove(viande_candidate)
                viandes_placees += 1
                
                # Mettre à jour les compteurs
                compteur_origines[viande_candidate['Origine']] += 1
                compteur_categories[viande_candidate['Catégorie']] += 1
                if viande_candidate['Catégorie'] == 'Viande rouge':
                    viande_rouge_utilisee = True
                    viandes_utilisees += 1
                elif viande_candidate['Catégorie'] == 'Volaille':
                    volaille_utilisee = True
                    viandes_utilisees += 1
    
    # Phase 2: Compléter le menu
    def choisir_recette_equilibree(pool_recettes, moment, jour):
        # Déclarer toutes les variables nonlocal au début
        nonlocal elabores_utilises, viandes_utilisees, viande_rouge_utilisee, volaille_utilisee, poissons_utilises
        
        pool_pondere = creer_pool_pondere(pool_recettes)
        candidats = []
        
        for recette in pool_pondere:
            # CORRECTION 1: Vérification stricte des répétitions (par ID et par objet)
            if recette in recettes_utilisees:
                continue
            if recette.get('id') and recette['id'] in recettes_ids_utilises:
                continue
            
            # Contrainte cuisine américaine (max 1/semaine)
            if recette['Origine'] == 'Cuisine américaine' and compteur_origines['Cuisine américaine'] >= 1:
                continue
            
            # Contrainte sur les viandes (exactement 2/semaine)
            if recette['Catégorie'] in ['Viande rouge', 'Volaille']:
                if viandes_utilisees >= 2:
                    continue
                if recette['Catégorie'] == 'Viande rouge' and viande_rouge_utilisee:
                    continue
                if recette['Catégorie'] == 'Volaille' and volaille_utilisee:
                    continue
            
            # NOUVEAUTÉ: Contrainte sur les poissons (max 2/semaine)
            if recette['Catégorie'] == 'Poisson' and poissons_utilises >= 2:
                continue
            
            # Contrainte élaborés (max 2, weekend seulement)
            if recette['Difficulté'] == 'Élaboré':
                if jour not in jours_weekend or elabores_utilises >= 2:
                    continue
            
            # Éviter trop de répétitions de catégories (max 3 de la même)
            if compteur_categories[recette['Catégorie']] >= 3:
                continue
            
            candidats.append(recette)
        
        # Si aucun candidat, relâcher les contraintes progressivement
        if not candidats:
            # Première tentative: autoriser plus de la même catégorie
            for recette in pool_pondere:
                if (recette not in recettes_utilisees and 
                    not (recette.get('id') and recette['id'] in recettes_ids_utilises)):
                    candidats.append(recette)
            
            # Si toujours rien, prendre n'importe quoi d'unique
            if not candidats:
                candidats = [r for r in pool_pondere 
                           if r not in recettes_utilisees and 
                           not (r.get('id') and r['id'] in recettes_ids_utilises)]
                
                # En dernier recours, prendre quelque chose
                if not candidats:
                    candidats = pool_pondere
        
        # Choisir une recette
        if candidats:
            # Éliminer les doublons du pool pondéré
            candidats_uniques = []
            ids_vus = set()
            for candidat in candidats:
                candidat_id = candidat.get('id')
                if candidat_id:
                    if candidat_id not in ids_vus:
                        candidats_uniques.append(candidat)
                        ids_vus.add(candidat_id)
                else:
                    # Si pas d'ID, vérifier par nom de recette
                    nom_recette = candidat.get('Recette', '')
                    if nom_recette not in [c.get('Recette', '') for c in candidats_uniques]:
                        candidats_uniques.append(candidat)
            
            if candidats_uniques:
                recette = random.choice(candidats_uniques)
                
                # Mettre à jour les compteurs et listes
                recettes_utilisees.append(recette)
                if recette.get('id'):
                    recettes_ids_utilises.add(recette['id'])
                    
                compteur_origines[recette['Origine']] += 1
                compteur_categories[recette['Catégorie']] += 1
                
                if recette['Catégorie'] == 'Viande rouge':
                    viande_rouge_utilisee = True
                    viandes_utilisees += 1
                elif recette['Catégorie'] == 'Volaille':
                    volaille_utilisee = True
                    viandes_utilisees += 1
                elif recette['Catégorie'] == 'Poisson':  # NOUVEAU: Compter les poissons
                    poissons_utilises += 1
                
                if recette['Difficulté'] == 'Élaboré':
                    elabores_utilises += 1
                
                return recette
        
        return None
    
    # Compléter tous les repas
    for jour in jours_total:
        if jour not in menu:
            menu[jour] = {}
        
        # Midi
        if "midi" not in menu[jour]:
            midi = choisir_recette_equilibree(recettes_midi, "midi", jour)
            menu[jour]["midi"] = midi
        
        # Soir
        if "soir" not in menu[jour]:
            if jour in jours_weekend:
                pool_soir = recettes_weekend
            else:
                pool_soir = recettes_soir_semaine
            soir = choisir_recette_equilibree(pool_soir, "soir", jour)
            menu[jour]["soir"] = soir
    
    # Générer le rapport
    rapport = analyser_equilibrage_menu(menu)
    rapport['contraintes_respectees'] = {
        'viandes': viandes_utilisees == 2 and viande_rouge_utilisee and volaille_utilisee,
        'americaine': compteur_origines['Cuisine américaine'] <= 1,
        'elabores': elabores_utilises <= 2,
        'poissons': poissons_utilises <= 2,  # NOUVEAU: Validation des poissons
        'recettes_uniques': len(recettes_utilisees) == len(set(r.get('id') or r.get('Recette') for r in recettes_utilisees))  # NOUVEAU: Validation unicité
    }
    
    return menu, rapport

def _generer_menu_optimise(plats_principaux, inclure_weekend, tentatives):
    """Génère plusieurs menus et sélectionne le meilleur"""
    
    meilleur_menu = None
    meilleur_score = -1
    meilleur_rapport = None
    
    for i in range(tentatives):
        menu, rapport = _generer_menu_simple(plats_principaux, inclure_weekend)
        score = _calculer_score_equilibrage(rapport)
        
        if score > meilleur_score:
            meilleur_score = score
            meilleur_menu = menu
            meilleur_rapport = rapport
    
    meilleur_rapport['score'] = meilleur_score
    return meilleur_menu, meilleur_rapport

def _calculer_score_equilibrage(rapport):
    """Calcule un score d'équilibrage pour un menu (0-100)"""
    score = 100
    
    # Pénalités pour non-respect des contraintes
    contraintes = rapport.get('contraintes_respectees', {})
    if not contraintes.get('viandes'):
        score -= 20
    if not contraintes.get('americaine'):
        score -= 15
    if not contraintes.get('elabores'):
        score -= 10
    if not contraintes.get('poissons'):  # NOUVEAU: Pénalité pour trop de poissons
        score -= 15
    if not contraintes.get('recettes_uniques'):  # NOUVEAU: Pénalité pour répétitions
        score -= 25
    
    # Bonus pour diversité des origines
    nb_origines = len(rapport.get('origines', {}))
    score += min(nb_origines * 2, 15)
    
    # Bonus pour équilibre des catégories
    categories = rapport.get('categories', {})
    if categories:
        vals = list(categories.values())
        ecart_categories = max(vals) - min(vals)
        score -= ecart_categories * 2
    
    # Bonus pour temps de préparation équilibré
    temps_moyen = rapport.get('temps_moyen', 35)
    if 30 <= temps_moyen <= 40:
        score += 10
    elif temps_moyen < 20 or temps_moyen > 60:
        score -= 15
    
    return max(0, min(100, score))

def analyser_equilibrage_menu(menu):
    """Analyse l'équilibrage d'un menu généré"""
    
    # Collecte des données
    origines = []
    categories = []
    difficultes = []
    temps_total = 0
    nb_plats = 0
    
    for jour, repas in menu.items():
        for moment, recette in repas.items():
            if recette:
                origines.append(recette['Origine'])
                categories.append(recette['Catégorie'])
                difficultes.append(recette['Difficulté'])
                temps_total += recette.get('Temps de préparation', 0)
                nb_plats += 1
    
    # Analyses
    compteur_origines = Counter(origines)
    compteur_categories = Counter(categories)
    compteur_difficultes = Counter(difficultes)
    
    return {
        'total_plats': nb_plats,
        'temps_total': temps_total,
        'temps_moyen': temps_total / nb_plats if nb_plats > 0 else 0,
        'origines': compteur_origines,
        'categories': compteur_categories,
        'difficultes': compteur_difficultes
    }

def creer_liste_courses(menu, nb_personnes_ajuste=None):
    """Crée une liste de courses consolidée à partir du menu"""
    from core.quantites import ajuster_menu_personnes
    
    # Ajuster le menu si nécessaire
    if nb_personnes_ajuste:
        menu = ajuster_menu_personnes(menu, nb_personnes_ajuste)
    
    ingredients_totaux = defaultdict(lambda: {"quantite": 0, "unite": "", "recettes": []})
    
    # Parcourir tous les repas du menu
    for jour, repas in menu.items():
        for moment, recette in repas.items():
            if recette:
                for ingredient in recette.get('Ingrédients', []):
                    nom = ingredient['nom']
                    
                    # Ajouter la recette à la liste des utilisations
                    usage = f"{recette['Recette']} ({jour} {moment})"
                    if usage not in ingredients_totaux[nom]["recettes"]:
                        ingredients_totaux[nom]["recettes"].append(usage)
                    
                    # Gérer les quantités si elles existent
                    if ingredient.get('quantité'):
                        try:
                            qte = float(ingredient['quantité'])
                            ingredients_totaux[nom]["quantite"] += qte
                            
                            # Garder l'unité (prendre la première rencontrée)
                            if not ingredients_totaux[nom]["unite"] and ingredient.get('unité'):
                                ingredients_totaux[nom]["unite"] = ingredient['unité']
                        except (ValueError, TypeError):
                            pass
    
    return dict(ingredients_totaux)

def _verifier_ids_menu(menu):
    """Vérifie que toutes les recettes du menu ont des IDs"""
    for jour, repas in menu.items():
        for moment, recette in repas.items():
            if recette and 'id' not in recette:
                # Log ou warning que l'ID manque
                print(f"Warning: Recette '{recette.get('Recette', 'Unknown')}' sans ID dans {jour} {moment}")