mv .env.example .env

python3 -m venv env

source env/bin/activate

pip install -r requirements.txt

flask run --port 5000 --host=0.0.0.0

ngrok http 5000
