# HeLO API
Work in progress ...

# Get Clan
Fetch a clan object by its id.
* **URL:** /clan/{id}
* **Method:** `Get`
* **JWT Required:** No
* **Success Response:** <br/>
  * Code: `200` <br/>
    Content: corresponding clan object
* **Error Response:** <br/>
  * Code: `404 NOT FOUND` <br/>
    Content: "not a valid object id" <br/>
    Meaning: the given {id} does not exist
* **Example:** <br/>
  * `GET .../clan/62308f7d43a886c4ef1935a1`
  * `{
    "_id": {
        "$oid": "62308f7d43a886c4ef1935a1"
    },
    "tag": "CoRe",
    "name": "Corvus Rex",
    "score": 798,
    "num_matches": 2
}`

