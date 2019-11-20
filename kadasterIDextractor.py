#!/usr/bin/env python
import pandas as pd
from xml.dom import minidom
import pickle
import os
import glob
import sys

VA_adresses = "VA_addresses_dict"
if os.path.isfile(VA_adresses + ".p"):
    with open(VA_adresses + '.p', 'rb') as fp:
        VA_addresses_dict = pickle.load(fp)
else: VA_addresses_dict = {}

checkedNUM = "checkedNUMfiles"
if os.path.isfile(checkedNUM + ".p"):
    with open(checkedNUM + ".p", 'rb') as fp:
        checkedNUMfiles = pickle.load(fp)
else: checkedNUMfiles = []


files = glob.glob("*xml")

#i = iter(files)

#currentfile = next(i)
#while currentfile in checkedNUMfiles:
#    print(currentfile,"\talready checked")
#    currentfile = next(i)
#print(currentfile)

for currentfile in files:
    if currentfile in checkedNUMfiles:
        print(currentfile + "\t already checked")
    else:
        print(currentfile)
        mydoc = minidom.parse(currentfile)

        items = mydoc.getElementsByTagName('bag_LVC:Nummeraanduiding')
        #print(items[0].firstChild.nodeName,":\t",items[0].firstChild.firstChild.nodeValue)

        ## Get ID's
        VA = pd.read_csv("VA_addresses.csv", index_col=0)
        #VA.iloc[0][1]len(items)

        for item in items:
            for child in item.childNodes:
#                print(child.nodeName[8:], child.firstChild.nodeValue)
                if child.nodeName[8:] == 'identificatie':
                    id = child.firstChild.nodeValue
                elif child.nodeName[8:] == 'huisnummer':
                    huisnr = child.firstChild.nodeValue
                elif child.nodeName[8:] == 'postcode':
                    pc = child.firstChild.nodeValue
            if VA.where((VA["PC"] == pc)&(VA["HUISNR"] == int(huisnr))).dropna().empty == False:
#                print(id,huisnr,pc)
                VA_addresses_dict[id]=[huisnr,pc]

    if bool(VA_addresses_dict):
        with open(VA_adresses + '.p', 'wb') as fp:
            pickle.dump(VA_addresses_dict, fp)

    checkedNUMfiles.append(currentfile)
    with open(checkedNUM + '.p', 'wb') as fp:
            pickle.dump(checkedNUMfiles, fp)
