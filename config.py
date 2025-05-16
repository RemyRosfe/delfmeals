# config.py
# Configuration Flask pour DelfMeals

import os
from datetime import timedelta

class Config:
    """Configuration de base pour Flask"""
    
    # Clé secrète pour les sessions (à changer en production)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-delfmeals-2024'
    
    # Configuration de la base de données SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'data', 'delfmeals.db')
    
    # Désactive le warning des modifications de modèles
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration des sessions
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    
    # Configuration des uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max pour les fichiers
    
    # Configuration générale
    RECETTES_PER_PAGE = 12  # Pour la pagination
    MENUS_PER_PAGE = 10

class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    
    # En production, utilisez une vraie clé secrète
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'prod-secret-change-me'

class TestingConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration par défaut
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}