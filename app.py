# app.py
# Application Flask principale pour DelfMeals
import os
import sys
from flask import Flask, render_template

# Ajouter le répertoire racine au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports des modules DelfMeals
from config import config
from models.database import db, init_database  # Importer l'instance db depuis models

def create_app(config_name='development'):
    """
    Factory pour créer l'application Flask
    """
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(config[config_name])
    
    # Initialiser les extensions avec l'instance db importée
    db.init_app(app)
    
    # Créer les dossiers nécessaires
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'images'), exist_ok=True)
    
    # Initialiser la base de données SQLite si nécessaire
    with app.app_context():
        # Vérifier si la base existe, sinon la créer
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if not os.path.exists(db_path):
            print("🗃️ Création de la base de données...")
            init_database()
    
    # Enregistrer les blueprints (routes)
    from routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from routes.recettes import recettes as recettes_blueprint
    app.register_blueprint(recettes_blueprint, url_prefix='/recettes')
    
    from routes.menus import menus as menus_blueprint
    app.register_blueprint(menus_blueprint, url_prefix='/menus')
    
    # Contexte des templates (variables globales pour tous les templates)
    @app.context_processor
    def inject_global_vars():
        return {
            'app_name': 'DelfMeals',
            'version': '1.0.0',
            # Ajoutez ici d'autres variables globales si nécessaire
        }
    
    # Gestionnaire d'erreurs personnalisés
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Commande CLI pour initialiser la base
    @app.cli.command()
    def init_db():
        """Initialise la base de données"""
        init_database()
        print("✅ Base de données initialisée")
    
    # Commande CLI pour migrer les recettes test
    @app.cli.command()
    def migrate_test_data():
        """Migre les recettes de test vers la base"""
        from utils.migration import migrer_recettes_test
        migrer_recettes_test()
        print("✅ Recettes de test migrées")
    
    return app

# Créer l'application
app = create_app(os.environ.get('FLASK_ENV', 'development'))

# Initialiser la base au démarrage (seulement sur Render)
if os.environ.get('RENDER') == 'true':
    print("🔄 Render détecté - Initialisation de la base")
    from init_db import initialiser_base
    initialiser_base()

if __name__ == '__main__':
    # Lancement de l'application en mode développement
    print("🍽️ Démarrage de DelfMeals...")
    print(f"🌐 Accès: http://localhost:5000")
    print(f"🔧 Mode: {app.config.get('ENV', 'development')}")
    
    # Lancer le serveur
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=True
    )
