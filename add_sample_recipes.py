# add_sample_recipes.py
# Script pour ajouter des recettes d'exemple à DelfMeals

from app import create_app
from core.database_manager import DatabaseManager

# Recettes d'exemple
RECETTES_EXEMPLES = [
    {
        "Recette": "Tarte aux poireaux et aux lardons",
        "Type de plat": "Plats",
        "Origine": "Cuisine française",
        "Catégorie": "Viande rouge",
        "Nombre de personnes": 4,
        "Temps de préparation": 45,
        "Difficulté": "Normal",
        "Saison": ["Toutes saisons"],
        "Préparation": [
            "Préchauffer le four à 210°C (thermostat 7).",
            "Faire la pâte à tarte : malaxer le beurre et la farine, l'eau, étaler puis mettre dans le plat.",
            "Émincer les poireaux. Les faire dorer dans un peu de beurre.",
            "Faire dorer les lardons à part.",
            "Les égoutter soigneusement avant de les ajouter aux poireaux.",
            "Faire l'appareil : mêler les oeufs, la crème, le sel et le poivre.",
            "Étaler les poireaux et les lardons sur la pâte.",
            "Parsemer de gruyère râpé, couvrir avec l'appareil.",
            "Mettre au four 25 min."
        ],
        "Ingrédients": [
            {"nom": "farine", "quantité": "250", "unité": "g"},
            {"nom": "beurre", "quantité": "140", "unité": "g"},
            {"nom": "poireaux", "quantité": "3", "unité": ""},
            {"nom": "lardons", "quantité": "400", "unité": "g"},
            {"nom": "fromage rapé", "quantité": "100", "unité": "g"},
            {"nom": "crème fraîche", "quantité": "25", "unité": "cl"},
            {"nom": "œufs", "quantité": "3", "unité": ""},
            {"nom": "sel", "quantité": "", "unité": ""},
            {"nom": "poivre", "quantité": "", "unité": ""}
        ],
        "Note": "Peut être préparée à l'avance"
    },
    {
        "Recette": "Pâtes carbonara express",
        "Type de plat": "Plats",
        "Origine": "Cuisine italienne",
        "Catégorie": "Viande rouge",
        "Nombre de personnes": 4,
        "Temps de préparation": 20,
        "Difficulté": "Rapide",
        "Saison": ["Toutes saisons"],
        "Préparation": [
            "Faire cuire les pâtes al dente selon les instructions.",
            "Faire revenir les lardons dans une poêle.",
            "Battre les œufs avec le parmesan, sel et poivre.",
            "Égoutter les pâtes en gardant un peu d'eau de cuisson.",
            "Mélanger les pâtes chaudes avec les œufs battus hors du feu.",
            "Ajouter les lardons et l'eau de cuisson si besoin.",
            "Servir immédiatement avec du parmesan."
        ],
        "Ingrédients": [
            {"nom": "pâtes", "quantité": "500", "unité": "g"},
            {"nom": "lardons", "quantité": "200", "unité": "g"},
            {"nom": "œufs", "quantité": "3", "unité": ""},
            {"nom": "parmesan râpé", "quantité": "100", "unité": "g"},
            {"nom": "poivre noir", "quantité": "", "unité": ""},
            {"nom": "sel", "quantité": "", "unité": ""}
        ],
        "Note": "Attention à ne pas cuire les œufs !"
    },
    {
        "Recette": "Curry de poulet indien",
        "Type de plat": "Plats",
        "Origine": "Cuisine indienne",
        "Catégorie": "Volaille",
        "Nombre de personnes": 4,
        "Temps de préparation": 35,
        "Difficulté": "Normal",
        "Saison": ["Toutes saisons"],
        "Préparation": [
            "Couper le poulet en morceaux et les faire dorer.",
            "Hacher finement l'oignon et l'ail.",
            "Faire revenir oignon et ail dans l'huile.",
            "Ajouter les épices et faire revenir 1 minute.",
            "Ajouter le lait de coco et les tomates concassées.",
            "Remettre le poulet et laisser mijoter 20 minutes.",
            "Servir avec du riz basmati."
        ],
        "Ingrédients": [
            {"nom": "escalopes de poulet", "quantité": "600", "unité": "g"},
            {"nom": "lait de coco", "quantité": "400", "unité": "ml"},
            {"nom": "tomates concassées", "quantité": "400", "unité": "g"},
            {"nom": "oignon", "quantité": "1", "unité": ""},
            {"nom": "gousses d'ail", "quantité": "3", "unité": ""},
            {"nom": "curry en poudre", "quantité": "2", "unité": "cuillères à soupe"},
            {"nom": "riz basmati", "quantité": "300", "unité": "g"}
        ],
        "Note": "Accompagner de naan ou chapati"
    },
    {
        "Recette": "Salade de quinoa méditerranéenne",
        "Type de plat": "Plats",
        "Origine": "Cuisine méditerranéenne",
        "Catégorie": "Végétarien",
        "Nombre de personnes": 4,
        "Temps de préparation": 25,
        "Difficulté": "Rapide",
        "Saison": ["Printemps", "Été"],
        "Préparation": [
            "Cuire le quinoa selon les instructions (environ 15 min).",
            "Couper les tomates cerises en deux.",
            "Émincer le concombre et l'oignon rouge.",
            "Préparer la vinaigrette avec huile d'olive, citron, sel.",
            "Mélanger quinoa refroidi avec légumes.",
            "Ajouter feta émiettée et olives.",
            "Assaisonner et parsemer de menthe fraîche."
        ],
        "Ingrédients": [
            {"nom": "quinoa", "quantité": "250", "unité": "g"},
            {"nom": "tomates cerises", "quantité": "300", "unité": "g"},
            {"nom": "concombre", "quantité": "1", "unité": ""},
            {"nom": "oignon rouge", "quantité": "1", "unité": ""},
            {"nom": "feta", "quantité": "200", "unité": "g"},
            {"nom": "olives noires", "quantité": "100", "unité": "g"},
            {"nom": "menthe fraîche", "quantité": "1", "unité": "bouquet"},
            {"nom": "huile d'olive", "quantité": "4", "unité": "cuillères à soupe"},
            {"nom": "citron", "quantité": "1", "unité": ""}
        ],
        "Note": "Excellent pour les déjeuners d'été"
    },
    {
        "Recette": "Fish and chips maison",
        "Type de plat": "Plats",
        "Origine": "Cuisine américaine",
        "Catégorie": "Poisson",
        "Nombre de personnes": 4,
        "Temps de préparation": 40,
        "Difficulté": "Normal",
        "Saison": ["Toutes saisons"],
        "Préparation": [
            "Éplucher et couper les pommes de terre en frites.",
            "Les blanchir 5 minutes dans l'eau bouillante.",
            "Préparer la pâte à beignets avec farine, bière et sel.",
            "Tremper les filets de poisson dans la pâte.",
            "Frire les frites puis les poissons dans l'huile chaude.",
            "Égoutter sur papier absorbant.",
            "Servir avec sauce tartare et petits pois."
        ],
        "Ingrédients": [
            {"nom": "filets de cabillaud", "quantité": "600", "unité": "g"},
            {"nom": "pommes de terre", "quantité": "800", "unité": "g"},
            {"nom": "farine", "quantité": "150", "unité": "g"},
            {"nom": "bière blonde", "quantité": "200", "unité": "ml"},
            {"nom": "huile de friture", "quantité": "1", "unité": "litre"},
            {"nom": "petits pois", "quantité": "300", "unité": "g"},
            {"nom": "sauce tartare", "quantité": "1", "unité": "pot"}
        ],
        "Note": "Plaisir coupable mais délicieux !"
    },
    {
        "Recette": "Pad Thaï aux crevettes",
        "Type de plat": "Plats",
        "Origine": "Cuisine asiatique",
        "Catégorie": "Poisson",
        "Nombre de personnes": 4,
        "Temps de préparation": 30,
        "Difficulté": "Normal",
        "Saison": ["Toutes saisons"],
        "Préparation": [
            "Faire tremper les nouilles de riz dans l'eau chaude.",
            "Préparer la sauce : mélanger sauce fish, tamarin, sucre.",
            "Faire revenir l'ail et les échalotes dans l'huile.",
            "Ajouter les crevettes et faire cuire.",
            "Ajouter nouilles égouttées et sauce, mélanger.",
            "Incorporer œufs battus et pousses de soja.",
            "Servir avec cacahuètes concassées et citron vert."
        ],
        "Ingrédients": [
            {"nom": "nouilles de riz", "quantité": "300", "unité": "g"},
            {"nom": "crevettes", "quantité": "400", "unité": "g"},
            {"nom": "œufs", "quantité": "2", "unité": ""},
            {"nom": "échalotes", "quantité": "2", "unité": ""},
            {"nom": "pousses de soja", "quantité": "200", "unité": "g"},
            {"nom": "sauce fish", "quantité": "3", "unité": "cuillères à soupe"},
            {"nom": "pâte de tamarin", "quantité": "2", "unité": "cuillères à soupe"},
            {"nom": "cacahuètes", "quantité": "100", "unité": "g"},
            {"nom": "citron vert", "quantité": "2", "unité": ""}
        ],
        "Note": "Authentique et parfumé"
    },
    {
        "Recette": "Blanquette de veau traditionnelle",
        "Type de plat": "Plats",
        "Origine": "Cuisine française",
        "Catégorie": "Viande rouge",
        "Nombre de personnes": 6,
        "Temps de préparation": 120,
        "Difficulté": "Élaboré",
        "Saison": ["Automne", "Hiver"],
        "Préparation": [
            "Couper la viande en morceaux réguliers.",
            "Faire blanchir la viande à l'eau bouillante 2 minutes.",
            "Égoutter et rincer à l'eau froide.",
            "Remettre dans une casserole avec bouquet garni et légumes.",
            "Couvrir d'eau froide et porter à ébullition.",
            "Laisser mijoter 1h à feu doux.",
            "Préparer la sauce avec farine, beurre et bouillon.",
            "Ajouter jaunes d'œufs et crème.",
            "Servir avec du riz."
        ],
        "Ingrédients": [
            {"nom": "épaule de veau", "quantité": "1.2", "unité": "kg"},
            {"nom": "carottes", "quantité": "3", "unité": ""},
            {"nom": "oignons", "quantité": "2", "unité": ""},
            {"nom": "champignons de Paris", "quantité": "300", "unité": "g"},
            {"nom": "crème fraîche", "quantité": "20", "unité": "cl"},
            {"nom": "jaunes d'œufs", "quantité": "2", "unité": ""},
            {"nom": "farine", "quantité": "40", "unité": "g"},
            {"nom": "bouquet garni", "quantité": "1", "unité": ""}
        ],
        "Note": "Plat de fête traditionnel"
    },
    {
        "Recette": "Risotto aux champignons",
        "Type de plat": "Plats",
        "Origine": "Cuisine italienne",
        "Catégorie": "Végétarien",
        "Nombre de personnes": 4,
        "Temps de préparation": 35,
        "Difficulté": "Normal",
        "Saison": ["Automne", "Hiver"],
        "Préparation": [
            "Faire chauffer le bouillon de légumes.",
            "Faire revenir l'oignon haché dans l'huile d'olive.",
            "Ajouter le riz et nacrer pendant 2 minutes.",
            "Ajouter le vin blanc et laisser évaporer.",
            "Incorporer le bouillon louche par louche en remuant.",
            "Ajouter les champignons poêlés en fin de cuisson.",
            "Terminer avec beurre et parmesan.",
            "Servir immédiatement."
        ],
        "Ingrédients": [
            {"nom": "riz arborio", "quantité": "300", "unité": "g"},
            {"nom": "champignons mélangés", "quantité": "400", "unité": "g"},
            {"nom": "bouillon de légumes", "quantité": "1", "unité": "litre"},
            {"nom": "oignon", "quantité": "1", "unité": ""},
            {"nom": "vin blanc", "quantité": "10", "unité": "cl"},
            {"nom": "parmesan râpé", "quantité": "100", "unité": "g"},
            {"nom": "beurre", "quantité": "50", "unité": "g"},
            {"nom": "huile d'olive", "quantité": "3", "unité": "cuillères à soupe"}
        ],
        "Note": "Remuer constamment pour une texture crémeuse"
    },
    {
        "Recette": "Saumon grillé sauce hollandaise",
        "Type de plat": "Plats",
        "Origine": "Cuisine française",
        "Catégorie": "Poisson",
        "Nombre de personnes": 4,
        "Temps de préparation": 30,
        "Difficulté": "Normal",
        "Saison": ["Printemps", "Été"],
        "Préparation": [
            "Préchauffer le four à 200°C.",
            "Préparer la sauce hollandaise : monter les jaunes avec le beurre fondu.",
            "Assaisonner les pavés de saumon.",
            "Les griller à la poêle 3 min de chaque côté.",
            "Finir au four 5 minutes si besoin.",
            "Cuire les légumes à la vapeur.",
            "Servir le saumon nappé de sauce hollandaise."
        ],
        "Ingrédients": [
            {"nom": "pavés de saumon", "quantité": "4", "unité": ""},
            {"nom": "beurre", "quantité": "150", "unité": "g"},
            {"nom": "jaunes d'œufs", "quantité": "3", "unité": ""},
            {"nom": "citron", "quantité": "1", "unité": ""},
            {"nom": "haricots verts", "quantité": "300", "unité": "g"},
            {"nom": "pommes de terre nouvelles", "quantité": "400", "unité": "g"},
            {"nom": "sel", "quantité": "", "unité": ""},
            {"nom": "poivre", "quantité": "", "unité": ""}
        ],
        "Note": "Sauce délicate, ne pas faire bouillir"
    },
    {
        "Recette": "Couscous aux légumes",
        "Type de plat": "Plats",
        "Origine": "Cuisine du Maghreb",
        "Catégorie": "Végétarien",
        "Nombre de personnes": 6,
        "Temps de préparation": 60,
        "Difficulté": "Normal",
        "Saison": ["Automne", "Hiver"],
        "Préparation": [
            "Faire revenir l'oignon dans l'huile d'olive.",
            "Ajouter les épices et faire revenir 1 minute.",
            "Ajouter les légumes durs en premier (carottes, navets).",
            "Couvrir d'eau et laisser mijoter.",
            "Ajouter les légumes plus tendres (courgettes, tomates).",
            "Préparer la semoule selon les instructions.",
            "Servir la semoule avec les légumes et le bouillon.",
            "Proposer harissa à côté."
        ],
        "Ingrédients": [
            {"nom": "semoule de couscous", "quantité": "500", "unité": "g"},
            {"nom": "courgettes", "quantité": "2", "unité": ""},
            {"nom": "carottes", "quantité": "3", "unité": ""},
            {"nom": "navets", "quantité": "2", "unité": ""},
            {"nom": "tomates", "quantité": "3", "unité": ""},
            {"nom": "pois chiches", "quantité": "200", "unité": "g"},
            {"nom": "oignon", "quantité": "1", "unité": ""},
            {"nom": "épices couscous", "quantité": "2", "unité": "cuillères à soupe"},
            {"nom": "harissa", "quantité": "1", "unité": "tube"}
        ],
        "Note": "Accompagner de merguez pour les non-végétariens"
    },
    {
        "Recette": "Bœuf bourguignon",
        "Type de plat": "Plats",
        "Origine": "Cuisine française",
        "Catégorie": "Viande rouge",
        "Nombre de personnes": 6,
        "Temps de préparation": 180,
        "Difficulté": "Élaboré",
        "Saison": ["Automne", "Hiver"],
        "Préparation": [
            "Couper la viande en gros cubes et la faire mariner au vin rouge.",
            "Faire suer les lardons et les réserver.",
            "Faire revenir la viande égouttée dans la graisse des lardons.",
            "Ajouter oignons et carottes, faire revenir.",
            "Saupoudrer de farine, mélanger.",
            "Ajouter le vin de marinade et le bouquet garni.",
            "Laisser mijoter 2h30 à feu doux.",
            "Ajouter champignons et lardons en fin de cuisson.",
            "Servir avec des pommes de terre ou des pâtes."
        ],
        "Ingrédients": [
            {"nom": "bœuf à braiser", "quantité": "1.5", "unité": "kg"},
            {"nom": "vin rouge", "quantité": "75", "unité": "cl"},
            {"nom": "lardons", "quantité": "200", "unité": "g"},
            {"nom": "champignons de Paris", "quantité": "300", "unité": "g"},
            {"nom": "carottes", "quantité": "3", "unité": ""},
            {"nom": "oignons", "quantité": "2", "unité": ""},
            {"nom": "farine", "quantité": "2", "unité": "cuillères à soupe"},
            {"nom": "bouquet garni", "quantité": "1", "unité": ""}
        ],
        "Note": "Meilleur réchauffé le lendemain"
    },
    {
        "Recette": "Poulet tikka masala",
        "Type de plat": "Plats",
        "Origine": "Cuisine indienne",
        "Catégorie": "Volaille",
        "Nombre de personnes": 4,
        "Temps de préparation": 45,
        "Difficulté": "Normal",
        "Saison": ["Toutes saisons"],
        "Préparation": [
            "Couper le poulet en cubes et faire mariner avec yaourt et épices.",
            "Faire griller le poulet mariné à la poêle.",
            "Dans une autre poêle, faire revenir oignon et ail.",
            "Ajouter les épices et faire revenir.",
            "Ajouter tomates concassées et crème.",
            "Remettre le poulet grillé dans la sauce.",
            "Laisser mijoter 10 minutes.",
            "Servir avec du riz basmati et du naan."
        ],
        "Ingrédients": [
            {"nom": "filets de poulet", "quantité": "600", "unité": "g"},
            {"nom": "yaourt nature", "quantité": "200", "unité": "ml"},
            {"nom": "tomates concassées", "quantité": "400", "unité": "g"},
            {"nom": "crème fraîche", "quantité": "15", "unité": "cl"},
            {"nom": "oignon", "quantité": "1", "unité": ""},
            {"nom": "gousses d'ail", "quantité": "3", "unité": ""},
            {"nom": "garam masala", "quantité": "2", "unité": "cuillères à soupe"},
            {"nom": "paprika", "quantité": "1", "unité": "cuillère à soupe"},
            {"nom": "gingembre frais", "quantité": "1", "unité": "morceau"}
        ],
        "Note": "Laisser mariner le poulet au moins 30 min"
    },
    {
        "Recette": "Ratatouille provençale",
        "Type de plat": "Plats",
        "Origine": "Cuisine française",
        "Catégorie": "Végétarien",
        "Nombre de personnes": 4,
        "Temps de préparation": 50,
        "Difficulté": "Rapide",
        "Saison": ["Été", "Automne"],
        "Préparation": [
            "Couper tous les légumes en cubes réguliers.",
            "Faire revenir l'oignon dans l'huile d'olive.",
            "Ajouter l'ail et faire revenir 1 minute.",
            "Ajouter aubergines et courgettes, faire revenir.",
            "Ajouter poivrons et tomates.",
            "Assaisonner avec herbes de Provence.",
            "Laisser mijoter 30 minutes à feu doux.",
            "Rectifier l'assaisonnement."
        ],
        "Ingrédients": [
            {"nom": "aubergines", "quantité": "2", "unité": ""},
            {"nom": "courgettes", "quantité": "2", "unité": ""},
            {"nom": "poivrons", "quantité": "2", "unité": ""},
            {"nom": "tomates", "quantité": "4", "unité": ""},
            {"nom": "oignon", "quantité": "1", "unité": ""},
            {"nom": "gousses d'ail", "quantité": "3", "unité": ""},
            {"nom": "herbes de Provence", "quantité": "2", "unité": "cuillères à café"},
            {"nom": "huile d'olive", "quantité": "5", "unité": "cuillères à soupe"}
        ],
        "Note": "Excellent froid le lendemain"
    },
    {
        "Recette": "Paella au poulet et fruits de mer",
        "Type de plat": "Plats",
        "Origine": "Cuisine méditerranéenne",
        "Catégorie": "Volaille",
        "Nombre de personnes": 6,
        "Temps de préparation": 60,
        "Difficulté": "Normal",
        "Saison": ["Printemps", "Été"],
        "Préparation": [
            "Faire revenir le poulet coupé en morceaux.",
            "Ajouter oignons et poivrons, faire revenir.",
            "Ajouter ail et tomates, faire revenir.",
            "Ajouter le riz et mélanger.",
            "Ajouter bouillon chaud et safran.",
            "Laisser cuire 15 minutes sans remuer.",
            "Ajouter fruits de mer en fin de cuisson.",
            "Laisser reposer 5 minutes avant de servir."
        ],
        "Ingrédients": [
            {"nom": "riz rond", "quantité": "400", "unité": "g"},
            {"nom": "cuisses de poulet", "quantité": "4", "unité": ""},
            {"nom": "moules", "quantité": "500", "unité": "g"},
            {"nom": "crevettes", "quantité": "300", "unité": "g"},
            {"nom": "poivrons", "quantité": "2", "unité": ""},
            {"nom": "tomates", "quantité": "2", "unité": ""},
            {"nom": "bouillon de volaille", "quantité": "1", "unité": "litre"},
            {"nom": "safran", "quantité": "1", "unité": "pincée"},
            {"nom": "petits pois", "quantité": "150", "unité": "g"}
        ],
        "Note": "Ne pas remuer pendant la cuisson du riz"
    },
    {
        "Recette": "Tacos au poisson épicé",
        "Type de plat": "Plats",
        "Origine": "Cuisine américaine",
        "Catégorie": "Poisson",
        "Nombre de personnes": 4,
        "Temps de préparation": 25,
        "Difficulté": "Rapide",
        "Saison": ["Printemps", "Été"],
        "Préparation": [
            "Assaisonner le poisson avec épices mexicaines.",
            "Faire griller le poisson à la poêle.",
            "Réchauffer les tortillas au four ou à la poêle.",
            "Préparer la sauce avec yaourt, citron vert et coriandre.",
            "Couper avocat et tomates en dés.",
            "Assembler les tacos avec poisson, sauce, légumes.",
            "Servir avec quartiers de citron vert."
        ],
        "Ingrédients": [
            {"nom": "filets de cabillaud", "quantité": "500", "unité": "g"},
            {"nom": "tortillas de blé", "quantité": "8", "unité": ""},
            {"nom": "avocat", "quantité": "2", "unité": ""},
            {"nom": "tomates", "quantité": "2", "unité": ""},
            {"nom": "yaourt grec", "quantité": "200", "unité": "ml"},
            {"nom": "citrons verts", "quantité": "3", "unité": ""},
            {"nom": "coriandre fraîche", "quantité": "1", "unité": "bouquet"},
            {"nom": "épices mexicaines", "quantité": "2", "unité": "cuillères à soupe"}
        ],
        "Note": "Délicieux avec une salade de chou"
    },
    {
        "Recette": "Sushi bowl aux légumes",
        "Type de plat": "Plats",
        "Origine": "Cuisine asiatique",
        "Catégorie": "Végétarien",
        "Nombre de personnes": 4,
        "Temps de préparation": 30,
        "Difficulté": "Rapide",
        "Saison": ["Printemps", "Été"],
        "Préparation": [
            "Cuire le riz sushi selon les instructions.",
            "Assaisonner le riz avec vinaigre de riz.",
            "Préparer les légumes : avocat, concombre, radis.",
            "Faire mariner le tofu dans sauce soja et miso.",
            "Faire griller le tofu à la poêle.",
            "Dresser dans des bols avec riz, légumes et tofu.",
            "Servir avec sauce soja et wasabi."
        ],
        "Ingrédients": [
            {"nom": "riz sushi", "quantité": "300", "unité": "g"},
            {"nom": "tofu ferme", "quantité": "200", "unité": "g"},
            {"nom": "avocat", "quantité": "2", "unité": ""},
            {"nom": "concombre", "quantité": "1", "unité": ""},
            {"nom": "radis", "quantité": "4", "unité": ""},
            {"nom": "vinaigre de riz", "quantité": "3", "unité": "cuillères à soupe"},
            {"nom": "sauce soja", "quantité": "5", "unité": "cuillères à soupe"},
            {"nom": "pâte miso", "quantité": "1", "unité": "cuillère à soupe"},
            {"nom": "graines de sésame", "quantité": "2", "unité": "cuillères à soupe"}
        ],
        "Note": "Garnir de graines de sésame et algues nori"
    },
    {
        "Recette": "Gratinée d'aubergines",
        "Type de plat": "Plats",
        "Origine": "Cuisine méditerranéenne",
        "Catégorie": "Végétarien",
        "Nombre de personnes": 4,
        "Temps de préparation": 60,
        "Difficulté": "Normal",
        "Saison": ["Été", "Automne"],
        "Préparation": [
            "Couper les aubergines en tranches épaisses.",
            "Les faire dégorger avec du sel 30 minutes.",
            "Rincer et sécher les aubergines.",
            "Les faire griller à la poêle avec huile d'olive.",
            "Préparer la sauce tomate avec ail et basilic.",
            "Alterner couches d'aubergines, sauce et mozzarella.",
            "Terminer par parmesan râpé.",
            "Gratiner au four 25 minutes à 180°C."
        ],
        "Ingrédients": [
            {"nom": "aubergines", "quantité": "3", "unité": ""},
            {"nom": "tomates concassées", "quantité": "400", "unité": "g"},
            {"nom": "mozzarella", "quantité": "250", "unité": "g"},
            {"nom": "parmesan râpé", "quantité": "100", "unité": "g"},
            {"nom": "basilic frais", "quantité": "1", "unité": "bouquet"},
            {"nom": "gousses d'ail", "quantité": "2", "unité": ""},
            {"nom": "huile d'olive", "quantité": "6", "unité": "cuillères à soupe"},
            {"nom": "sel", "quantité": "", "unité": ""}
        ],
        "Note": "Laisser reposer 10 min avant de servir"
    },
    {
        "Recette": "Crème brûlée à la vanille",
        "Type de plat": "Desserts",
        "Origine": "Cuisine française",
        "Catégorie": "Végétarien",
        "Nombre de personnes": 6,
        "Temps de préparation": 45,
        "Difficulté": "Normal",
        "Saison": ["Toutes saisons"],
        "Préparation": [
            "Fendre la gousse de vanille et gratter les graines.",
            "Faire chauffer la crème avec vanille sans bouillir.",
            "Battre jaunes d'œufs avec sucre jusqu'à blanchiment.",
            "Verser crème chaude sur les jaunes en fouettant.",
            "Filtrer et répartir dans ramequins.",
            "Cuire au bain-marie 40 min à 150°C.",
            "Laisser refroidir puis réfrigérer 4h.",
            "Saupoudrer de sucre et caraméliser au chalumeau."
        ],
        "Ingrédients": [
            {"nom": "crème liquide", "quantité": "50", "unité": "cl"},
            {"nom": "jaunes d'œufs", "quantité": "6", "unité": ""},
            {"nom": "sucre en poudre", "quantité": "100", "unité": "g"},
            {"nom": "gousse de vanille", "quantité": "1", "unité": ""},
            {"nom": "sucre roux", "quantité": "50", "unité": "g"}
        ],
        "Note": "Indispensable : chalumeau culinaire"
    },
    {
        "Recette": "Gazpacho andalou",
        "Type de plat": "Entrées",
        "Origine": "Cuisine méditerranéenne",
        "Catégorie": "Végétarien",
        "Nombre de personnes": 4,
        "Temps de préparation": 20,
        "Difficulté": "Rapide",
        "Saison": ["Été"],
        "Préparation": [
            "Éplucher et épépiner les tomates.",
            "Éplucher le concombre et enlever les graines.",
            "Mixer tous les légumes avec ail et pain trempé.",
            "Ajouter huile d'olive, vinaigre et eau froide.",
            "Mixer jusqu'à obtenir consistance lisse.",
            "Assaisonner sel et poivre.",
            "Réfrigérer au moins 2 heures.",
            "Servir avec dés de légumes en garniture."
        ],
        "Ingrédients": [
            {"nom": "tomates mûres", "quantité": "1", "unité": "kg"},
            {"nom": "concombre", "quantité": "1", "unité": ""},
            {"nom": "poivron rouge", "quantité": "1", "unité": ""},
            {"nom": "oignon", "quantité": "1/2", "unité": ""},
            {"nom": "gousse d'ail", "quantité": "1", "unité": ""},
            {"nom": "pain de mie", "quantité": "2", "unité": "tranches"},
            {"nom": "huile d'olive", "quantité": "5", "unité": "cuillères à soupe"},
            {"nom": "vinaigre de xérès", "quantité": "2", "unité": "cuillères à soupe"}
        ],
        "Note": "Parfait pour les chaudes journées d'été"
    }
]

def main():
    """Ajoute les recettes d'exemple à la base de données"""
    print("🍽️ Ajout de recettes d'exemple...")
    
    # Créer l'application Flask
    app = create_app()
    
    with app.app_context():
        with DatabaseManager() as db:
            ajoutees = 0
            erreurs = 0
            
            for recette in RECETTES_EXEMPLES:
                try:
                    recette_id = db.add_recette(recette)
                    print(f"✅ Recette ajoutée : {recette['Recette']} (ID: {recette_id})")
                    ajoutees += 1
                except Exception as e:
                    print(f"❌ Erreur pour {recette['Recette']}: {e}")
                    erreurs += 1
            
            print(f"\n📊 Résumé : {ajoutees} recettes ajoutées, {erreurs} erreurs")
            print("🎉 Terminé ! Vous pouvez maintenant profiter de votre application DelfMeals.")

if __name__ == "__main__":
    main()
