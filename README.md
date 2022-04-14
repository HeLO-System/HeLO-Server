# HeLO API
there is still work in progress ...

documentation:
https://app.swaggerhub.com/apis-docs/HeLO-System/HeLO-API/0.1#/

- [HeLO API](#helo-api)
- [Routes Overview](#routes-overview)
- [Clan Objects](#clan-objects)
  - [Get Clan](#get-clan)
  - [Update Clan](#update-clan)
  - [Delete Clan](#delete-clan)
  - [Create Clan](#create-clan)
- [Match Objects](#match-objects)
  - [Create Match](#create-match)
  - [Get Match](#get-match)
  - [Update Match](#update-match)
  - [Delete Match](#delete-match)
- [Signup and Login](#signup-and-login)
  - [Signup](#signup)
  - [Login](#login)
- [User Objects](#user-objects)
  - [Get User](#get-user)
  - [Change User](#change-user)
  - [Delete User](#delete-user)
- [Models Overview](#models-overview)
  - [Clan](#clan)
  - [Event](#event)
  - [Match](#match)
  - [User](#user)
  - [Score](#score)
- [Coding Examples - Python](#coding-examples---python)
  - [Simple `GET` request](#simple-get-request)
  - [Simple `POST` request](#simple-post-request)

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
* **Endpoint:** */clan/{id}*
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

## Update Clan
Update a clan object in the database.
* **Endpoint:** */clan/{id}*
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

## Delete Clan
Delete a clan object from the database.
* **Endpoint:** */clan/{id}*
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

## Create Clan
Create a new clan object.
* **Endpoint:** */clans*
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
## Create Match
Create a new match object in the database.
* **Endpoint:** */matches*
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
* **Note:** Only the "match_id" is a required field and it is unique. However, everything else is required later to calculate the scores out of this match. A game has to be confirmed from both sides. More on that later (see "Update Matches").
* **Further Explanation:**

  | Field           | Explanation                             |
  | :-------------: |:---------------------------------------:|
  | `clans_ids`     | `list` of unique ids                    |
  | `player_dist`   | mapping of clan tag to players (opt.)   |
  | `players`       | number of players fielded               |
  | `factor`        | competitive factor                      |
  | `caps`          | captured strongpoints                   |


<br/>

## Get Match
Fetch a match object from the database.
* **Endpoint:** */match/{id}*
* **Method:** `GET`
* **JWT Required:** No
* **Admin Required:** No
* **Example:** <br/>
  * Request: <br/>
    `GET .../match/6231b2b0caa748197199bd48`<br/>
  * Response:
    ```
    200 OK
    {
      "_id": {
          "$oid": "6231b2b0caa748197199bd48"
      },
      "match_id": "StDb+Phx-CoRe-15-03-2022",
      "clans1_ids": [
          "62308f9743a886c4ef1935a3",
          "62308f7d43a886c4ef1935a1"
      ],
      "clans2_ids": [
          "62308f8a43a886c4ef1935a2"
      ],
      "player_dist1": {
          "StDb": 35,
          "Phx": 15
      },
      "player_dist2": {
          "CoRe": 50
      },
      "caps1": 1,
      "caps2": 4,
      "players": 50,
      "factor": 1.0
    }
    ```
<br/>

## Update Match
Update a match object in the database.
* **Endpoint:** */match/{id}*
* **Method:** `PUT`
* **JWT Required:** Yes
* **Admin Required:** No
* **Example:** <br/>
  * Request: <br/>
    `PUT .../match/6231b2b0caa748197199bd48`<br/>
    header:
    ```
    Token = yJ0eX...
    ```
    body:
    ```
    {
      "conf1": "307305122940659340"
    }
    ```
  * Response:
    ```
    204 NO CONTENT
    
    ```
* **Note:** In order to trigger the score calculations for a match, both sides need to confirm the match. This should be performed using `PUT` as shown in the example above. The fields `conf1` (and `conf2` respectively) contain the Discord User ID of the one who confirmed the match. Of course, other things can be updated via `PUT` as well.

<br/>

## Delete Match
Delete a match object from the database.
* **Endpoint:** */match/{id}*
* **Method:** `DELETE`
* **JWT Required:** Yes
* **Admin Required:** No
* **Example:** <br/>
  * Request: <br/>
    `DELETE .../match/6231b2b0caa748197199bd48`<br/>
    header:
    ```
    Token = yJ0eX...
    ```
  * Response:
    ```
    204 NO CONTENT
    
    ```

<br/>

# Signup and Login
## Signup
Create a new user.
* **Endpoint:** */auth/signup*
* **Method:** `POST`
* **JWT Required:** Yes
* **Admin Required:** Yes
* **Example:** <br/>
  * Request: <br/>
    `POST .../auth/signup`<br/>
    header:
    ```
    Token = yJ0eX...
    ```
    body:
    ```
    {
      "userid": "307305122940659340",
      "pin": "12345",
      "name": "MasterMind3000",
      "role": "teamrep"
    }
    ```
  * Response:
    ```
    200 OK
    {
      "id": "307305122940659340"
    }
    ```
* **Note:** Only "userid" and "role" are required fields.

<br/>

## Login
Login with existing user id and pin in order to receive an active token (JWT). The JWT expires after seven days.
* **Endpoint:** */auth/login*
* **Method:** `POST`
* **JWT Required:** No
* **Admin Required:** No
* **Example:** <br/>
  * Request: <br/>
    `POST .../auth/login`<br/>
    body:
    ```
    {
      "userid": "307305122940659340",
      "pin": "12345"
    }
    ```
  * Response:
    ```
    200 OK
    {
      "token": "yJ0eX..."
    }
    ```
    

<br/>

# User Objects
## Get User
Fetch user object from database by discord id.
* **Endpoint:** */user/{id}*
* **Method:** `GET`
* **JWT Required:** No
* **Admin Required:** No
* **Example:** <br/>
  * Request: <br/>
    `GET .../user/307305122940659340`<br/>
  * Response:
    ```
    200 OK
    {
      "_id": {
          "$oid": "6231c401ae4121068fa98057"
      },
      "userid": "307305122940659340",
      "pin": "$2b$12$nqOao4.1j4sT9pLoyibo8u1evrNKyDCHdHcEtF7f7AJSj6pOgkCQq",
      "name": "MasterMind3000",
      "role": "teamrep"
    }
    ```
* **Note:** The pin is hashed and not human-readable. This is also the case for admins having direct database access.

<br/>

## Change User
Change user object in the database.
* **Endpoint:** */user/{id}*
* **Method:** `PUT`
* **JWT Required:** Yes
* **Admin Required:** No
* **Example:** <br/>
  * Request: <br/>
    `PUT .../user/307305122940659340`<br/>
    header:
    ```
    Token = yJ0eX...
    ```
    body:
    ```
    {
      "name": "NotSoMasterMind1000"
    }
  * Response:
    ```
    204 NO CONTENT
    
    ```
* **Note:** Even though updating a user requires no admin permissions, it is not possible to change the role of a user.

<br/>

## Delete User
Delete a user object from the database.
* **Endpoint:** */user/{id}*
* **Method:** `DELETE`
* **JWT Required:** Yes
* **Admin Required:** Yes
* **Example:** <br/>
  * Request: <br/>
    `DELETE .../user/307305122940659340`<br/>
    header:
    ```
    Token = yJ0eX...
    ```
  * Response:
    ```
    204 NO CONTENT
    
    ```

# Models Overview
All attributes and possible settings for the different objects. `*` means the field is required and `**` means the field is required and unique.

## Clan
  | Field           | Explanation                                     | Type        |
  | :-------------: |:-----------------------------------------------:|:-----------:|
  | `tag**`         | official clan tag, e.g. CoRe                    | StringField |
  | `name`          | full name of the clan, e.g. Corvus Rex          | StringField |
  | `flag`          | discord icon ID of flag of origin, e.g. flag_eu | StringField |
  | `invite`        | discord invite link                             | StringField |
  | `score`         | current HeLO Score                              | IntField    |
  | `num_matches`   | number of played matches                        | IntField    |
  | `conf`          | *not in use, reserved*                          | StringField |
  | `alt_tags`      | alternative tags, in case of renaming           | ListField   |
<br/>

## Event
  | Field           | Explanation                                     | Type        |
  | :-------------: |:-----------------------------------------------:|:-----------:|
  | `tag**`         | acronym of the event, e.g. HPL                  | StringField |
  | `name`          | corresponding name, e.g. HLL Premier League     | StringField |
  | `emoji`         | event emoji discord id, e.g. hpl                | StringField |
  | `factor`        | tournament's comp. factor for score calculations| FloatField  |
  | `invite`        | discord invite link to the event server         | StringField |
  | `conf`          | *not in use, reserved*                          | StringField |
<br/>

## Match
  | Field           | Explanation                                     | Type        |
  | :-------------: |:-----------------------------------------------:|:-----------:|
  | `match_id**`    | unique identifier, e.g. "StDb-91.-2022-01-01"   | StringField |
  | `clans1_ids`    | list of clan ids, side1                         | ListField   |
  | `clans2_ids`    | list of clan ids, side2                         | ListField   |
  | `player_dist1`  | player distributions, tag mapped to int         | DictField   |
  | `player_dist2`  | player distributions, tag mapped to int         | DictField   |
  | `side1`         | which fraction, allies or axis, side1           | StringField |
  | `side2`         | which fraction, allies or axis, side2           | StringField |
  | `caps1`         | number of strongpoints, side1                   | IntField    |
  | `caps2`         | number of strongpoints, side2                   | IntField    |
  | `players`       | number of players on each side                  | IntField    |
  | `map`           | the map the match where played on               | StringField |
  | `date`          | datetime of the match                           | DateField   |
  | `duration`      | duration of the match in min                    | IntField    |
  | `factor`        | competitive factor of the match                 | FloatField  |
  | `event`         | event the match belongs to                      | StringField |
  | `conf1`         | user id who confirmed the match for side 1      | StringField |
  | `conf2`         | user id who confirmed the match for side 2      | StringField |
<br/>

## User
  | Field           | Explanation                                     | Type        |
  | :-------------: |:-----------------------------------------------:|:-----------:|
  | `userid**`      | discord user id                                 | StringField |
  | `pin`           | pin to log in                                   | StringField |
  | `name`          | discord name, e.g. Soxxes                       | StringField |
  | `role*`         | admin or teamrep                                | StringField |
  | `clan`          | clan/team the user belongs to, e.g. CoRe        | StringField |
  | `conf`          | *not in use, reserved*                          | StringField |
<br/>

## Score
  | Field           | Explanation                                     | Type        |
  | :-------------: |:-----------------------------------------------:|:-----------:|
  | `clan*`         | clan the score belongs to                       | StringField |
  | `num_matches*`  | number of matches, serves as a counter          | IntField    |
  | `match_id*`     | match the score is based on                     | StringField |
  | `score*`        | score of the clan                               | IntField    |
<br/>

# Coding Examples - Python
## Simple `GET` request
import the `requests` module and send a basic `GET` request:
(final URL will be announced)
```
>>> import requests
>>> r = requests.get("http://.../clan/62308f8a43a886c4ef1935a2")
```
unpack status code and payload
```
>>> r
<Response [200]>
>>> r.json()
{'_id': {'$oid': '62308f8a43a886c4ef1935a2'}, 'tag': 'CoRe', 'name': 'Corvus Rex', 'score': 619, 'num_matches': 2, 'alt_tags': []}
```
<br/>

## Simple `POST` request

