# smm-bots
Bots for reposting messages in Twitter and TG

# how to install
1. Prerequisite. Install docker and docker-compose
2. Clone file `telegram-bot/.env.example` to `telegram-bot/.env` 
```shell script
cp telegram-bot/.env.example telegram-bot/.env
```
3.Edit file `telegram-bot/.env` and fill the variables
```shell script
vi telegram-bot/.env
```
4.Clone file `twitter-bot-python/.env.example` to `twitter-bot-python/.env`
```shell script
cp twitter-bot-python/.env.example twitter-bot-python/.env
```
5.Edit file `twitter-bot-python/.env` and fill the variables
```shell script
vi twitter-bot-python/.env
```
6. Build containers with docker-compose
```shell script
docker-compose build
```

# how to run services
```shell script
docker-compose up
```

# how to stop services
```shell script
docker-compose down
```
