#
# import os
# import logging
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager
# from sqlalchemy.orm import DeclarativeBase
# from werkzeug.middleware.proxy_fix import ProxyFix
#
# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
#
#
# class Base(DeclarativeBase):
#     pass
#
#
# # Initialize extensions
# db = SQLAlchemy(model_class=Base)
# login_manager = LoginManager()
#
# # Create Flask app
# app = Flask(__name__)
# app.secret_key = os.environ.get("SESSION_SECRET") or "dev-secret-key-change-in-production"
# app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
#
# # Database configuration - prioritize PostgreSQL for Replit environment
# database_url = None
# db_type = None
#
# # Check for PostgreSQL first (Replit environment priority)
# database_url_env = os.environ.get("DATABASE_URL", "")
#
# # Try PostgreSQL first if DATABASE_URL is available and contains postgres
# if database_url_env and ("postgres" in database_url_env or "postgresql" in database_url_env):
#     try:
#         logging.info(f"Using PostgreSQL database (Replit environment): {database_url_env[:50]}...")
#
#         # Convert postgres:// to postgresql:// if needed for SQLAlchemy compatibility
#         if database_url_env.startswith("postgres://"):
#             database_url_env = database_url_env.replace("postgres://", "postgresql://", 1)
#
#         app.config["SQLALCHEMY_DATABASE_URI"] = database_url_env
#         app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
#             "pool_recycle": 300,
#             "pool_pre_ping": True,
#             "pool_size": 5,
#             "max_overflow": 10
#         }
#         db_type = "postgresql"
#
#         # Test PostgreSQL connection
#         from sqlalchemy import create_engine, text
#         test_engine = create_engine(database_url_env, pool_pre_ping=True)
#         with test_engine.connect() as conn:
#             conn.execute(text("SELECT 1"))
#         logging.info("PostgreSQL database connection successful")
#         database_url = database_url_env
#
#     except Exception as e:
#         logging.warning(f"PostgreSQL connection failed: {e}")
#         database_url = None
#
# # Fallback to MySQL (local development)
# if not database_url:
#     mysql_config = {
#         'host': os.environ.get('MYSQL_HOST', 'localhost'),
#         'port': os.environ.get('MYSQL_PORT', '3306'),
#         'user': os.environ.get('MYSQL_USER', 'root'),
#         'password': os.environ.get('MYSQL_PASSWORD', 'root123'),
#         'database': os.environ.get('MYSQL_DATABASE', 'it_lobby')
#     }
#
#     try:
#         database_url = f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}"
#         logging.info(f"Using MySQL database: {database_url}")
#
#         # Test MySQL connection
#         from sqlalchemy import create_engine, text
#         test_engine = create_engine(database_url, connect_args={'connect_timeout': 5})
#         with test_engine.connect() as conn:
#             conn.execute(text("SELECT 1"))
#
#         app.config["SQLALCHEMY_DATABASE_URI"] = database_url
#         app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
#             "pool_recycle": 300,
#             "pool_pre_ping": True,
#             "pool_size": 10,
#             "max_overflow": 20
#         }
#         db_type = "mysql"
#         logging.info("MySQL database connection successful")
#
#     except Exception as e:
#         logging.error(f"MySQL connection failed: {e}")
#         database_url = None
#
# # Final fallback to SQLite if both PostgreSQL and MySQL fail
# if not database_url:
#     database_url = "sqlite:///wms_development.db"
#     app.config["SQLALCHEMY_DATABASE_URI"] = database_url
#     app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
#         "pool_recycle": 300,
#         "pool_pre_ping": True
#     }
#     db_type = "sqlite"
#     logging.info("Using SQLite database as fallback")
#
# # Store database type
# app.config["DB_TYPE"] = db_type
# logging.info(f"Database type set to: {db_type}")
#
# # Initialize extensions
# db.init_app(app)
# login_manager.init_app(app)
# login_manager.login_view = 'login'
# login_manager.login_message = 'Please log in to access this page.'
#
# # SAP B1 Configuration
# app.config['SAP_B1_SERVER'] = os.environ.get('SAP_B1_SERVER', 'https://10.112.253.173:50000')
# app.config['SAP_B1_USERNAME'] = os.environ.get('SAP_B1_USERNAME', 'manager')
# app.config['SAP_B1_PASSWORD'] = os.environ.get('SAP_B1_PASSWORD', '1422')
# app.config['SAP_B1_COMPANY_DB'] = os.environ.get('SAP_B1_COMPANY_DB', 'SBODemoUS')
#
# # Import models
# import models
# import models_extensions
#
# # Import module models
# from modules.invoice_creation import models as invoice_models  # noqa: F401
#
# with app.app_context():
#     # Create tables
#     db.create_all()
#     logging.info("✅ Database tables created")
#
#     # Drop unique constraint if exists
#     try:
#         from sqlalchemy import text
#         with db.engine.connect() as conn:
#             # PostgreSQL compatible query
#             if db_type == "postgresql":
#                 result = conn.execute(text("""
#                     SELECT constraint_name
#                     FROM information_schema.table_constraints
#                     WHERE table_schema = 'public'
#                     AND table_name = 'serial_number_transfer_serials'
#                     AND constraint_name = 'unique_serial_per_item'
#                 """))
#             else:
#                 # MySQL query
#                 result = conn.execute(text("""
#                     SELECT CONSTRAINT_NAME
#                     FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
#                     WHERE TABLE_SCHEMA = DATABASE()
#                     AND TABLE_NAME = 'serial_number_transfer_serials'
#                     AND CONSTRAINT_NAME = 'unique_serial_per_item'
#                 """))
#             if result.fetchone():
#                 conn.execute(text("ALTER TABLE serial_number_transfer_serials DROP INDEX unique_serial_per_item"))
#                 conn.commit()
#                 logging.info("Dropped unique_serial_per_item constraint")
#     except Exception as e:
#         logging.warning(f"⚠️ Could not drop unique constraint: {e}")
#
#     # Create default data
#     try:
#         from models_extensions import Branch
#         from werkzeug.security import generate_password_hash
#         from models import User
#
#         default_branch = Branch.query.filter_by(id='BR001').first()
#         if not default_branch:
#             default_branch = Branch(
#                 id='BR001',
#                 name='Main Branch',
#                 branch_code='BR001',
#                 branch_name='Main Branch',
#                 description='Main Office Branch',
#                 address='Main Office',
#                 phone='123-456-7890',
#                 email='main@company.com',
#                 manager_name='Branch Manager',
#                 active=True,
#                 is_default=True
#             )
#             db.session.add(default_branch)
#             logging.info("✅ Default branch created")
#
#         admin = User.query.filter_by(username='admin').first()
#         if not admin:
#             admin = User(
#                 username='admin',
#                 email='admin@company.com',
#                 password_hash=generate_password_hash('admin123'),
#                 first_name='System',
#                 last_name='Administrator',
#                 role='admin',
#                 branch_id='BR001',
#                 branch_name='Main Branch',
#                 default_branch_id='BR001',
#                 active=True,
#                 must_change_password=False
#             )
#             db.session.add(admin)
#             logging.info("✅ Default admin user created")
#
#         db.session.commit()
#         logging.info("✅ Default data initialized")
#
#     except Exception as e:
#         logging.error(f"❌ Error initializing default data: {e}")
#         db.session.rollback()
#
# # Setup logging
# try:
#     from logging_config import setup_logging
#     logger = setup_logging(app)
#     logger.info("🚀 WMS Application starting with file-based logging")
# except Exception as e:
#     logging.warning(f"⚠️ Logging setup failed: {e}. Using basic logging.")
#
# # Register blueprints
# from modules.inventory_transfer.routes import transfer_bp
# from modules.serial_item_transfer.routes import serial_item_bp
# from modules.invoice_creation.routes import invoice_bp
#
# app.register_blueprint(transfer_bp)
# app.register_blueprint(serial_item_bp)
# app.register_blueprint(invoice_bp)
#
# # Import routes
# import routes

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)


class Base(DeclarativeBase):
    pass


# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or "dev-secret-key-change-in-production"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration - prioritize PostgreSQL for Replit environment
database_url = None
db_type = None

# Check for PostgreSQL first (Replit environment priority)
database_url_env = os.environ.get("DATABASE_URL", "")

# Try PostgreSQL first if DATABASE_URL is available and contains postgres
if database_url_env and ("postgres" in database_url_env or "postgresql" in database_url_env):
    try:
        logging.info(f"Using PostgreSQL database (Replit environment): {database_url_env[:50]}...")

        # Convert postgres:// to postgresql:// if needed for SQLAlchemy compatibility
        if database_url_env.startswith("postgres://"):
            database_url_env = database_url_env.replace("postgres://", "postgresql://", 1)

        app.config["SQLALCHEMY_DATABASE_URI"] = database_url_env
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
            "pool_size": 5,
            "max_overflow": 10
        }
        db_type = "postgresql"

        # Test PostgreSQL connection
        from sqlalchemy import create_engine, text
        test_engine = create_engine(database_url_env, pool_pre_ping=True)
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logging.info("✅ PostgreSQL database connection successful")
        database_url = database_url_env

    except Exception as e:
        logging.warning(f"⚠️ PostgreSQL connection failed: {e}")
        database_url = None

# Fallback to MySQL (local development)
if not database_url:
    mysql_config = {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'port': os.environ.get('MYSQL_PORT', '3306'),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', 'root123'),
        'database': os.environ.get('MYSQL_DATABASE', 'it_lobby')
    }

    try:
        database_url = f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}"
        logging.info(f"Using MySQL database: {database_url}")

        # Test MySQL connection
        from sqlalchemy import create_engine, text
        test_engine = create_engine(database_url, connect_args={'connect_timeout': 5})
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
            "pool_size": 10,
            "max_overflow": 20
        }
        db_type = "mysql"
        logging.info("✅ MySQL database connection successful")

    except Exception as e:
        logging.error(f"❌ MySQL connection failed: {e}")
        database_url = None

# Final fallback to SQLite if both PostgreSQL and MySQL fail
if not database_url:
    database_url = "sqlite:///wms_development.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True
    }
    db_type = "sqlite"
    logging.info("⚠️ Using SQLite database as fallback")

# Store database type
app.config["DB_TYPE"] = db_type

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# SAP B1 Configuration
app.config['SAP_B1_SERVER'] = os.environ.get('SAP_B1_SERVER', 'https://10.112.253.173:50000')
app.config['SAP_B1_USERNAME'] = os.environ.get('SAP_B1_USERNAME', 'manager')
app.config['SAP_B1_PASSWORD'] = os.environ.get('SAP_B1_PASSWORD', '1422')
app.config['SAP_B1_COMPANY_DB'] = os.environ.get('SAP_B1_COMPANY_DB', 'SBODemoUS')

# Import models
import models
import models_extensions
from modules.invoice_creation import models as invoice_models  # noqa: F401

with app.app_context():
    # Create tables
    db.create_all()
    logging.info("✅ Database tables created")

    # Drop unique constraint if exists
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            # PostgreSQL compatible query
            if db_type == "postgresql":
                result = conn.execute(text("""
                    SELECT constraint_name
                    FROM information_schema.table_constraints
                    WHERE table_schema = 'public'
                    AND table_name = 'serial_number_transfer_serials'
                    AND constraint_name = 'unique_serial_per_item'
                """))
                if result.fetchone():
                    conn.execute(text("ALTER TABLE serial_number_transfer_serials DROP CONSTRAINT unique_serial_per_item"))
                    conn.commit()
                    logging.info("Dropped unique_serial_per_item constraint")
            else:
                # MySQL query
                result = conn.execute(text("""
                    SELECT CONSTRAINT_NAME
                    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'serial_number_transfer_serials'
                    AND CONSTRAINT_NAME = 'unique_serial_per_item'
                """))
                if result.fetchone():
                    conn.execute(text("ALTER TABLE serial_number_transfer_serials DROP INDEX unique_serial_per_item"))
                    conn.commit()
                    logging.info("Dropped unique_serial_per_item constraint")
    except Exception as e:
        logging.warning(f"⚠️ Could not drop unique constraint: {e}")

    # Create default data
    try:
        from models_extensions import Branch
        from werkzeug.security import generate_password_hash
        from models import User

        default_branch = Branch.query.filter_by(id='BR001').first()
        if not default_branch:
            default_branch = Branch(
                id='BR001',
                name='Main Branch',
                branch_code='BR001',
                branch_name='Main Branch',
                description='Main Office Branch',
                address='Main Office',
                phone='123-456-7890',
                email='main@company.com',
                manager_name='Branch Manager',
                active=True,
                is_default=True
            )
            db.session.add(default_branch)
            logging.info("✅ Default branch created")

        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@company.com',
                password_hash=generate_password_hash('admin123'),
                first_name='System',
                last_name='Administrator',
                role='admin',
                branch_id='BR001',
                branch_name='Main Branch',
                default_branch_id='BR001',
                active=True,
                must_change_password=False
            )
            db.session.add(admin)
            logging.info("✅ Default admin user created")

        db.session.commit()
        logging.info("✅ Default data initialized")

    except Exception as e:
        logging.error(f"❌ Error initializing default data: {e}")
        db.session.rollback()

# Setup logging
try:
    from logging_config import setup_logging
    logger = setup_logging(app)
    logger.info("🚀 WMS Application starting with file-based logging")
except Exception as e:
    logging.warning(f"⚠️ Logging setup failed: {e}. Using basic logging.")

# Register blueprints
from modules.inventory_transfer.routes import transfer_bp
from modules.serial_item_transfer.routes import serial_item_bp
from modules.invoice_creation.routes import invoice_bp

app.register_blueprint(transfer_bp)
app.register_blueprint(serial_item_bp)
app.register_blueprint(invoice_bp)

# Import routes
import routes

