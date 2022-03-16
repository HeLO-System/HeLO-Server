# HeLO API
Work in progress ...

# Routes Overview
* /auth/signup
* /auth/login
* /user/{userid}
* /users
* /clan/{id}
* /clans
* /match/{id}
* /matches
* /event/{id}
* /events
* /score/{id}
* /scores
* /simulations

<br/>

# Clan Objects
## Get Clan
Fetch a clan object by its id.
* **URL:** /clan/{id}
* **Method:** `GET`
* **JWT Required:** No
* **Admin Required:** No
* **Success Response:** <br/>
  * Code: `200` <br/>
    Content: corresponding clan object
* **Error Response:** <br/>
  * Code: `404 NOT FOUND` <br/>
    Content: "not a valid object id" <br/>
    Meaning: the given {id} is not valid, maybe there is something missing
  * Code: `404 NOT FOUND` <br/>
    Content: "does not exist" <br/>
    Meaning: the given {id} does not exist
* **Example:** <br/>
  * Request: <br/>
    `GET .../clan/62308f7d43a886c4ef1935a1`
  * Response:
    ```
    200 OK
    {
        "_id": {
            "$oid": "62308f7d43a886c4ef1935a1"
        },
        "tag": "CoRe",
        "name": "Corvus Rex",
        "score": 798,
        "num_matches": 2
    }
    ```
<br/>

## Update a Clan
Update a clan object in the database.
* **URL:** /clan/{id}
* **Method:** `PUT`
* **JWT Required:** Yes
* **Admin Required:** No
* **Success Response:** <br/>
  * Code: `204` <br/>
    Content: empty
* **Error Response:** <br/>
  * Code: `400 BAD REQUEST` <br/>
    Content: "Faulty Request"<br/>
    Meaning: your JSON object contains errors
  * Code: `401 UNAUTHORIZED`<br/>
    Content: "Wrong Token or no Admin"<br/>
    Meaning: your JWT is not correct
  * Code: `404 NOT FOUND` <br/>
    Content: "not a valid object id" <br/>
    Meaning: the given {id} is not valid, maybe there is something missing
  * Code: `404 NOT FOUND` <br/>
    Content: "does not exist" <br/>
    Meaning: the given {id} does not exist
* **Example:** <br/>
  * Request: <br/>
    `PUT .../clan/62308f7d43a886c4ef1935a1`<br/>
    header:
    ```
    Token = yJ0eX...
    ```
    body:
    ```
    {
        "score": 1022
    }
    ```
  * Response:
    ```
    204 NO CONTENT

    ```
<br/>

## Delete a Clan
Delete a clan object from the database.
* **URL:** /clan/{id}
* **Method:** `DELETE`
* **JWT Required:** Yes
* **Admin Required:** Yes
* **Success Response:** <br/>
  * Code: `204` <br/>
    Content: empty
* **Error Response:** <br/>
  * Code: `401 UNAUTHORIZED`<br/>
    Content: "Wrong Token or no Admin"<br/>
    Meaning: your JWT is not correct
  * Code: `404 NOT FOUND` <br/>
    Content: "not a valid object id" <br/>
    Meaning: the given {id} is not valid, maybe there is something missing
  * Code: `404 NOT FOUND` <br/>
    Content: "does not exist" <br/>
    Meaning: the given {id} does not exist
* **Example:** <br/>
  * Request: <br/>
    `DELETE .../clan/62308f7d43a886c4ef1935a1`<br/>
    header:
    ```
    Token = yJ0eX...
    ```
  * Response:
    ```
    204 NO CONTENT

    ```
<br/>

## Create a Clan
Create a new clan object.
* **URL:** /clans
* **Method:** `POST`
* **JWT Required:** Yes
* **Admin Required:** Yes
* **Example:** <br/>
  * Request: <br/>
    `POST .../clans`<br/>
    header:
    ```
    Token = yJ0eX...
    ```
    body:
    ```
    {
        "tag": "CoRe",
        "name": "Corvus Rex",
        "invite": "https://discord.gg/M4DtuGcq8m",
        "score": 700,
        "num_matches": 22
    }
    ```
  * Response:
    ```
    200 OK
    "id: 6231be6d09e11eef9fbf8537"
    ```
* **Note:** Only "tag" is a required field. "score" and "num_matches" will be set automatically to their default values when they have not been sent. The response contains the unique id of the clan in the database.

<br/>


# Match Objects
## Get Match
Fetch a match object from the database.
* **URL:** /match/{id}
* **Method:** `GET`
* **JWT Required:** No
* **Admin Required:** No
* **Example:** <br/>
  * Request: <br/>
    `GET .../match/`<br/>
  * Response:
    ```
    200 OK
    "id: 6231be6d09e11eef9fbf8537"
    ```
* **Note:** Only "tag" is a required field. "score" and "num_matches" will be set automatically to their default values when they have not been sent. The response contains the unique id of the clan in the database.

<br/>

## Create a Match
Create a new match object in the database.
Create a new clan object.
* **URL:** /matches
* **Method:** `POST`
* **JWT Required:** Yes
* **Admin Required:** No
* **Example:** <br/>
  * Request: <br/>
    `POST .../matches`<br/>
    header:
    ```
    Token = yJ0eX...
    ```
    body:
    ```
    {
      "match_id": "StDb+Phx-CoRe-15-03-2022",
      "clans1_ids": ["62308f9743a886c4ef1935a3", "62308f7d43a886c4ef1935a1"],
      "clans2_ids": ["62308f8a43a886c4ef1935a2"],
      "player_dist1": {
          "StDb": 35,
          "Phx": 15
      },
      "player_dist2": {
          "CoRe": 50
      },
      "players": 50,
      "factor": 1.0,
      "caps1": 1,
      "caps2": 4
    }
    ```
  * Response:
    ```
    200 OK
    {
      "match_id": "StDb+Phx-CoRe-15-03-2022",
      "confirmed": false
    }
    ```
* **Note:** 

<br/>
