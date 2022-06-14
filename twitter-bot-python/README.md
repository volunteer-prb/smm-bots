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

1. Get authorization URL
```
    $ curl http://localhost:{SERVER_PORT}/authorization-url
````
Example response
```
{
    "url": "https://api.twitter.com/oauth/authorize?oauth_token=3ehh4QAAAAABdoTMAAABgWRadpw"
}
```
2. Open the URL in a browser, authorize the app and copy a PIN
3. Post the PIN to the endpoint
```
    $ curl -X POST --data-raw '{"verifier" : "{PIN}"} http://localhost:{SERVER_PORT}/start
````
Example response
```
{
    "status": "started"
}
```
### Stop
```
    $ curl http://localhost:{SERVER_PORT}/stop
````
Example response
```
{
    "status": "stopped"
}
```
### Get current status
```
    $ curl http://localhost:{SERVER_PORT}/status
````
Example response
```
{
    "status": "started"
}
```