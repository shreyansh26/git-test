import requests
import json
import itertools
import math
import tqdm
import pymongo
from access_token import access_token

with pymongo.MongoClient("localhost", 27017) as client:
	db = client.get_database("github")
	users = db.get_collection("users")
	people = list(users.find({}, ["login", "repos_url"]))

	params = {
		"access_token": access_token
	}

	for person in tqdm.tqdm(people):
		repos = requests.get(person["repos_url"], params=params).json()
		users.update_one({"login": person["login"]}, {"$set": {"repos": list(repos)}})