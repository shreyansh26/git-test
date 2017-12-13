import requests
import json
import itertools
import math
import tqdm
import pymongo
from access_token import *
from bson import ObjectId

def search(q):
	url = "https://api.github.com/search/users"
	params = {
		"q": str(q),
		"page": 1,
		"per_page": 30,
		"access_token": access_token
	}
	first = requests.get(url, params=params)
	body = first.json()
	if first.status_code != 200:
		raise Error("error: " + body.get("message", ""))

	for item in body["items"]:
		yield item
	total = body["total_count"]
	per_page = params["per_page"]
	n_pages = int(math.ceil(total/per_page))

	for page in range(2, n_pages+1):
		params["page"] = page
		response = requests.get(url, params=params)
		body = response.json()
		if response.status_code != 200:
			raise Error("error: " + body.get("message", ""))
		for item in body["items"]:
			yield item

query_strings = ["location:IIT BHU", "location:Varanasi", "location:IIT (BHU)", "location:IIT Varanasi"]

with pymongo.MongoClient("localhost", 27017) as client:
	db = client.get_database("github")
	users = db.get_collection("users")
	users.create_index(keys=[("login", pymongo.ASCENDING)], unique=True)

	for q in query_strings:
		for item in tqdm.tqdm(search(q)):
			try:
				users.insert_one(item)
				#print(json.dumps(item))
			except pymongo.errors.DuplicateKeyError:
				pass

	print(users.count())

res_json = []

for q in query_strings:
	for i in search(q):
		res_json.append(json.dumps(i))

res_json = list(set(res_json))

with open("results.json", "w") as f:
	f.write('[')
	for i in range(len(res_json)-1):
		f.write(str(res_json[i]))
		f.write(',')
	f.write(str(res_json[i]))
	f.write(']')

