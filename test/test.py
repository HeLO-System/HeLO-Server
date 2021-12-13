# test/test.py
import requests, json

host = "http://127.0.0.1:5000"
#host = "https://mongorest-sandbox.herokuapp.com"
headers = { "Content-Type": "application/json", "Authorization": None } # MUST be provided for POST and PUT requests


def login(userid, pin):
    print("-----------------------------------------")
    print(f"LOGIN {userid}")
    body = json.dumps({ "userid": userid, "pin": pin })
    result = requests.post(f"{host}/auth/login", body, headers=headers)    
    headers["Authorization"] = f"Bearer {json.loads(result.content)['token']}"
    print(f'{headers["Authorization"][:50]}...')
    print("-----------------------------------------")

def print_clans():
    print("-----------------------------------------")
    clans = json.loads(requests.get(f"{host}/clans").content)
    for clan in clans: print(f'{clan["tag"]} \t{clan["name"]}')
    print("-----------------------------------------")


def create(body):
    print(f"POST {body}")    
    return requests.post(f"{host}/clans", body, headers=headers)

def create_process_result(error = None, message = None, _auto_id_0 = None):
    if error != None: print(f"ERROR: {error}")
    if message != None: print(f"Message: {message}")
    if _auto_id_0 != None: print(_auto_id_0["$oid"])
    

def update(tag, body):
    response = requests.get(f"{host}/clans?tag={tag}")    
    clans = json.loads(response.content)
    id = clans['_id']["$oid"]
    print(f"PUT {id} {body}")
    requests.put(f"{host}/clan/{id}", body, headers=headers)


def delete(tag):
    print(f"DELETE {tag}")
    clans = json.loads(requests.get(f"{host}/clans?tag={tag}").content)
    id = clans['_id']["$oid"]
    requests.delete(f"{host}/clan/{id}", headers=headers)
    

# GET can be called without authorization
print_clans() 

# LOGIN
login("407302122921656340", "0")

# POST
result = create(json.dumps({"tag": "Phx", "name": "Phoenix"}))   
create_process_result(**json.loads(result.content))
print_clans()

# PUT
update("Phx", json.dumps({"tag": "Phx", "name": "Team Phoenix"}))
print_clans()

# DELETE
delete("Phx")
print_clans()
