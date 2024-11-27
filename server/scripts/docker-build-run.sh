docker build -t build-now .
PORT=5000 
docker run --name build-now --env-file .env-docker -it -p 5000:5000 --rm buid-now