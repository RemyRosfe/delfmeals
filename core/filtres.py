# core/filtres.py
# Fonctions de filtrage avancé pour DelfMeals

def filtrer_recettes(recettes, **criteres):
    """
    Filtre une liste de recettes selon des critères multiples
    
    Exemples d'utilisation :
    - filtrer_recettes(recettes, difficulte="Rapide")
    - filtrer_recettes(recettes, categorie="Végétarien", temps_max=30)
    - filtrer_recettes(recettes, origines=["Cuisine asiatique", "Cuisine méditerranéenne"])
    """
    
    # Mapping des noms de paramètres vers les clés du dictionnaire
    mapping_cles = {
        'type_plat': 'Type de plat',
        'temps_preparation': 'Temps de préparation',
        'difficulte': 'Difficulté',
        'categorie': 'Catégorie',
        'origine': 'Origine',
        'nb_personnes': 'Nombre de personnes'
    }
    
    recettes_filtrees = []
    
    for recette in recettes:
        correspondance = True
        
        for cle, valeur in criteres.items():
            # Critères spéciaux
            if cle == 'temps_max':
                if recette.get('Temps de préparation', 0) > valeur:
                    correspondance = False
                    break
            elif cle == 'temps_min':
                if recette.get('Temps de préparation', 0) < valeur:
                    correspondance = False
                    break
            elif cle == 'origines':  # Pour filtrer sur plusieurs origines
                if recette.get('Origine') not in valeur:
                    correspondance = False
                    break
            elif cle == 'categories':  # Pour filtrer sur plusieurs catégories
                if recette.get('Catégorie') not in valeur:
                    correspondance = False
                    break
            elif cle == 'saisons':  # Pour filtrer sur plusieurs saisons
                if not any(saison in recette.get('Saison', []) for saison in valeur):
                    correspondance = False
                    break
            elif cle == 'recherche_texte':  # Recherche textuelle dans le nom
                if valeur.lower() not in recette.get('Recette', '').lower():
                    correspondance = False
                    break
            else:
                # Critères normaux avec mapping
                vraie_cle = mapping_cles.get(cle, cle)
                if recette.get(vraie_cle) != valeur:
                    correspondance = False
                    break
        
        if correspondance:
            recettes_filtrees.append(recette)
    
    return recettes_filtrees

def rechercher_recettes(recettes, terme_recherche="", **filtres):
    """
    Recherche avancée dans les recettes
    Combine recherche textuelle et filtres multiples
    """
    # Ajouter la recherche textuelle aux filtres
    if terme_recherche:
        filtres['recherche_texte'] = terme_recherche
    
    return filtrer_recettes(recettes, **filtres)

def grouper_par_critere(recettes, critere):
    """
    Groupe les recettes selon un critère donné
    """
    from collections import defaultdict
    
    groupes = defaultdict(list)
    
    mapping_cles = {
        'type_plat': 'Type de plat',
        'difficulte': 'Difficulté',
        'categorie': 'Catégorie',
        'origine': 'Origine'
    }
    
    vraie_cle = mapping_cles.get(critere, critere)
    
    for recette in recettes:
        valeur = recette.get(vraie_cle, 'Non défini')
        groupes[valeur].append(recette)
    
    return dict(groupes)

def trier_recettes(recettes, critere='Recette', reverse=False):
    """
    Trie les recettes selon un critère
    """
    mapping_cles = {
        'nom': 'Recette',
        'temps': 'Temps de préparation',
        'difficulte': 'Difficulté',
        'personnes': 'Nombre de personnes'
    }
    
    vraie_cle = mapping_cles.get(critere, critere)
    
    # Fonction de tri personnalisée pour gérer les types différents
    def cle_tri(recette):
        valeur = recette.get(vraie_cle, '')
        
        # Gérer les cas spéciaux
        if vraie_cle == 'Difficulté':
            ordre_difficulte = {'Rapide': 1, 'Normal': 2, 'Élaboré': 3}
            return ordre_difficulte.get(valeur, 99)
        elif isinstance(valeur, (int, float)):
            return valeur
        else:
            return str(valeur).lower()
    
    return sorted(recettes, key=cle_tri, reverse=reverse)