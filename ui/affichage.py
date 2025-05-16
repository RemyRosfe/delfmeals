# ui/affichage.py
# Interface console pour DelfMeals

from collections import defaultdict

def afficher_recette(recette):
    """Affiche une recette de façon formatée et lisible"""
    print(f"{'=' * 60}")
    print(f"🍽️  {recette['Recette']}")
    print(f"{'=' * 60}")
    print(f"📍 {recette['Origine']} | 🍖 {recette['Catégorie']}")
    print(f"⏱️  {recette['Temps de préparation']} min | 👥 {recette['Nombre de personnes']} personnes")
    print(f"📊 Difficulté: {recette['Difficulté']} | 🌍 Saison: {', '.join(recette['Saison'])}")
    
    if recette.get('Note'):
        print(f"💡 {recette['Note']}")
    
    print(f"\n📋 INGRÉDIENTS")
    print("-" * 30)
    for ingredient in recette['Ingrédients']:
        ligne = afficher_ingredient(ingredient)
        print(f"  • {ligne}")
    
    print(f"\n👨‍🍳 PRÉPARATION")
    print("-" * 30)
    for i, etape in enumerate(recette['Préparation'], 1):
        print(f"{i:2d}. {etape}")
    
    print("\n")

def afficher_ingredient(ingredient):
    """Formate intelligemment l'affichage d'un ingrédient"""
    if ingredient['quantité']:
        if ingredient['unité']:
            # Unités qui ne prennent pas "de"
            unites_sans_de = ['pièces', 'pièce', 'tranches', 'tranche', 'cuillères à soupe', 'cuillères à café']
            
            if ingredient['unité'] in unites_sans_de:
                return f"{ingredient['quantité']} {ingredient['unité']} {ingredient['nom']}"
            else:
                return f"{ingredient['quantité']} {ingredient['unité']} de {ingredient['nom']}"
        else:
            # Cas où on a une quantité mais pas d'unité (comme 3 œufs)
            return f"{ingredient['quantité']} {ingredient['nom']}"
    else:
        return ingredient['nom']

def afficher_recette_ajustee(recette, nb_personnes=None):
    """
    Affiche une recette avec possibilité d'ajustement des quantités
    """
    from core.quantites import ajuster_quantites_recette
    
    if nb_personnes and nb_personnes != recette.get('Nombre de personnes', 4):
        recette_a_afficher = ajuster_quantites_recette(recette, nb_personnes)
        print(f"📏 Quantités ajustées pour {nb_personnes} personnes (original: {recette.get('Nombre de personnes', 4)})")
    else:
        recette_a_afficher = recette
    
    afficher_recette(recette_a_afficher)

def lister_recettes(recettes):
    """Affiche la liste de toutes les recettes avec leurs principales caractéristiques"""
    print(f"📚 BASE DE DONNÉES - {len(recettes)} recettes disponibles")
    print("=" * 80)
    for i, recette in enumerate(recettes, 1):
        saisons_str = ", ".join(recette['Saison'])
        print(f"{i:2d}. {recette['Recette']:<30} | {recette['Catégorie']:<12} | {recette['Difficulté']:<10} | {recette['Temps de préparation']:2d}min | {saisons_str}")
    print()

def afficher_menu_semaine(menu):
    """Affiche le menu de la semaine de façon structurée"""
    print("\n" + "="*60)
    print("🗓️  MENU DE LA SEMAINE")
    print("="*60)
    
    for jour, repas in menu.items():
        print(f"\n📅 {jour.upper()}")
        print("-" * 30)
        
        # Midi
        if repas["midi"]:
            print(f"🌅 Midi : {repas['midi']['Recette']}")
            print(f"   └─ {repas['midi']['Catégorie']} | {repas['midi']['Temps de préparation']}min | {repas['midi']['Difficulté']}")
        else:
            print(f"🌅 Midi : ⚠️  Aucune recette disponible")
        
        # Soir
        if repas["soir"]:
            print(f"🌙 Soir : {repas['soir']['Recette']}")
            print(f"   └─ {repas['soir']['Catégorie']} | {repas['soir']['Temps de préparation']}min | {repas['soir']['Difficulté']}")
        else:
            print(f"🌙 Soir : ⚠️  Aucune recette disponible")
    
    print("\n" + "="*60)

def afficher_liste_courses(ingredients_totaux):
    """Affiche la liste de courses organisée par catégories"""
    print("\n" + "="*60)
    print("🛒 LISTE DE COURSES")
    print("="*60)
    
    # Classification basique des ingrédients
    categories = {
        "Viandes/Poissons": [],
        "Légumes/Fruits": [],
        "Féculents/Céréales": [],
        "Produits laitiers": [],
        "Épices/Assaisonnements": [],
        "Autres": []
    }
    
    # Listes de mots-clés pour la classification
    viandes = ['poulet', 'lardons', 'crevettes', 'cabillaud', 'escalopes', 'viande', 'porc', 'bœuf', 'agneau', 'poisson']
    legumes = ['poireaux', 'tomates', 'oignon', 'concombre', 'courgettes', 'carottes', 'pommes de terre', 'salade', 'épinards']
    feculents = ['pâtes', 'riz', 'quinoa', 'farine', 'nouilles', 'blé', 'semoule', 'pain']
    laitiers = ['fromage', 'crème', 'feta', 'beurre', 'parmesan', 'lait', 'yaourt', 'mozzarella']
    epices = ['sel', 'poivre', 'curry', 'sauce', 'huile', 'vinaigre', 'épices', 'herbes', 'persil', 'thym']
    
    for nom, details in ingredients_totaux.items():
        nom_lower = nom.lower()
        
        # Classification par mots-clés
        if any(viande in nom_lower for viande in viandes):
            categorie = "Viandes/Poissons"
        elif any(legume in nom_lower for legume in legumes):
            categorie = "Légumes/Fruits"
        elif any(feculent in nom_lower for feculent in feculents):
            categorie = "Féculents/Céréales"
        elif any(laitier in nom_lower for laitier in laitiers):
            categorie = "Produits laitiers"
        elif any(epice in nom_lower for epice in epices):
            categorie = "Épices/Assaisonnements"
        else:
            categorie = "Autres"
        
        # Formater l'affichage
        if details["quantite"] > 0:
            if details["unite"]:
                ligne = f"{details['quantite']:g} {details['unite']} de {nom}"
            else:
                ligne = f"{details['quantite']:g} {nom}"
        else:
            ligne = nom
        
        categories[categorie].append(ligne)
    
    # Afficher par catégories
    for categorie, items in categories.items():
        if items:
            print(f"\n📂 {categorie}")
            print("-" * 25)
            for item in sorted(items):
                print(f"  • {item}")

def afficher_rapport_menu(rapport):
    """Affiche un rapport détaillé d'équilibrage du menu"""
    print("\n" + "="*60)
    print("📊 RAPPORT D'ÉQUILIBRAGE DU MENU")
    print("="*60)
    
    print(f"\n🔢 Vue d'ensemble:")
    print(f"  • Total de plats: {rapport['total_plats']}")
    print(f"  • Temps moyen/plat: {rapport['temps_moyen']:.1f} min")
    print(f"  • Temps total de cuisine: {rapport['temps_total']} min")
    
    print(f"\n🌍 Répartition par origine:")
    for origine, count in rapport['origines'].most_common():
        pourcentage = (count/rapport['total_plats']) * 100
        print(f"  • {origine:<25} {count:2d} plats ({pourcentage:4.1f}%)")
    
    print(f"\n🍖 Répartition par catégorie:")
    for categorie, count in rapport['categories'].most_common():
        pourcentage = (count/rapport['total_plats']) * 100
        print(f"  • {categorie:<15} {count:2d} plats ({pourcentage:4.1f}%)")
    
    print(f"\n⚡ Répartition par difficulté:")
    for difficulte, count in rapport['difficultes'].most_common():
        pourcentage = (count/rapport['total_plats']) * 100
        print(f"  • {difficulte:<10} {count:2d} plats ({pourcentage:4.1f}%)")
    
    # Validation des contraintes
    print(f"\n✅ Validation des contraintes:")
    
    # Contrainte viande
    viande_rouge = rapport['categories'].get('Viande rouge', 0)
    volaille = rapport['categories'].get('Volaille', 0)
    total_viandes = viande_rouge + volaille
    status_viande = '✓' if rapport['contraintes_respectees']['viandes'] else '⚠️'
    print(f"  • Viandes: {total_viandes}/2 (Rouge: {viande_rouge}, Volaille: {volaille}) {status_viande}")
    
    # Contrainte cuisine américaine
    americaine = rapport['origines'].get('Cuisine américaine', 0)
    status_americaine = '✓' if rapport['contraintes_respectees']['americaine'] else '⚠️'
    print(f"  • Cuisine américaine: {americaine}/1 {status_americaine}")
    
    # Contrainte élaborés
    elabores = rapport['difficultes'].get('Élaboré', 0)
    status_elabores = '✓' if rapport['contraintes_respectees']['elabores'] else '⚠️'
    print(f"  • Plats élaborés: {elabores}/2 {status_elabores}")
    
    # Surpondération asiatique/méditerranéenne
    asiatique = rapport['origines'].get('Cuisine asiatique', 0)
    mediterraneenne = rapport['origines'].get('Cuisine méditerranéenne', 0)
    print(f"  • Asiat./Médit.: {asiatique + mediterraneenne} plats (surpondérées x2)")

def afficher_recommandations(rapport):
    """Affiche des recommandations personnalisées"""
    print(f"\n💡 RECOMMANDATIONS:")
    print("-" * 30)
    
    if not rapport['contraintes_respectees']['viandes']:
        print("• ⚠️  Ajuster l'équilibre protéique (viser 1 rouge + 1 volaille)")
    
    if rapport['temps_moyen'] > 45:
        print("• ⏰ Semaine chargée - Prévoir plus de plats rapides")
    elif rapport['temps_moyen'] < 25:
        print("• 👨‍🍳 Semaine légère - Parfait pour expérimenter !")
    
    if len(rapport['categories']) > 0:
        categorie_principale = rapport['categories'].most_common(1)[0]
        if categorie_principale[1] > 5:
            print(f"• 🔄 Beaucoup de {categorie_principale[0].lower()} cette semaine - Variez la semaine prochaine")
    
    if len(rapport['origines']) > 0:
        origine_principale = rapport['origines'].most_common(1)[0]
        if origine_principale[1] > 4:
            print(f"• 🌍 Dominance {origine_principale[0]} - Diversifiez les origines")
    
    print("\n✨ Bon appétit et bonne cuisine ! 👨‍🍳👩‍🍳")