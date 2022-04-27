# HeLO API - Documentation
The API documentation can be found [here](https://app.swaggerhub.com/apis-docs/HeLO-System/HeLO-API/0.1#/).

</br>

# Coding Examples - Python

## Simple `GET` request

send a simple `GET` request:
```
>>> import requests
>>> r = requests.get("http://api.helo-system.de/clan/626481305970d05c050877c2")
```
</br>

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
<br/>

## Simple `POST` request

