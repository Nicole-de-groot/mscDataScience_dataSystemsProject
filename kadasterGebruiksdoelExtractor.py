import pandas as pd
from xml.dom import minidom
import pickle
import os
import glob
import sys

kadaster_vbObject = "kadaster_vbObject"
columns = ["vblObject","gebruiksdoel","oppervlakte","vbloStatus"]
if os.path.isfile(kadaster_vbObject + ".csv"):
    kadaster = pd.read_csv(kadaster_vbObject + ".csv")
else: kadaster = pd.DataFrame(columns=columns)

checkedVBO = "checkedVBOfiles"
if os.path.isfile(checkedVBO + ".p"):
    with open(checkedVBO + ".p", 'rb') as fp:
        checkedVBOfiles = pickle.load(fp)
else: checkedVBOfiles = []
    
kadaster_ids = pd.read_csv("kadaster_ids.csv", dtype = object)
nr_ids = len(kadaster_ids)

start_len = len(kadaster)

prefix = "kadaster/9999VBO08112019/"
cut = len(prefix)

files = glob.glob(prefix+"*xml")

def checkfile(currentfile):
    mydoc = minidom.parse(currentfile)
    items = mydoc.getElementsByTagName("bag_LVC:Verblijfsobject")
    vbCurrentFile = pd.DataFrame(columns = columns)
    for item in items:
        for child in item.childNodes:
            if child.nodeName[8:] == 'identificatie':
                id = child.firstChild.nodeValue
            elif child.nodeName[8:] == 'gebruiksdoelVerblijfsobject':
                gebruiksdoel = child.firstChild.nodeValue
            elif child.nodeName[8:] == 'oppervlakteVerblijfsobject':
                oppervlakte = child.firstChild.nodeValue
            elif child.nodeName[8:] == 'verblijfsobjectStatus':
                status = child.firstChild.nodeValue[16:]
        if kadaster_ids.where((kadaster_ids["vblObject"] == id)).dropna().empty == False:
            vbObject = pd.DataFrame(data = [[id,gebruiksdoel,oppervlakte,status]], columns=columns)
            vbCurrentFile = vbCurrentFile.append(vbObject)
    return vbCurrentFile

for currentfile in files:
    print(currentfile[cut:])
    if currentfile not in checkedVBOfiles:
        vbObject = checkfile(currentfile)
        if not vbObject.empty:
            kadaster = kadaster.append(vbObject)
    else: print("already checked")
    if len(kadaster) > start_len:
        print("found",len(kadaster)-start_len,"new ids -",len(kadaster),"of",nr_ids,"found")
        kadaster.to_csv(kadaster_vbObject + ".csv", index = None)
        start_len = len(kadaster)
    else: print("no new items found")
    
    checkedVBOfiles.append(currentfile)
    with open(checkedVBO + '.p', 'wb') as fp:
        pickle.dump(checkedVBOfiles, fp)

    if len(kadaster) == nr_ids:
        sys.exit()
