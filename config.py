import os
from app import app
from flaskext.mysql import MySQL
from dotenv import load_dotenv
import requests

# load environment variables
# load_dotenv()

# Fetch user data
user_data_url = "http://169.254.169.254/latest/user-data"
response = requests.get(user_data_url)
user_data = response.text

# Split user data into lines
lines = user_data.split('\n')

# Parse environment variable assignments
environment_variables = {}
for line in lines:
    if line.strip().startswith("export "):
        parts = line.strip()[7:].split("=")
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()
            environment_variables[key] = value

# Access the environment variables
db_host = environment_variables.get("DB_HOST")
db_name = environment_variables.get("DB_NAME")
db_user = environment_variables.get("DB_USER")
db_password = environment_variables.get("DB_PASSWORD")


# fetch database credentials from environment variables
def set_db_creds():
    app.config['MYSQL_DATABASE_USER'] = db_user
    app.config['MYSQL_DATABASE_PASSWORD'] = db_password
    #app.config['MYSQL_DATABASE_DB'] = db_name
    app.config['MYSQL_DATABASE_HOST'] = db_host
    # print(os.getenv('db_user'))

    #print(os.getenv('db_password'), os.getenv('db_user'), os.getenv('db_host'))


mysql = MySQL()
mysql.init_app(app)
