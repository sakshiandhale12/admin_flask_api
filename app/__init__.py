from flask import Flask
from .extensions import db, api
import os
from .resources import ns_subsubgroup, ns_subgroup, ns_state, ns_stage, ns_roleprogramm, ns_role, ns_rolelink, ns_program, ns_module, ns, ns_miscellaneous, ns_business, ns_ecode, ns_city, ns_company, ns_currency, ns_customer, ns_token, ns_department, ns_division, ns_Finyr, ns_item, ns_itemm, ns_location
from .resources import ns_upload
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from .resources import authorizations
from datetime import timedelta

def create_app():
    app = Flask(__name__)

    # Configuration
    # app.config['APPLICATION_ROOT'] = '/'
    # app.config['PREFERRED_URL_SCHEME'] = 'HTTPS'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI') + "?options=-c%20search_path%3Depps_admin"
    app.config['JWT_SECRET_KEY'] = 'SECRET_KEY$123'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['SERVER_NAME'] = '192.168.1.184:5000'  # Change this to match your server configuration

    load_dotenv()

    # Initialize extensions
    db.init_app(app)
    api.init_app(app)
    jwt = JWTManager(app)

    # Register API namespaces
    api.add_namespace(ns_ecode)
    api.add_namespace(ns_business)
    api.add_namespace(ns_city)
    api.add_namespace(ns_company)
    api.add_namespace(ns_currency)
    api.add_namespace(ns_customer)
    api.add_namespace(ns_department)
    api.add_namespace(ns_division)
    api.add_namespace(ns)
    api.add_namespace(ns_Finyr)
    api.add_namespace(ns_item)
    api.add_namespace(ns_itemm)
    api.add_namespace(ns_location)
    api.add_namespace(ns_miscellaneous)
    api.add_namespace(ns_module)
    api.add_namespace(ns_program)
    api.add_namespace(ns_rolelink)
    api.add_namespace(ns_role)
    api.add_namespace(ns_roleprogramm)
    api.add_namespace(ns_stage)
    api.add_namespace(ns_state)
    api.add_namespace(ns_subgroup)
    api.add_namespace(ns_subsubgroup)
    api.add_namespace(ns_token)
    api.add_namespace(ns_upload)



    # Define API documentation details
    api.authorizations = authorizations
    api.security = 'Bearer Auth'
    api.version = '1.0'
    api.title = 'EPPS-CORE REST API Documentation'
    api.description = 'API documentation for EPPS-CORE'

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
