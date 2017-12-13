import requests
import json
import itertools
import math
import tqdm
import pymongo
from access_token import *

with pymongo.MongoClient("localhost", 27017) as client:
    db = client.get_database("github")
    users = db.get_collection("users")
    people = list(users.find({}, ["login", "followers_url", "following_url"]))

    params = {
        "access_token": access_token
    }

    for person in tqdm.tqdm(people):
        followers = requests.get(person["followers_url"], params=params).json()
        following = requests.get(person["following_url"].rstrip("{/other_user}"), params=params).json()
        connections = followers + following
        connection_logins = set([each["login"] for each in connections])
        users.update_one({"login": person["login"]}, {"$set": {"connections": list(connection_logins)}})
        for connection in connections:
            try:
                users.insert_one(connection)
            except pymongo.errors.DuplicateKeyError:
                pass