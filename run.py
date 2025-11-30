"""
AlexRentaCar Admin Application Factory
Initializes Flask app with all extensions and blueprints
"""
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
talisman = Talisman()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
cache = Cache()


def create_app(config_name=None):
    """Application factory pattern"""
    from app.config import get_config
    
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = 'development'
    
    app.config.from_object(get_config(config_name))
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # Initialize cache (optional - can be disabled)
    if app.config.get('ENABLE_CACHE', False):
        try:
            cache_config = {
                'CACHE_TYPE': 'RedisCache' if app.config['CACHE_TYPE'] == 'redis' else 'SimpleCache',
                'CACHE_DEFAULT_TIMEOUT': app.config['CACHE_DEFAULT_TIMEOUT']
            }
            if app.config['CACHE_TYPE'] == 'redis':
                cache_config['CACHE_REDIS_URL'] = app.config['CACHE_REDIS_URL']
            
            cache.init_app(app, config=cache_config)
            app.logger.info("Cache enabled successfully")
        except Exception as e:
            app.logger.warning(f"Cache initialization failed: {e}. Continuing without cache.")
            app.config['ENABLE_CACHE'] = False
    else:
        # Initialize with simple cache as fallback
        cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})
        app.logger.info("Cache disabled - using SimpleCache as fallback")
    
    # Initialize rate limiter (optional)
    if app.config.get('RATELIMIT_ENABLED', False):
        try:
            limiter.init_app(app)
            app.logger.info("Rate limiting enabled")
        except Exception as e:
            app.logger.warning(f"Rate limiter initialization failed: {e}")
    
    # Initialize Talisman for security headers
    if not app.config['DEBUG']:
        talisman.init_app(
            app,
            force_https=app.config['TALISMAN_FORCE_HTTPS'],
            content_security_policy=app.config['TALISMAN_CONTENT_SECURITY_POLICY']
        )
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Usuario
        return Usuario.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.settings_routes import settings_bp
    from app.routes.modulos_routes import modulos_bp
    from app.routes.reportes_routes import reportes_bp
    from app.routes.mecanicos_routes import mecanicos_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(modulos_bp, url_prefix='/modulos')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')
    app.register_blueprint(mecanicos_bp, url_prefix='/mecanicos')
    
    # Root route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    # CLI commands
    @app.cli.command()
    def init_db():
        """Initialize the database with initial data"""
        from app.services.user_service import create_initial_data
        create_initial_data()
        print("Database initialized successfully!")
    
    @app.cli.command()
    def create_admin():
        """Create admin user"""
        from app.services.user_service import create_user
        username = input("Enter username: ")
        email = input("Enter email: ")
        password = input("Enter password: ")
        nombre = input("Enter first name: ")
        apellido = input("Enter last name: ")
        
        user = create_user(
            username=username,
            password=password,
            email=email,
            nombre=nombre,
            apellido=apellido,
            rol='admin'
        )
        if user:
            print(f"Admin user {username} created successfully!")
        else:
            print("Error creating admin user")
    
    return app

app = create_app()


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(5000),
        debug=app.config['DEBUG']
    )

