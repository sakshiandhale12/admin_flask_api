from flask import Flask
from .extensions import db, api
import os
from .resources import ns, ns_business, ns_ecode, ns_city, ns_company, ns_currency, ns_customer,ns_token,ns_department,ns_division,ns_Finyr,ns_item,ns_itemm,ns_location
from flask import Flask
from flask_jwt_extended import JWTManager
from .extensions import db
from dotenv import load_dotenv
from  .resources  import authorizations
from datetime import timedelta

def create_app():
    app = Flask(__name__)
# Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI') + "?options=-c%20search_path%3Depps_admin"
    app.config['JWT_SECRET_KEY'] = 'SECRET_KEY$123'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)  
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  
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
    api.add_namespace(ns_token)


    api.authorizations = authorizations
    api.security = 'Bearer Auth'
    api.version = '1.0'
    api.title = 'EPPS-CORE REST API Documentation'
    api.description = 'API documentation for EPPS-CORE'

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()








