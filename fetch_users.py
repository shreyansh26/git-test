import requests
import tqdm
import json
from access_token import *

def get_urls(filename):
	with open(filename) as f:
		data = json.load(f)
		return [each["url"] for each in data]

urls = get_urls("results.json")
print(len(urls))

params = {
		"access_token": access_token
	}

profiles = [requests.get(url, params=params).json() for url in tqdm.tqdm(urls)]

with open("users.json", "w") as f:
	json.dump(profiles, f)