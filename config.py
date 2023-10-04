import os
from app import app
from flaskext.mysql import MySQL
from dotenv import load_dotenv

# load environment variables
load_dotenv()


# fetch database credentials from environment variables
def set_db_creds():
    app.config['MYSQL_DATABASE_USER'] = os.environ.get('db_user')
    app.config['MYSQL_DATABASE_PASSWORD'] = os.environ.get('db_password')
    #app.config['MYSQL_DATABASE_DB'] = os.environ.get('db_name')
    app.config['MYSQL_DATABASE_HOST'] = os.environ.get('db_host')

    #print(os.environ.get('db_password'), os.environ.get('db_user'), os.environ.get('db_host'))


mysql = MySQL()
mysql.init_app(app)
