import needle from 'needle';
import OAuth from 'oauth-1.0a';
import crypto from 'crypto';
import * as readline from "readline";

const terminal = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const token = 'AAAAAAAAAAAAAAAAAAAAAFMSdgEAAAAASNbPRcmh99yU9ao2JhXoGm28i0c%3DXl0hfpjPqzRLGGjNdSe6h0BDDF6Ro9Mt2QxMx1PCE8DKg8yR89';
const endpointUrl = `https://api.twitter.com/2/`;
const consumer_key = 'lvRDzUBhH2AyFUEcFjTY8qxXo';
const consumer_secret = 'KXYnHH0fxWGS7eMQ6qOYFIUvnlNLOkBEQVkEI0FELf6O6TvSNw';

const requestTokenURL = 'https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write';
const authorizeURL = new URL('https://api.twitter.com/oauth/authorize');
const accessTokenURL = 'https://api.twitter.com/oauth/access_token';
const oauth = new OAuth({
  consumer: {
    key: consumer_key,
    secret: consumer_secret
  },
  signature_method: 'HMAC-SHA1',
  hash_function: (baseString, key) => crypto.createHmac('sha1', key).update(baseString).digest('base64')
});

let updateTimerId: NodeJS.Timeout | null = null;

export function twitterBot() {
  updateWatcher();

  return () => {
    if (!updateTimerId) {
      return;
    }

    clearTimeout(updateTimerId);
  }
}

async function input(prompt: string) {
  return new Promise<string>(async (resolve, reject) => {
    terminal.question(prompt, (out) => {
      terminal.close();
      resolve(out);
    });
  });
}

async function updateWatcher() {
  const headers = {
    headers: {
      "User-Agent": "v2SpacesSearchJS",
      "authorization": `Bearer ${token}`
    }
  };
  const params = {
    query: 'from:navalnylive'
  };

  createTweet();

  // updateTimerId = setTimeout(updateWatcher, 60000);
}

async function createTweet() {
  const oAuthRequestToken = await requestToken();
  console.log(oAuthRequestToken);
  authorizeURL.searchParams.append('oauth_token', oAuthRequestToken.oauth_token);
  console.log('Please go here and authorize:', authorizeURL.href);
  const pin = await input('Paste the PIN here: ');
  const oAuthAccessToken = await accessToken(oAuthRequestToken, pin.trim());
  const response = await getRequest(oAuthAccessToken);
  console.dir(response, {
    depth: null
  });

  authorizeURL.searchParams.append('oauth_token', oAuthRequestToken.oauth_token);
}

async function requestToken() {
  const authHeader = oauth.toHeader(oauth.authorize({
    url: requestTokenURL,
    method: 'POST'
  }));
  console.log(authHeader["Authorization"]);

  const req = await needle('post', requestTokenURL, {}, {
    headers: {
      Authorization: authHeader["Authorization"]
    }
  });
  if (req.body) {
    console.log(req.body);
    return req.body.split('&').reduce((result: {[name: string]: string}, item: string) => {
      const [key, value] = item.split('=');
      result[key] = value;

      return result;
    }, {});
  } else {
    throw new Error('Cannot get an OAuth request token');
  }
}

async function getRequest({
                            oauth_token,
                            oauth_token_secret
                          }: {
  oauth_token: string;
  oauth_token_secret: string;
}) {

  const token = {
    key: oauth_token,
    secret: oauth_token_secret
  };

  const authHeader = oauth.toHeader(oauth.authorize({
    url: endpointUrl + 'tweets',
    method: 'POST'
  }, token));

  const req = await needle('post', endpointUrl + 'tweets', {
    text: 'test'
  }, {
    headers: {
      Authorization: authHeader["Authorization"],
      'user-agent': "v2CreateTweetJS",
      'content-type': "application/json",
      'accept': "application/json"
    }
  });
  if (req.body) {
    return req.body;
  } else {
    throw new Error('Unsuccessful request');
  }
}

async function accessToken({
                             oauth_token,
                             oauth_token_secret
                           }: {oauth_token: string;
  oauth_token_secret: string;}, verifier: string) {
  const authHeader = oauth.toHeader(oauth.authorize({
    url: accessTokenURL,
    method: 'POST'
  }));
  const path = `https://api.twitter.com/oauth/access_token?oauth_verifier=${verifier}&oauth_token=${oauth_token}`
  const req = await needle('post', path, {}, {
    headers: {
      Authorization: authHeader["Authorization"]
    }
  });
  if (req.body) {
    return req.body;
  } else {
    throw new Error('Cannot get an OAuth request token');
  }
}
