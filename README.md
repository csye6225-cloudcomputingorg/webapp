# webapp

## Prerequisite for building and deploying your application locally
	- Install python 3.8 or above
	- Install the below dependencies:
	-	pip install Flask
	-	pip install Flask-Cors
	-	pip install SQLAlchemy
	-	pip install mysql-connector-python
	-	pip install python-dotenv
	-	pip install bcrypt
	-	pip install pytest requests
	- Run main.py (& C:/Users/18573/anaconda3/python.exe c:/Users/18573/Downloads/csye-6225-cloud-computing/main.py)
	- Run pytest integration_tests.py
	
	- ssh -i .ssh/digitalocean root@206.189.184.105
	
	- sudo apt update
	- sudo apt upgrade -y
	- sudo apt install python3 python3-pip -y
	- apt install python3.11-venv
	- mkdir -p /csye-6225-cloud-computing/webapp
	- scp -i .ssh/digitalocean -r C:/Users/18573/Downloads/csye-6225-cloud-computing root@206.189.184.105:/csye-6225-cloud-computing/webapp
		
	- export FLASK_APP=main.py
	- export FLASK_ENV=development
	- flask run --host=127.0.0.1 --port=5000

### Command for Certificate Import
aws acm import-certificate --certificate fileb://./demo_adityasrprakash_me.crt --private-key fileb://./private.key --certificate-chain fileb://./demo_adityasrprakash_me.ca-bundle --profile demo

