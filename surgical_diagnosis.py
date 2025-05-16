#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic chirurgical - Identifie EXACTEMENT quelles cellules posent problème
"""

import sqlite3

DB_PATH = "data/delfmeals.db"

def surgical_diagnosis():
    """Diagnostic précis des problèmes de types restants"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔍 DIAGNOSTIC CHIRURGICAL\n")
    print("="*70)
    
    # Test 1: Identification des types problématiques dans nb_personnes
    print("1️⃣ ANALYSE nb_personnes:")
    cursor.execute("SELECT id, nom, nb_personnes, typeof(nb_personnes) FROM recettes ORDER BY id")
    all_nb_pers = cursor.fetchall()
    
    nb_pers_problems = []
    for row_id, nom, value, type_name in all_nb_pers:
        if type_name != 'integer' and value is not None:
            nb_pers_problems.append((row_id, nom, value, type_name))
    
    if nb_pers_problems:
        print(f"  ❌ {len(nb_pers_problems)} recettes avec nb_personnes non-entier:")
        for row_id, nom, value, type_name in nb_pers_problems:
            print(f"    #{row_id:3d} {nom:<40} → '{value}' ({type_name})")
    else:
        print(f"  ✅ Tous les nb_personnes sont corrects")
    
    # Test 2: Identification des types problématiques dans temps_preparation
    print(f"\n2️⃣ ANALYSE temps_preparation:")
    cursor.execute("SELECT id, nom, temps_preparation, typeof(temps_preparation) FROM recettes ORDER BY id")
    all_temps = cursor.fetchall()
    
    temps_problems = []
    for row_id, nom, value, type_name in all_temps:
        if type_name != 'integer' and value is not None:
            temps_problems.append((row_id, nom, value, type_name))
    
    if temps_problems:
        print(f"  ❌ {len(temps_problems)} recettes avec temps_preparation non-entier:")
        for row_id, nom, value, type_name in temps_problems:
            print(f"    #{row_id:3d} {nom:<40} → '{value}' ({type_name})")
    else:
        print(f"  ✅ Tous les temps_preparation sont corrects")
    
    # Test 3: Test des opérations qui causent l'erreur
    print(f"\n3️⃣ TEST DES OPÉRATIONS PROBLÉMATIQUES:")
    
    # Test tri nb_personnes
    print(f"  Tri par nb_personnes:")
    try:
        cursor.execute("SELECT id, nom, nb_personnes FROM recettes ORDER BY nb_personnes ASC LIMIT 5")
        print(f"    ✅ Tri réussi")
    except Exception as e:
        print(f"    ❌ ERREUR: {e}")
    
    # Test tri temps_preparation
    print(f"  Tri par temps_preparation:")
    try:
        cursor.execute("SELECT id, nom, temps_preparation FROM recettes ORDER BY temps_preparation ASC LIMIT 5")
        print(f"    ✅ Tri réussi")
    except Exception as e:
        print(f"    ❌ ERREUR: {e}")
    
    # Test comparaison nb_personnes
    print(f"  Comparaison nb_personnes > 2:")
    try:
        cursor.execute("SELECT COUNT(*) FROM recettes WHERE nb_personnes > 2")
        count = cursor.fetchone()[0]
        print(f"    ✅ {count} recettes trouvées")
    except Exception as e:
        print(f"    ❌ ERREUR: {e}")
    
    # Test comparaison temps_preparation
    print(f"  Comparaison temps_preparation > 30:")
    try:
        cursor.execute("SELECT COUNT(*) FROM recettes WHERE temps_preparation > 30")
        count = cursor.fetchone()[0]
        print(f"    ✅ {count} recettes trouvées")
    except Exception as e:
        print(f"    ❌ ERREUR: {e}")
    
    # Test 4: Détection des valeurs mixtes dans d'autres colonnes
    print(f"\n4️⃣ VÉRIFICATION AUTRES COLONNES:")
    
    # Test ID (parfois problématique)
    cursor.execute("SELECT id, typeof(id) FROM recettes WHERE typeof(id) != 'integer'")
    bad_ids = cursor.fetchall()
    if bad_ids:
        print(f"  ❌ IDs non-entiers détectés: {len(bad_ids)}")
        for row_id, type_name in bad_ids[:3]:
            print(f"    ID {row_id} est {type_name}")
    else:
        print(f"  ✅ Tous les IDs sont entiers")
    
    conn.close()
    
    # Résumé des problèmes à corriger
    print(f"\n" + "="*70)
    print(f"📋 RÉSUMÉ - CELLULES À CORRIGER MANUELLEMENT:")
    print(f"="*70)
    
    print(f"\n🔧 Dans DB Browser, corrigez ces cellules EXACTEMENT:")
    
    if nb_pers_problems:
        print(f"\n  NB_PERSONNES (retirez les guillemets):")
        for row_id, nom, value, type_name in nb_pers_problems:
            if isinstance(value, str):
                # Extrait le nombre de la string
                import re
                numbers = re.findall(r'\d+', value)
                if numbers:
                    corrected = int(numbers[0])
                    print(f"    Ligne #{row_id}: '{value}' → {corrected}")
                else:
                    print(f"    Ligne #{row_id}: '{value}' → 4 (défaut)")
    
    if temps_problems:
        print(f"\n  TEMPS_PREPARATION (convertissez en minutes):")
        for row_id, nom, value, type_name in temps_problems:
            if isinstance(value, str):
                if value == '' or not value:
                    print(f"    Ligne #{row_id}: '{value}' → NULL")
                else:
                    # Essaie de parser le temps
                    import re
                    if 'min' in value:
                        numbers = re.findall(r'(\d+)\s*min', value)
                        if numbers:
                            print(f"    Ligne #{row_id}: '{value}' → {numbers[0]}")
                        else:
                            print(f"    Ligne #{row_id}: '{value}' → 30 (défaut)")
                    else:
                        print(f"    Ligne #{row_id}: '{value}' → 30 (défaut)")
    
    total_problems = len(nb_pers_problems) + len(temps_problems)
    return total_problems

def simple_type_fix_queries():
    """Génère des requêtes SQL simples pour corriger les types"""
    
    print(f"\n" + "="*70)
    print(f"💡 REQUÊTES SQL RAPIDES (Copiez dans Execute SQL):")
    print(f"="*70)
    
    queries = [
        "-- Force la conversion des nb_personnes string en integer",
        "UPDATE recettes SET nb_personnes = CAST(nb_personnes AS INTEGER) WHERE typeof(nb_personnes) = 'text';",
        "",
        "-- Remplace les temps vides par NULL", 
        "UPDATE recettes SET temps_preparation = NULL WHERE temps_preparation = '';",
        "",
        "-- Force la conversion des temps numériques",
        "UPDATE recettes SET temps_preparation = CAST(temps_preparation AS INTEGER) WHERE typeof(temps_preparation) = 'text' AND temps_preparation GLOB '[0-9]*';",
        "",
        "-- Vérification finale",
        "SELECT id, nom, nb_personnes, typeof(nb_personnes), temps_preparation, typeof(temps_preparation) FROM recettes WHERE typeof(nb_personnes) != 'integer' OR (typeof(temps_preparation) != 'integer' AND temps_preparation IS NOT NULL);"
    ]
    
    for query in queries:
        print(query)

if __name__ == "__main__":
    print("=== DIAGNOSTIC CHIRURGICAL TYPES ===\n")
    
    problems = surgical_diagnosis()
    
    if problems > 0:
        simple_type_fix_queries()
        print(f"\n🎯 ACTIONS:")
        print(f"1. Corrigez les {problems} cellules listées ci-dessus")
        print(f"2. OU utilisez les requêtes SQL pour correction automatique")
        print(f"3. Relancez Flask après correction")
    else:
        print(f"\n🤔 Types semblent corrects...")
        print(f"L'erreur vient peut-être du code Flask")
        print(f"Partagez le code de la route qui plante pour aide")
