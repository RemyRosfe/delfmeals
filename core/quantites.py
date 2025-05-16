# core/quantites.py
# Gestion des ajustements de quantités pour DelfMeals

def ajuster_quantites_recette(recette, nb_personnes_souhaite):
    """
    Ajuste les quantités d'une recette selon le nombre de personnes souhaité
    """
    if not recette or nb_personnes_souhaite <= 0:
        return recette
    
    nb_personnes_original = recette.get('Nombre de personnes', 4)
    if nb_personnes_original <= 0:
        nb_personnes_original = 4  # Défaut si non spécifié
    
    ratio = nb_personnes_souhaite / nb_personnes_original
    
    # Créer une copie de la recette pour ne pas modifier l'originale
    recette_ajustee = recette.copy()
    recette_ajustee['Nombre de personnes'] = nb_personnes_souhaite
    recette_ajustee['Ingrédients'] = []
    
    # Ajuster chaque ingrédient
    for ingredient in recette['Ingrédients']:
        ingredient_ajuste = ingredient.copy()
        
        if ingredient['quantité']:
            try:
                # Convertir et ajuster la quantité
                quantite_originale = float(ingredient['quantité'])
                quantite_ajustee = quantite_originale * ratio
                
                # Arrondir intelligemment selon le type de quantité
                ingredient_ajuste['quantité'] = arrondir_quantite(quantite_ajustee)
                
            except ValueError:
                # Si impossible de convertir, garder tel quel
                pass
        
        recette_ajustee['Ingrédients'].append(ingredient_ajuste)
    
    return recette_ajustee

def arrondir_quantite(quantite):
    """
    Arrondit intelligemment une quantité selon sa valeur
    """
    if quantite < 0.1:
        # Très petites quantités (épices) : garder au minimum
        return str(round(quantite, 2))
    elif quantite < 1:
        # Petites quantités : 1 décimale
        return str(round(quantite, 1))
    elif quantite < 10:
        # Quantités moyennes : arrondir au 0.5 près
        return str(round(quantite * 2) / 2)
    else:
        # Grandes quantités : arrondir à l'entier
        return str(round(quantite))

def ajuster_menu_personnes(menu, nb_personnes):
    """
    Ajuste toutes les recettes d'un menu pour le nombre de personnes souhaité
    """
    menu_ajuste = {}
    
    for jour, repas in menu.items():
        menu_ajuste[jour] = {}
        for moment, recette in repas.items():
            if recette:
                menu_ajuste[jour][moment] = ajuster_quantites_recette(recette, nb_personnes)
            else:
                menu_ajuste[jour][moment] = None
    
    return menu_ajuste

def calculer_ratio_ajustement(nb_personnes_original, nb_personnes_souhaite):
    """
    Calcule le ratio d'ajustement entre deux nombres de personnes
    """
    if nb_personnes_original <= 0:
        nb_personnes_original = 4
    
    return nb_personnes_souhaite / nb_personnes_original

def convertir_quantite(quantite_str):
    """
    Convertit une chaîne de quantité en nombre si possible
    """
    if not quantite_str:
        return None
    
    try:
        # Gérer les fractions communes
        if '1/2' in quantite_str:
            return float(quantite_str.replace('1/2', '0.5'))
        elif '1/4' in quantite_str:
            return float(quantite_str.replace('1/4', '0.25'))
        elif '3/4' in quantite_str:
            return float(quantite_str.replace('3/4', '0.75'))
        else:
            return float(quantite_str)
    except ValueError:
        return None

def formatter_quantite_pour_affichage(quantite):
    """
    Formate une quantité pour l'affichage (ex: 1.5 -> "1.5", 2.0 -> "2")
    """
    if isinstance(quantite, str):
        return quantite
    
    # Convertir les fractions décimales communes en fractions
    if quantite == 0.5:
        return "1/2"
    elif quantite == 0.25:
        return "1/4"
    elif quantite == 0.75:
        return "3/4"
    elif quantite == int(quantite):
        return str(int(quantite))
    else:
        return str(quantite)