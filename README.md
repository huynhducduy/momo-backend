mv .env.example .env

source env/bin/activate

flask run --port 8080 --host=0.0.0.0

ssh -R 80:localhost:3000 serveo.net
