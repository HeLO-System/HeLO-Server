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
    Content: Faulty Request<br/>
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
  * Code: `401 UNAUTHORIZED`
    Content: Wrong Token or no Admin
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
