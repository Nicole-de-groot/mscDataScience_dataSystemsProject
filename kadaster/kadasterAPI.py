import json
import pandas as pd
import requests
import os

prefix = "../"
filename = "VA_addresses.csv"

#open vestigingadressen dataframe
addresses = pd.read_csv(prefix+filename)

#kadaster_id dataframe - als deze al bestaat wordt deze geopend
columns = ["huisnummer","postcode","nrAanduiding","vblObject","inOnderzoek"]
if os.path.isfile("kadaster_ids.csv"):
    kadaster_ids = pd.read_csv("kadaster_ids.csv",dtype=object)
else:
    kadaster_ids = pd.DataFrame(columns=columns)

#BAG Kadaster API
def getResponse(PC, HUISNR):
    url = "https://bag.basisregistraties.overheid.nl/api/v1/nummeraanduidingen?postcode={}&huisnummer={}".format(PC,HUISNR)

    payload = {}
    headers = {
      'x-api-key': '593f1c08-4eac-4f5b-8a35-59d64883e2b2'
    }

    response = requests.request("GET", url, headers=headers, data = payload)
    return response

#extract informatie
def getInfo(json_response):
    huisnummer = json_response["_embedded"]["nummeraanduidingen"][0]["huisnummer"]
    postcode = json_response["_embedded"]["nummeraanduidingen"][0]["postcode"]
    nrAanduiding = json_response["_embedded"]["nummeraanduidingen"][0]["identificatiecode"]
    vblObject = json_response["_embedded"]["nummeraanduidingen"][0]["_links"]["adresseerbaarObject"]["href"].rpartition("/")[-1]
    inOnderzoek = json_response["_embedded"]["nummeraanduidingen"][0]["_embedded"]["geldigVoorkomen"]["inOnderzoek"]
    
    df = pd.DataFrame(data = [[huisnummer,postcode,nrAanduiding,vblObject,inOnderzoek]],columns=columns)
    return df

#loop over (vestigings)adressen
for index, row in addresses.iterrows():
    HUISNR = row["HUISNR"]
    PC = row["PC"]
    if not kadaster_ids.where((kadaster_ids["huisnummer"]==HUISNR) & (kadaster_ids["postcode"] == PC)).dropna().empty:
        response = getResponse(PC, HUISNR)
        json_response = json.loads(response.text)
        try: 
            kadaster_ids = kadaster_ids.append(getInfo(json_response))
        #except wanneer de adressen niet te vinden zijn
        except (IndexError,KeyError):
            continue

#sla kadaster_ids op voor vervolg script
kadaster_ids.to_csv("kadaster_ids.csv", index=None)
