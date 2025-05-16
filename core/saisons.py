# core/saisons.py
# Gestion intelligente des saisons pour DelfMeals

import datetime

def detecter_saison_actuelle():
    """Détecte la saison actuelle et les saisons de transition"""
    maintenant = datetime.datetime.now()
    mois = maintenant.month
    jour = maintenant.day
    
    # Définir les saisons principales
    if mois in [12, 1, 2]:
        saison_principale = "Hiver"
    elif mois in [3, 4, 5]:
        saison_principale = "Printemps"
    elif mois in [6, 7, 8]:
        saison_principale = "Été"
    else:  # 9, 10, 11
        saison_principale = "Automne"
    
    # Gestion des périodes de transition (à partir du 15 du mois)
    saisons_disponibles = [saison_principale]
    
    # Transitions vers la saison suivante
    if (mois == 2 and jour >= 15) or (mois == 3 and jour <= 15):
        saisons_disponibles = ["Hiver", "Printemps"]
    elif (mois == 5 and jour >= 15) or (mois == 6 and jour <= 15):
        saisons_disponibles = ["Printemps", "Été"]
    elif (mois == 8 and jour >= 15) or (mois == 9 and jour <= 15):
        saisons_disponibles = ["Été", "Automne"]
    elif (mois == 11 and jour >= 15) or (mois == 12 and jour <= 15):
        saisons_disponibles = ["Automne", "Hiver"]
    
    return saison_principale, saisons_disponibles

def filtrer_par_saison(recettes, saisons_disponibles):
    """Filtre les recettes selon les saisons disponibles"""
    recettes_saison = []
    
    for recette in recettes:
        # Une recette est valide si elle contient "Toutes saisons" 
        # ou si une de ses saisons correspond aux saisons disponibles
        if "Toutes saisons" in recette['Saison']:
            recettes_saison.append(recette)
        else:
            # Vérifier s'il y a intersection entre les saisons de la recette et les saisons disponibles
            if any(saison in saisons_disponibles for saison in recette['Saison']):
                recettes_saison.append(recette)
    
    return recettes_saison

def get_saison_pour_date(date):
    """Retourne la saison pour une date donnée"""
    mois = date.month
    
    if mois in [12, 1, 2]:
        return "Hiver"
    elif mois in [3, 4, 5]:
        return "Printemps"
    elif mois in [6, 7, 8]:
        return "Été"
    else:
        return "Automne"

def est_periode_transition():
    """Vérifie si on est dans une période de transition entre saisons"""
    _, saisons_disponibles = detecter_saison_actuelle()
    return len(saisons_disponibles) > 1