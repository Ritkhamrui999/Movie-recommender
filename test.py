import requests
r = requests.get("http://www.omdbapi.com/?t=Inception&apikey=YOUR_KEY")
print(r.json())
