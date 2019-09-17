mv .env.example .env

python3 -m venv env

source env/bin/activate

pip install -r requirements.txt

flask run --port 8080 --host=0.0.0.0

ssh -R 80:localhost:3000 serveo.net
