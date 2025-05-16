#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'import amélioré avec conversion forcée des types
Évite les problèmes de types str/int
"""

import json
import sqlite3
import re
from pathlib import Path

def convert_to_int(value, default=4):
    """Convertit une valeur en entier de manière robuste"""
    if isinstance(value, int):
        return value
    
    if isinstance(value, str):
        # Extrait les chiffres de la string
        numbers = re.findall(r'\d+', value)
        if numbers:
            return int(numbers[0])
    
    # Si conversion impossible, retourne la valeur par défaut
    return default

def import_recipes_safe(json_folder, db_path):
    """Import avec conversion stricte des types"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    imported = 0
    
    for json_file in Path(json_folder).glob('*.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            recipe = json.load(f)
        
        try:
            # Conversion forcée du nb_personnes
            nb_personnes = convert_to_int(recipe.get('nb_personnes', 4))
            
            # Préparation avec types forcés
            data = (
                str(recipe['nom']),                                          # nom: string
                str(recipe.get('type_plat', 'Plats')),                      # type_plat: string
                str(recipe.get('origine', '')),                             # origine: string
                str(recipe['categorie']),                                   # categorie: string
                int(nb_personnes),                                          # nb_personnes: INT FORCÉ
                str(recipe.get('temps_preparation', '')),                   # temps_preparation: string
                str(recipe.get('difficulte', 'Normal')),                    # difficulte: string
                json.dumps(recipe.get('saisons', []), ensure_ascii=False),  # saisons: JSON string
                json.dumps(recipe.get('ingredients', []), ensure_ascii=False), # ingredients: JSON string
                json.dumps(recipe.get('preparation', []), ensure_ascii=False), # preparation: JSON string
                str(recipe.get('notes', ''))                                # note: string
            )
            
            cursor.execute("""
                INSERT INTO recettes (
                    nom, type_plat, origine, categorie, nb_personnes,
                    temps_preparation, difficulte, saisons, ingredients,
                    preparation, note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
            
            imported += 1
            print(f"✅ {recipe['nom']} (personnes: {nb_personnes})")
            
        except Exception as e:
            print(f"❌ {json_file.name}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 {imported} recettes importées avec types corrects!")

# Utilisation
if __name__ == "__main__":
    JSON_FOLDER = "recettes_json"
    DB_PATH = "data/delfmeals.db"
    
    import_recipes_safe(JSON_FOLDER, DB_PATH)
