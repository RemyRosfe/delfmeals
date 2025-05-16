# run_flask.py
# Script de lancement avec vérifications pour DelfMeals

import os
import sys

def main():
    """Lance l'application DelfMeals en mode développement"""
    
    print("🍽️  Démarrage de DelfMeals...")
    
    # Importer et créer l'application
    from app import create_app
    
    # Créer l'app avec la configuration de développement
    app = create_app('development')
    
    # Vérifications avec contexte d'application
    with app.app_context():
        print("🔍 Vérification de la base de données...")
        
        try:
            from core.database_manager import DatabaseManager
            with DatabaseManager() as db:
                stats = db.get_statistiques()
                print(f"📊 {stats['nb_recettes']} recettes et {stats['nb_menus']} menus en base")
        except Exception as e:
            print(f"⚠️  Problème avec la base de données: {e}")
            print("💡 L'application va démarrer quand même.")
    
    # Informations de démarrage
    print(f"🌐 URL: http://localhost:5000")
    print(f"🔧 Mode: {app.config.get('ENV', 'development')}")
    print("✨ Application prête !")
    print("-" * 50)
    
    # Lancer le serveur Flask
    try:
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de l'application")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
