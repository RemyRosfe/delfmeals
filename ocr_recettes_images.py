# ocr_recettes_images.py
# Script OCR pour images de recettes (alternative sans PDF)

import pytesseract
from PIL import Image
import re
import spacy
import json
from pathlib import Path
import os

# Configuration Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Charger le modèle spaCy français
try:
    nlp = spacy.load("fr_core_news_sm")
except OSError:
    print("⚠️ Modèle spaCy français non trouvé")
    nlp = None

class RecetteOCRImages:
    def __init__(self):
        # Mêmes mots-clés que la version PDF
        self.mots_cles_ingredients = [
            'ingrédients', 'ingredients', 'ingrédient', 'ingredient',
            'pour', 'il faut', 'nécessaire', 'composition'
        ]
        
        self.mots_cles_preparation = [
            'préparation', 'preparation', 'méthode', 'method', 'recette',
            'étapes', 'etapes', 'cuisson', 'réalisation', 'realisation',
            'procédé', 'procede', 'mode opératoire'
        ]
        
        self.mots_cles_temps = [
            'temps', 'durée', 'duree', 'cuisson', 'préparation', 'preparation',
            'minute', 'min', 'heure', 'heures', 'h'
        ]
        
        self.mots_cles_personnes = [
            'personne', 'personnes', 'portions', 'parts', 'convive', 'convives'
        ]
        
        # Unités courantes
        self.unites = [
            'kg', 'g', 'gr', 'gramme', 'grammes', 'kilogramme', 'kilogrammes',
            'l', 'litre', 'litres', 'ml', 'millilitre', 'millilitres',
            'cl', 'centilitre', 'centilitres', 'dl', 'décilitre', 'décilitres',
            'cuillère', 'cuillères', 'cuillere', 'cuilleres', 'c.', 'cs', 'cc',
            'c.à.s', 'c.à.c', 'cuillère à soupe', 'cuillère à café',
            'verre', 'verres', 'tasse', 'tasses', 'bol', 'bols',
            'pièce', 'pièces', 'piece', 'pieces', 'tranche', 'tranches',
            'botte', 'bottes', 'bouquet', 'bouquets', 'pincée', 'pincees',
            'sachet', 'sachets', 'boîte', 'boites', 'conserve'
        ]
    
    def preprocesser_image(self, image_path):
        """Préprocessing de l'image pour améliorer l'OCR"""
        try:
            image = Image.open(image_path)
            
            # Convertir en niveaux de gris
            if image.mode != 'L':
                image = image.convert('L')
            
            # Améliorer la résolution si trop petite
            width, height = image.size
            if width < 1000:
                scale_factor = 1200 / width
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            print(f"❌ Erreur preprocessing {image_path}: {e}")
            return None
    
    def extraire_texte_ocr(self, image):
        """Extrait le texte d'une image avec OCR optimisé"""
        try:
            # Preprocessing
            image = self.preprocesser_image(image) if isinstance(image, str) else image
            if image is None:
                return ""
            
            # Configuration OCR
            config = '--oem 3 --psm 6 -l fra'
            texte = pytesseract.image_to_string(image, config=config)
            
            return texte
            
        except Exception as e:
            print(f"❌ Erreur OCR: {e}")
            return ""
    
    def nettoyer_texte(self, texte):
        """Nettoie le texte extrait"""
        if not texte:
            return ""
        
        # Corrections OCR courantes
        corrections = {
            'ﬁ': 'fi', 'ﬂ': 'fl', 'œ': 'oe', 'æ': 'ae',
            'º': '°', '§': 's', '|': 'l', '1|': 'll',
            'cuillcre': 'cuillère', 'cuillere': 'cuillère',
            'grammc': 'gramme', 'grarnme': 'gramme',
            'minutc': 'minute', 'minutcs': 'minutes',
        }
        
        for ancien, nouveau in corrections.items():
            texte = texte.replace(ancien, nouveau)
        
        # Nettoyer les lignes
        lignes = [ligne.strip() for ligne in texte.split('\n') if ligne.strip()]
        return '\n'.join(lignes)
    
    def extraire_titre(self, texte):
        """Extrait le titre de la recette"""
        lignes = texte.split('\n')
        
        for ligne in lignes[:5]:
            ligne = ligne.strip()
            if ligne and len(ligne) > 5:
                # Éviter les mots-clés de section
                ligne_lower = ligne.lower()
                mots_a_eviter = self.mots_cles_ingredients + self.mots_cles_preparation
                if not any(mot in ligne_lower for mot in mots_a_eviter):
                    if not self.est_ingredient_line(ligne):
                        return ligne
        
        return "Recette scannée"
    
    def extraire_temps_preparation(self, texte):
        """Extrait le temps de préparation"""
        patterns = [
            r'(\d+)\s*(?:min|minute|minutes)',
            r'(\d+)\s*(?:h|heure|heures)\s*(?:(\d+)\s*(?:min|minute|minutes))?',
            r'temps[:\s]*(\d+)',
            r'préparation[:\s]*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texte, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2 and match.group(2):
                    return int(match.group(1)) * 60 + int(match.group(2))
                else:
                    return int(match.group(1))
        return 30
    
    def extraire_nb_personnes(self, texte):
        """Extrait le nombre de personnes"""
        patterns = [
            r'(\d+)\s*(?:personne|personnes|portions)',
            r'pour\s*(\d+)',
            r'(\d+)\s*parts'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texte, re.IGNORECASE)
            if match:
                nb = int(match.group(1))
                if 1 <= nb <= 20:
                    return nb
        return 4
    
    def est_ingredient_line(self, ligne):
        """Détermine si une ligne est un ingrédient"""
        ligne_lower = ligne.lower().strip()
        
        if len(ligne) < 3 or len(ligne) > 100:
            return False
        
        # Vérifier quantité + unité
        for unite in self.unites:
            if unite in ligne_lower:
                if re.search(rf'\d+.*{re.escape(unite)}', ligne_lower):
                    return True
        
        # Vérifier format liste
        if re.match(r'^\s*[-•*\d+\.]\s*', ligne):
            return True
        
        return False
    
    def parser_ingredient(self, ligne):
        """Parse une ligne d'ingrédient"""
        ligne_originale = ligne
        ligne = re.sub(r'^[-•*\d+\.]\s*', '', ligne.strip())
        
        # Pattern quantité + unité + nom
        pattern = r'^(\d+(?:[.,]\d+)?)\s*([a-zA-Zàáâäéèêëïîôöùúûü\.]+)?\s*(?:de\s+)?(.+)$'
        match = re.match(pattern, ligne, re.IGNORECASE)
        
        if match:
            quantite = match.group(1).replace(',', '.')
            unite = match.group(2) if match.group(2) else ""
            nom = match.group(3).strip()
            
            # Normaliser l'unité
            if unite:
                unite = unite.lower().strip('.')
                unite_normalisee = {
                    'gr': 'g', 'grs': 'g',
                    'cs': 'cuillères à soupe', 'cc': 'cuillères à café',
                }.get(unite, unite)
                unite = unite_normalisee
            
            return {"nom": nom, "quantité": quantite, "unité": unite}
        
        return {"nom": ligne, "quantité": "", "unité": ""}
    
    def extraire_sections(self, texte):
        """Extrait les sections ingrédients et préparation"""
        lignes = texte.split('\n')
        
        section_courante = "autre"
        ingredients = []
        preparation = []
        
        for ligne in lignes:
            ligne = ligne.strip()
            if not ligne:
                continue
            
            ligne_lower = ligne.lower()
            
            # Détecter sections
            if any(mot in ligne_lower for mot in self.mots_cles_ingredients):
                section_courante = "ingredients"
                continue
            
            if any(mot in ligne_lower for mot in self.mots_cles_preparation):
                section_courante = "preparation"
                continue
            
            # Ajouter à la section appropriée
            if section_courante == "ingredients" and self.est_ingredient_line(ligne):
                ingredients.append(self.parser_ingredient(ligne))
            elif section_courante == "preparation":
                etape = re.sub(r'^\d+[\.\)]\s*', '', ligne).strip()
                if etape:
                    preparation.append(etape)
        
        return ingredients, preparation
    
    def deviner_categorie(self, ingredients_text, titre):
        """Devine la catégorie de la recette"""
        text_complet = (titre + " " + ingredients_text).lower()
        
        if any(mot in text_complet for mot in ['boeuf', 'veau', 'agneau', 'porc']):
            return "Viande rouge"
        elif any(mot in text_complet for mot in ['poulet', 'volaille', 'dinde']):
            return "Volaille"
        elif any(mot in text_complet for mot in ['poisson', 'saumon', 'crevette']):
            return "Poisson"
        else:
            return "Végétarien"
    
    def deviner_difficulte(self, nb_etapes, temps):
        """Devine la difficulté"""
        if temps <= 30 and nb_etapes <= 5:
            return "Rapide"
        elif temps >= 90 or nb_etapes >= 10:
            return "Élaboré"
        else:
            return "Normal"
    
    def traiter_image(self, image_path):
        """Traite une image de recette"""
        print(f"🔍 Traitement de {os.path.basename(image_path)}...")
        
        # OCR
        texte_brut = self.extraire_texte_ocr(image_path)
        if not texte_brut or len(texte_brut.strip()) < 50:
            print(f"⚠️ Texte insuffisant")
            return None
        
        # Extraction
        texte_nettoye = self.nettoyer_texte(texte_brut)
        titre = self.extraire_titre(texte_nettoye)
        temps = self.extraire_temps_preparation(texte_nettoye)
        nb_personnes = self.extraire_nb_personnes(texte_nettoye)
        ingredients, preparation = self.extraire_sections(texte_nettoye)
        
        if not ingredients and not preparation:
            print(f"⚠️ Aucun ingrédient ou étape trouvé")
            return None
        
        # Inférences
        ingredients_text = " ".join([ing["nom"] for ing in ingredients])
        categorie = self.deviner_categorie(ingredients_text, titre)
        difficulte = self.deviner_difficulte(len(preparation), temps)
        
        # Créer recette
        recette = {
            "Recette": titre,
            "Type de plat": "Plats",
            "Origine": "",
            "Catégorie": categorie,
            "Nombre de personnes": nb_personnes,
            "Temps de préparation": temps,
            "Difficulté": difficulte,
            "Saison": ["Toutes saisons"],
            "Préparation": preparation,
            "Ingrédients": ingredients,
            "Note": f"Recette numérisée depuis {os.path.basename(image_path)}"
        }
        
        return {
            "recette": recette,
            "texte_brut": texte_brut,
            "texte_nettoye": texte_nettoye
        }

def traiter_images_recettes(dossier_images="recettes_images", dossier_output="recettes_txt"):
    """Traite toutes les images d'un dossier"""
    ocr = RecetteOCRImages()
    
    # Créer dossiers
    Path(dossier_output).mkdir(exist_ok=True)
    Path(dossier_images).mkdir(exist_ok=True)
    
    # Extensions supportées
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
    
    # Trouver toutes les images
    fichiers = []
    for ext in extensions:
        fichiers.extend(Path(dossier_images).glob(f'*{ext}'))
        fichiers.extend(Path(dossier_images).glob(f'*{ext.upper()}'))
    
    if not fichiers:
        print(f"❌ Aucune image trouvée dans {dossier_images}/")
        print(f"💡 Extensions supportées: {extensions}")
        return []
    
    print(f"🖼️ {len(fichiers)} image(s) trouvée(s)")
    
    recettes_traitees = []
    
    for fichier in fichiers:
        resultat = ocr.traiter_image(str(fichier))
        
        if resultat:
            recettes_traitees.append(resultat)
            
            # Sauvegarder
            nom_base = fichier.stem
            
            # JSON
            chemin_json = Path(dossier_output) / f"{nom_base}_recette.json"
            with open(chemin_json, 'w', encoding='utf-8') as f:
                json.dump(resultat["recette"], f, indent=2, ensure_ascii=False)
            
            # Texte brut
            chemin_texte = Path(dossier_output) / f"{nom_base}_texte_brut.txt"
            with open(chemin_texte, 'w', encoding='utf-8') as f:
                f.write(resultat["texte_brut"])
            
            print(f"✅ {fichier.name} → {resultat['recette']['Recette']}")
    
    print(f"\n📊 {len(recettes_traitees)} recettes extraites")
    return recettes_traitees

# Script principal
if __name__ == "__main__":
    print("🍽️ OCR Recettes Images - DelfMeals")
    print("==================================")
    
    # Configuration
    DOSSIER_IMAGES = "recettes_images"
    DOSSIER_OUTPUT = "recettes_txt"
    
    print("💡 INSTRUCTIONS :")
    print(f"1. Convertissez vos PDFs en images (JPG/PNG)")
    print(f"2. Placez les images dans {DOSSIER_IMAGES}/")  
    print(f"3. Relancez ce script")
    print(f"\n🔄 Pour convertir PDF → Images:")
    print(f"   - Ouvrez vos PDFs dans un lecteur")
    print(f"   - 'Enregistrer sous' → Format: JPG ou PNG")
    print(f"   - Ou utilisez un convertisseur en ligne")
    
    # Traiter les images
    recettes = traiter_images_recettes(DOSSIER_IMAGES, DOSSIER_OUTPUT)
    
    if recettes:
        print(f"\n🎉 {len(recettes)} recettes extraites !")
        print(f"📁 Vérifiez les résultats dans {DOSSIER_OUTPUT}/")
        print(f"📝 Lancez ensuite: python import_recettes_scannees.py")
    else:
        print(f"\n💡 Convertissez vos PDFs en images et placez-les dans {DOSSIER_IMAGES}/")
