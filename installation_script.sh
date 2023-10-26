#!/bin/bash

echo_info () {
    echo $1
}

echo_info "---------UPDATES-BEING-INSTALLED---------"

# Update the system
sudo apt update && sudo apt upgrade -y

# Installing python server
echo_info "---------INSTALLING-PYTHON---------"
sudo apt install -y python3 python3-pip

# Create a Python virtual environment
sudo apt install python3.11-venv -y
python3.11 -m venv myenv
source myenv/bin/activate

# Install Python dependencies (update libraries for postgreSQL)
pip3 install bcrypt==4.0.1 blinker==1.6.3 certifi==2023.7.22 charset-normalizer==3.3.0 click==8.1.7 Flask==2.2.5 Flask-Cors==4.0.0 Flask-MySQL==1.5.2 greenlet==3.0.0 idna==3.4 iniconfig==2.0.0 itsdangerous==2.1.2 Jinja2==3.1.2 MarkupSafe==2.1.3 mysql-connector-python==8.1.0 packaging==23.2 pip==23.0.1 pluggy==1.3.0 protobuf==4.21.12 PyMySQL==1.1.0 pytest==7.4.2 python-dotenv==1.0.0 requests==2.31.0 setuptools==66.1.1 SQLAlchemy==2.0.21 typing_extensions==4.8.0 urllib3==2.0.6 Werkzeug==3.0.0

# Start and enable MariaDB service
# echo_info "---------INSTALLING-MARIADB---------"
# sudo apt install mariadb-server -y
# sudo systemctl start mariadb
# sudo systemctl enable mariadb
# sudo systemctl status mariadb

# sudo mysql -u root -ppassword -e 'CREATE DATABASE webapp;',
# sudo mysql -u root --skip-password -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'password';"

# Secure MariaDB installation (optional but recommended)
# Make sure to set a strong password for the root user
# sudo mysql_secure_installation

# Installing UNZIP
echo_info "---------INSTALLING-UNZIP---------"
sudo apt install -y unzip

# Download and unzip your web application code
mkdir webapp
unzip webapp.zip -d webapp
rm webapp.zip
cd webapp

sudo groupadd csye6225
sudo useradd -s /bin/false -g csye6225 -d /home/admin -m csye6225
sudo chown csye6225:csye6225 -R .
sudo chmod -R 755 .

sudo mv webapp.service /etc/systemd/system/webapp.service

sudo systemctl daemon-reload
sudo systemctl enable webapp
sudo systemctl start webapp
sudo systemctl restart webapp
sudo systemctl stop webapp

deactivate
