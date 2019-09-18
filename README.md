mv .env.example .env

python3 -m venv env

source env/bin/activate

pip install -r requirements.txt

flask run --port 5000 --host=0.0.0.0

ngrok http 5000

ssh -R 80:localhost:5000 tunnel.us.ngrok.com http

ssh -R 80:localhost:5000 serveo.net

lt --port 5000
