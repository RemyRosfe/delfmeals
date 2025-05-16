# utils/validation.py
# Fonctions de validation et utilités pour DelfMeals

from collections import Counter
from models.recette import CATEGORIES, DIFFICULTES, TYPE_PLATS, ORIGINES, SAISONS

def valider_recettes(recettes):
    """Valide une liste de recettes et retourne les erreurs trouvées"""
    erreurs = []
    
    for i, recette in enumerate(recettes):
        erreurs_recette = valider_recette_complete(recette, i+1)
        erreurs.extend(erreurs_recette)
    
    return erreurs

def valider_recette_complete(recette, numero=None):
    """Valide une recette complètement"""
    erreurs = []
    prefix = f"Recette {numero}: " if numero else ""
    
    # Vérifier les champs obligatoires
    champs_requis = ['Recette', 'Type de plat', 'Catégorie', 'Difficulté', 'Temps de préparation']
    for champ in champs_requis:
        if champ not in recette or not recette[champ]:
            erreurs.append(f"{prefix}Champ '{champ}' manquant ou vide")
    
    # Vérifier les types
    if 'Temps de préparation' in recette:
        if not isinstance(recette['Temps de préparation'], int) or recette['Temps de préparation'] <= 0:
            erreurs.append(f"{prefix}Temps de préparation doit être un entier positif")
    
    if 'Nombre de personnes' in recette:
        if not isinstance(recette['Nombre de personnes'], int) or recette['Nombre de personnes'] <= 0:
            erreurs.append(f"{prefix}Nombre de personnes doit être un entier positif")
    
    # Vérifier les valeurs dans les listes autorisées
    validations = [
        ('Type de plat', TYPE_PLATS),
        ('Catégorie', CATEGORIES),
        ('Difficulté', DIFFICULTES),
        ('Origine', ORIGINES)
    ]
    
    for champ, valeurs_autorisees in validations:
        if champ in recette and recette[champ]:
            if recette[champ] not in valeurs_autorisees:
                erreurs.append(f"{prefix}{champ} '{recette[champ]}' non autorisé")
    
    # Vérifier les saisons
    if 'Saison' in recette:
        if not isinstance(recette['Saison'], list):
            erreurs.append(f"{prefix}Le champ 'Saison' doit être une liste")
        else:
            for saison in recette['Saison']:
                if saison not in SAISONS:
                    erreurs.append(f"{prefix}Saison '{saison}' non autorisée")
    
    # Vérifier les ingrédients
    if 'Ingrédients' in recette:
        if not isinstance(recette['Ingrédients'], list):
            erreurs.append(f"{prefix}Le champ 'Ingrédients' doit être une liste")
        else:
            for j, ing in enumerate(recette['Ingrédients']):
                if not isinstance(ing, dict):
                    erreurs.append(f"{prefix}Ingrédient {j+1} doit être un dictionnaire")
                else:
                    if 'nom' not in ing or not ing['nom']:
                        erreurs.append(f"{prefix}Ingrédient {j+1}: 'nom' manquant")
                    if 'quantité' not in ing:
                        erreurs.append(f"{prefix}Ingrédient {j+1}: 'quantité' manquant")
                    if 'unité' not in ing:
                        erreurs.append(f"{prefix}Ingrédient {j+1}: 'unité' manquant")
    
    # Vérifier la préparation
    if 'Préparation' in recette:
        if not isinstance(recette['Préparation'], list):
            erreurs.append(f"{prefix}Le champ 'Préparation' doit être une liste")
        elif not recette['Préparation']:
            erreurs.append(f"{prefix}La préparation ne peut pas être vide")
    
    return erreurs

def analyser_repartition_recettes(recettes):
    """Analyse la répartition des recettes selon différents critères"""
    if not recettes:
        return {}
    
    analyse = {
        'total': len(recettes),
        'par_categorie': Counter(r.get('Catégorie') for r in recettes),
        'par_difficulte': Counter(r.get('Difficulté') for r in recettes),
        'par_origine': Counter(r.get('Origine') for r in recettes),
        'par_type_plat': Counter(r.get('Type de plat') for r in recettes),
        'temps_moyen': sum(r.get('Temps de préparation', 0) for r in recettes) / len(recettes),
        'personnes_moyen': sum(r.get('Nombre de personnes', 4) for r in recettes) / len(recettes)
    }
    
    # Analyser les saisons
    toutes_saisons = []
    for recette in recettes:
        toutes_saisons.extend(recette.get('Saison', []))
    analyse['par_saison'] = Counter(toutes_saisons)
    
    return analyse

def verifier_coherence_base(recettes):
    """Vérifie la cohérence globale de la base de recettes"""
    problemes = []
    
    # Vérifier qu'on a assez de variété pour générer des menus
    plats_principaux = [r for r in recettes if r.get('Type de plat') == 'Plats']
    
    if len(plats_principaux) < 14:
        problemes.append(f"Seulement {len(plats_principaux)} plats principaux (14 recommandés pour une semaine)")
    
    # Vérifier l'équilibre des catégories
    categories = Counter(r.get('Catégorie') for r in plats_principaux)
    
    if not categories.get('Viande rouge'):
        problemes.append("Aucune recette de viande rouge")
    if not categories.get('Volaille'):
        problemes.append("Aucune recette de volaille")
    if not categories.get('Poisson'):
        problemes.append("Aucune recette de poisson")
    if not categories.get('Végétarien'):
        problemes.append("Aucune recette végétarienne")
    
    # Vérifier l'équilibre des difficultés
    difficultes = Counter(r.get('Difficulté') for r in plats_principaux)
    
    if not difficultes.get('Rapide'):
        problemes.append("Aucune recette rapide pour les midis")
    
    # Vérifier les temps pour les midis
    rapides_midi = [r for r in plats_principaux 
                   if r.get('Difficulté') == 'Rapide' or r.get('Temps de préparation', 0) <= 30]
    
    if len(rapides_midi) < 7:
        problemes.append(f"Seulement {len(rapides_midi)} recettes adaptées aux midis (7 recommandés)")
    
    # Vérifier la diversité des origines
    origines = Counter(r.get('Origine') for r in plats_principaux)
    
    if len(origines) < 3:
        problemes.append(f"Peu de diversité dans les origines ({len(origines)} différentes)")
    
    return problemes

def generer_rapport_base(recettes):
    """Génère un rapport complet sur la base de recettes"""
    print("📊 RAPPORT SUR LA BASE DE RECETTES")
    print("=" * 50)
    
    # Validation
    erreurs = valider_recettes(recettes)
    if erreurs:
        print(f"\n❌ ERREURS DÉTECTÉES ({len(erreurs)}):")
        for erreur in erreurs[:10]:  # Afficher max 10 erreurs
            print(f"  • {erreur}")
        if len(erreurs) > 10:
            print(f"  ... et {len(erreurs) - 10} autres erreurs")
    else:
        print(f"\n✅ Toutes les recettes sont correctement formatées")
    
    # Analyse de répartition
    analyse = analyser_repartition_recettes(recettes)
    
    print(f"\n📈 RÉPARTITION DES RECETTES:")
    print(f"  • Total: {analyse['total']} recettes")
    print(f"  • Temps moyen: {analyse['temps_moyen']:.1f} min")
    print(f"  • Nombre de personnes moyen: {analyse['personnes_moyen']:.1f}")
    
    print(f"\n🍖 Par catégorie:")
    for categorie, count in analyse['par_categorie'].most_common():
        pourcentage = (count / analyse['total']) * 100
        print(f"  • {categorie:<15} {count:3d} ({pourcentage:4.1f}%)")
    
    print(f"\n⚡ Par difficulté:")
    for difficulte, count in analyse['par_difficulte'].most_common():
        pourcentage = (count / analyse['total']) * 100
        print(f"  • {difficulte:<10} {count:3d} ({pourcentage:4.1f}%)")
    
    print(f"\n🌍 Par origine:")
    for origine, count in analyse['par_origine'].most_common():
        pourcentage = (count / analyse['total']) * 100
        print(f"  • {origine:<25} {count:3d} ({pourcentage:4.1f}%)")
    
    # Vérification de cohérence
    problemes = verifier_coherence_base(recettes)
    
    if problemes:
        print(f"\n⚠️  PROBLÈMES DE COHÉRENCE:")
        for probleme in problemes:
            print(f"  • {probleme}")
    else:
        print(f"\n✅ La base de recettes est cohérente pour la génération de menus")
    
    return analyse, erreurs, problemes

def nettoyer_recette(recette):
    """Nettoie et normalise une recette"""
    # Créer une copie pour ne pas modifier l'original
    recette_nettoyee = recette.copy()
    
    # Normaliser les champs texte
    if 'Recette' in recette_nettoyee:
        recette_nettoyee['Recette'] = recette_nettoyee['Recette'].strip()
    
    if 'Note' in recette_nettoyee:
        recette_nettoyee['Note'] = recette_nettoyee['Note'].strip()
    
    # Assurer les valeurs par défaut
    if 'Nombre de personnes' not in recette_nettoyee:
        recette_nettoyee['Nombre de personnes'] = 4
    
    if 'Saison' not in recette_nettoyee:
        recette_nettoyee['Saison'] = ['Toutes saisons']
    elif not isinstance(recette_nettoyee['Saison'], list):
        recette_nettoyee['Saison'] = [recette_nettoyee['Saison']]
    
    if 'Préparation' not in recette_nettoyee:
        recette_nettoyee['Préparation'] = []
    elif not isinstance(recette_nettoyee['Préparation'], list):
        # Convertir string en liste si nécessaire
        recette_nettoyee['Préparation'] = [recette_nettoyee['Préparation']]
    
    if 'Ingrédients' not in recette_nettoyee:
        recette_nettoyee['Ingrédients'] = []
    
    # Nettoyer les ingrédients
    ingredients_nettoyes = []
    for ing in recette_nettoyee.get('Ingrédients', []):
        if isinstance(ing, dict):
            ing_propre = {
                'nom': ing.get('nom', '').strip(),
                'quantité': ing.get('quantité', '').strip(),
                'unité': ing.get('unité', '').strip()
            }
            ingredients_nettoyes.append(ing_propre)
    
    recette_nettoyee['Ingrédients'] = ingredients_nettoyes
    
    return recette_nettoyee