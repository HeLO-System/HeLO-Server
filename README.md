# HeLO API - Documentation

The API documentation can be found [here](https://app.swaggerhub.com/apis-docs/HeLO-System/HeLO-API/0.1#/).

# Configuration parameters

This is a non-conclusive overview of environment variables and their use cases, which may need to be set for HeLO-Server to run:

* `DB_USERNAME`, `DB_PASSWORD`, `DB_HOST`: The usual database specific connection details and credentials (for the mongo db cluster)
* `DB_NAME_PC`, `DB_NAME_CONSOLE`: The database/collection names for the mongo db collections to use for data saved for PC game and console game
* `JWT_SECRET_KEY`: The secret string used to issue JWTs
* `SECRET_KEY`: Same as `JWT_SECRET_KEY`, however, might be used for other signing in the future (is also used for discord auth)
* `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`: Client ID and secret from the Discord app used for OAuth2 login (get these from the Discord developer portal)
* `DISCORD_REDIRECT_URI`: The absolute redirect URL used for the Discord OAuth2 authentication flow. Needs to be the publicly reachable URL of the HeLO-Server app
* `DISCORD_AUTH_REDIRECT_URI`: (Temporary?) The redirect URL of the application that requests user authentication. Usually this is the HeLO-Frontend app for now
* `DISCORD_AUTH_GUILD_ID`: The Guild ID from which authorization data is used (roles). This is usually the HeLO discord Guild (get it from the Discord client; right click -> Copy ID)
* `DISCORD_AUTH_ADMIN_ROLE`: The Discord Role ID of a role with in the `DISCORD_AUTH_GUILD_ID` guild, which makes a logged-in user an admin in the HeLO-System
* `DISCORD_AUTH_TEAM_MANAGER_ROLE`: The Discord Role ID of a role with in the `DISCORD_AUTH_GUILD_ID` guild, which makes a logged-in user a team manager in the HeLO-System
* `DISCORD_REPORT_MATCH_WEBHOOK`: A Discord Webhook URL to report new matches into

# Local setup

To start HeLO-Server locally, you need to start a local mongodb instance (or use any other hosted mongo db you've around). E.g. start one using docker:

```shell
cd local/
docker-compose up -d
```

This starts up a local mongo db and sets up a new helo-user.
Then, set the environment variables from above accordingly, while the database username and password are:
* Username: `helo`
* Password: `my_other_secure_password`

# Coding Examples - Python

## Simple `GET` request

send a simple `GET` request:
```
>>> import requests
>>> r = requests.get("http://api.helo-system.de/clan/626481305970d05c050877c2")
```

unpack status code and payload:
```
>>> r
<Response [200]>
>>> r.json()
{
    "_id":
      {
        "$oid": "626481305970d05c050877c2"
      },
    "tag": "CoRe",
    "name": "Corvus Rex",
    "invite": "https://discord.gg/hllcore",
    "score": 917,
    "num_matches": 55,
    "alt_tags": [],
    "icon": "https://media.discordapp.net/attachments/955418562284109864/955419459923886130/alte_maus_sensi.PNG?width=575&height=640",
    "last_updated":
      {
        "$date": 1650834405012
      }
}
```

## Simple `POST` request

