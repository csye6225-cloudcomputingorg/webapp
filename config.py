import os
from app import app
from flaskext.mysql import MySQL
from dotenv import load_dotenv

# load environment variables
load_dotenv()


# fetch database credentials from environment variables
def set_db_creds():
    app.config['MYSQL_DATABASE_USER'] = os.getenv('db_user')
    app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('db_password')
    #app.config['MYSQL_DATABASE_DB'] = os.getenv('db_name')
    app.config['MYSQL_DATABASE_HOST'] = os.getenv('db_host')
    print(os.getenv('db_user'))

    #print(os.getenv('db_password'), os.getenv('db_user'), os.getenv('db_host'))


mysql = MySQL()
mysql.init_app(app)
