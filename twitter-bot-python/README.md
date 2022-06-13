# Twitter bot

## Create virtual environment and install components
```
    $ python3 -m venv env
    $ source env/bin/activate
    $ pip install -r requirements.txt
    $ cp .env.example .env
    $ vi .env # feel with your data
````

## Run the bot
```
    $ python3 setup.py
````

## How to use
### Start
```
    $ curl http://localhost:{SERVER_PORT}/start
````
### Stop
```
    $ curl http://localhost:{SERVER_PORT}/stop
````
### Get current status
```
    $ curl http://localhost:{SERVER_PORT}/status
````
