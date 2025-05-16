# models/recette.py
# Structure des données et constantes pour DelfMeals

# Constantes pour les champs prédéfinis
TYPE_PLATS = ["Apéro", "Entrées", "Plats", "Desserts", "Boissons", "Brunch et petit déj"]

ORIGINES = [
    "Cuisine française", 
    "Cuisine italienne", 
    "Cuisine méditerranéenne", 
    "Cuisine indienne", 
    "Cuisine asiatique", 
    "Cuisine américaine", 
    "Cuisine du Maghreb", 
    "Autre"
]

CATEGORIES = ["Viande rouge", "Volaille", "Poisson", "Végétarien"]

DIFFICULTES = ["Rapide", "Normal", "Élaboré"]

SAISONS = ["Toutes saisons", "Hiver", "Printemps", "Été", "Automne"]

# Schéma de recette type pour validation
SCHEMA_RECETTE = {
    "Recette": str,
    "Type de plat": str,
    "Origine": str,
    "Catégorie": str,
    "Nombre de personnes": int,
    "Temps de préparation": int,
    "Difficulté": str,
    "Saison": list,
    "Préparation": list,
    "Ingrédients": list,
    "Note": str
}

# Schéma d'ingrédient
SCHEMA_INGREDIENT = {
    "nom": str,
    "quantité": str,
    "unité": str
}

def valider_recette(recette):
    """Valide qu'une recette respecte le schéma attendu"""
    errors = []
    
    # Vérifier les champs obligatoires
    champs_requis = ['Recette', 'Type de plat', 'Catégorie', 'Difficulté', 'Temps de préparation']
    for champ in champs_requis:
        if champ not in recette or not recette[champ]:
            errors.append(f"Champ '{champ}' manquant ou vide")
    
    # Vérifier les valeurs dans les listes autorisées
    if 'Type de plat' in recette and recette['Type de plat'] not in TYPE_PLATS:
        errors.append(f"Type de plat '{recette['Type de plat']}' non autorisé")
    
    if 'Catégorie' in recette and recette['Catégorie'] not in CATEGORIES:
        errors.append(f"Catégorie '{recette['Catégorie']}' non autorisée")
    
    if 'Difficulté' in recette and recette['Difficulté'] not in DIFFICULTES:
        errors.append(f"Difficulté '{recette['Difficulté']}' non autorisée")
    
    if 'Origine' in recette and recette['Origine'] and recette['Origine'] not in ORIGINES:
        errors.append(f"Origine '{recette['Origine']}' non autorisée")
    
    # Vérifier les saisons
    if 'Saison' in recette:
        if not isinstance(recette['Saison'], list):
            errors.append("Le champ 'Saison' doit être une liste")
        else:
            for saison in recette['Saison']:
                if saison not in SAISONS:
                    errors.append(f"Saison '{saison}' non autorisée")
    
    # Vérifier les ingrédients
    if 'Ingrédients' in recette:
        if not isinstance(recette['Ingrédients'], list):
            errors.append("Le champ 'Ingrédients' doit être une liste")
        else:
            for i, ing in enumerate(recette['Ingrédients']):
                if not isinstance(ing, dict):
                    errors.append(f"Ingrédient {i+1} doit être un dictionnaire")
                else:
                    if 'nom' not in ing:
                        errors.append(f"Ingrédient {i+1}: 'nom' manquant")
    
    return errors

def creer_recette_vide():
    """Crée une structure de recette vide avec les champs par défaut"""
    return {
        "Recette": "",
        "Type de plat": "Plats",
        "Origine": "",
        "Catégorie": "",
        "Nombre de personnes": 4,
        "Temps de préparation": 30,
        "Difficulté": "Normal",
        "Saison": ["Toutes saisons"],
        "Préparation": [],
        "Ingrédients": [],
        "Note": ""
    }

def creer_ingredient_vide():
    """Crée un ingrédient vide"""
    return {
        "nom": "",
        "quantité": "",
        "unité": ""
    }