#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script final optimisé pour vos JSONs avec guillemets typographiques
"""

import json
import re
import os
from pathlib import Path


def normalize_quotes(text):
    """Convertit tous les types de guillemets en guillemets standard"""
    # Guillemets typographiques → guillemets droits
    text = text.replace('"', '"')  # Guillemet ouvrant (U+201C)
    text = text.replace('"', '"')  # Guillemet fermant (U+201D)
    text = text.replace(''', "'")  # Apostrophe typographique (U+2019)
    text = text.replace(''', "'")  # Apostrophe ouvrant (U+2018)
    
    return text


def extract_json_recipes(file_path, output_folder="recettes_json"):
    """Extrait toutes les recettes JSON du fichier"""
    
    # Crée le dossier de sortie
    os.makedirs(output_folder, exist_ok=True)
    
    # Lit le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Normalise les guillemets
    content = normalize_quotes(content)
    
    # Extrait les objets JSON
    json_objects = []
    brace_count = 0
    start_pos = None
    
    for i, char in enumerate(content):
        if char == '{':
            if brace_count == 0:
                start_pos = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_pos is not None:
                json_str = content[start_pos:i+1]
                json_objects.append(json_str)
                start_pos = None
    
    print(f"🔍 Trouvé {len(json_objects)} objets JSON")
    
    # Parse et sauvegarde chaque recette
    success_count = 0
    for i, json_str in enumerate(json_objects):
        try:
            # Parse le JSON
            recipe = json.loads(json_str)
            
            # Génère un nom de fichier propre
            name = recipe.get('nom', f'recette_{i+1}')
            filename = re.sub(r'[^\w\s-]', '', name)
            filename = re.sub(r'[-\s]+', '_', filename)
            filename = filename.strip()[:50]  # Max 50 caractères
            
            # Évite les doublons
            output_path = Path(output_folder) / f"{filename}.json"
            counter = 1
            while output_path.exists():
                output_path = Path(output_folder) / f"{filename}_{counter}.json"
                counter += 1
            
            # Sauvegarde le JSON formaté
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(recipe, f, ensure_ascii=False, indent=2)
            
            success_count += 1
            print(f"✅ {success_count}. {name}")
            print(f"   → {output_path.name}")
            
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON #{i+1}: {e}")
            continue
    
    print(f"\n🎉 Extraction terminée!")
    print(f"✅ {success_count} recettes converties avec succès")
    print(f"📁 Fichiers créés dans: {output_folder}/")
    
    return success_count


# Utilisation directe
if __name__ == "__main__":
    print("=== Extracteur de recettes JSON ===\n")
    
    # Utilise votre fichier directement
    input_file = "toutes_mes_recettes.txt"
    
    # Vérifie que le fichier existe
    if not os.path.exists(input_file):
        print(f"❌ Fichier '{input_file}' introuvable")
        exit(1)
    
    # Lance l'extraction
    count = extract_json_recipes(input_file)
    
    if count > 0:
        print(f"\n🚀 Prêt pour l'importation!")
        print(f"Utilisez maintenant le script d'importation en base de données")
    else:
        print(f"\n⚠️ Aucune recette extraite")
