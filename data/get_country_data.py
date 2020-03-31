
import json
import os
import urllib.request
import hashlib
import sys


with open("../public_html/data.json", "rt") as f:
    jdata = json.loads(f.read())



popsizes = dict()

for key in jdata["keys_by_name"]:

    country = key[0]
    country = country.replace("/", " ").strip()

    if country in ["Canada Diamond Princess", "Canada Grand Princess", "Canada Recovered", "Diamond Princess", "MS Zaandam"]:
        popsizes[key[0]] = None
        continue

    if country == "United Kingdom Turks and Caicos Islands":
        popsizes[key[0]] = 31458
        continue
    if country == "China Shandong":
        popsizes[key[0]] = 100470000
        continue
    if country == "United Kingdom British Virgin Islands":
        popsizes[key[0]] = 35802
        continue
    if country == "United Kingdom Channel Islands":
        popsizes[key[0]] = 170499
        continue
    if country == "Canada Yukon":
        popsizes[key[0]] = 35874
        continue
    if country == "Denmark Faroe Islands":
        popsizes[key[0]] = 49290
        continue

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    url = "https://www.google.com/search?client=ubuntu&channel=fs&q=population+size+" + country + "&ie=utf-8&oe=utf-8"
    url = url.replace(" ", "+")
    url = url.replace("ü", "%C3%BC")
    url = url.replace("ä", "%C3%A4")

    save_filename = "google_cache/" + hashlib.md5(url.encode("utf-8")).hexdigest()

    if not os.path.exists(save_filename):
        print("loading", url)
        req = urllib.request.Request(url=url, headers=headers)
        page = urllib.request.urlopen(req)
        data = page.read().decode("utf-8")
        with open(save_filename, "wt") as f:
            f.write(data)
    else:
        with open(save_filename, "rt") as f:
            data = f.read()

    posb = data.find("span class='kpd-date'")
    posc = data.find('data-attrid="kc:/location/statistical_region:population" aria-level="3" role="heading"')

    if posc > 0:
        pos0 = posc+106
        pos1 = data.find("<", pos0)
    elif posb > 0:
        pos0 = posb+44
        pos1 = data.find("<", pos0)
        pos2 = data.find("(", pos0)
        pos1 = min(pos1, pos2)

    if max(posb, posc) < 0:
        print(save_filename, url, country, posb, posc)
        continue

    popsize = data[(pos0):(pos1)].strip()

    popsize = popsize.replace(",", ".")
    popsize = popsize.replace(" ", "")
    popsize = popsize.replace(" ", "")
    popsize = popsize.replace("Milliarden", "*1000000000")
    popsize = popsize.replace("Millionen", "*1000000")
    popsize = popsize.replace("million", "*1000000")

    if len(popsize) > 3 and popsize[-4] == ".":
        popsize = popsize.replace(".", "")

    pos = popsize.find("(")
    if pos > 0:
        popsize = popsize[0:pos]

    val = int(eval(popsize))
    popsizes[key[0]] = val

    #print(key[0], val)


areas = dict()

for key in jdata["keys_by_name"]:

    country = key[0]
    country = country.replace("/", " ").strip()

    if country in ["Canada Diamond Princess", "Canada Grand Princess", "Canada Recovered", "Diamond Princess", "MS Zaandam", "United Kingdom Turks and Caicos Islands"]:
        areas[key[0]] = None
        continue

    if country == "United Kingdom Turks and Caicos Islands":
        areas[key[0]] = 616.3
        continue
    if country == "Holy See":
        areas[key[0]] = 0.44
        continue
    if country == "World":
        areas[key[0]] = 149400000
        continue
    if country == "Netherlands Curacao":
        areas[key[0]] = 444
        continue
    if country == "United Kingdom British Virgin Islands":
        areas[key[0]] = 150
        continue
    if country == "United Kingdom Channel Islands":
        areas[key[0]] = 118
        continue
    if country == "Denmark Faroe Islands":
        areas[key[0]] = 1399
        continue

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    url = "https://www.google.com/search?client=ubuntu&channel=fs&q=Fläche+" + country + "&ie=utf-8&oe=utf-8"
    url = url.replace(" ", "+")
    url = url.replace("ü", "%C3%BC")
    url = url.replace("ä", "%C3%A4")

    save_filename = "google_cache/" + hashlib.md5(url.encode("utf-8")).hexdigest()

    if not os.path.exists(save_filename):
        print("loading", url)
        req = urllib.request.Request(url=url, headers=headers)
        page = urllib.request.urlopen(req)
        data = page.read().decode("utf-8")
        with open(save_filename, "wt") as f:
            f.write(data)
    else:
        with open(save_filename, "rt") as f:
            data = f.read()

    posb = data.find("span class='kpd-date'")
    posc = data.find('data-attrid="kc:/location/location:area" aria-level="3" role="heading"')

    if posc > 0:
        pos0 = posc+90
        pos1 = data.find("<", pos0)
    elif posb > 0:
        pos0 = posb+44
        pos1 = data.find("<", pos0)
        pos2 = data.find("(", pos0)
        pos1 = min(pos1, pos2)

    if max(posb, posc) < 0:
        print(save_filename, url, country, posb, posc)
        continue

    area = data[(pos0):(pos1)].strip()

    area = area.replace(",", ".")
    area = area.replace(" ", "")
    area = area.replace(" ", "")
    area = area.replace("km²", "")
    area = area.replace("ha", "*0.01")
    #area = area.replace("Millionen", "*1000000")
    #area = area.replace("million", "*1000000")

    if len(area) > 3 and area[-4] == ".":
        area = area.replace(".", "")

    #pos = area.find("(")
    #if pos > 0:
    #    area = area[0:pos]

    val = float(eval(area))
    areas[key[0]] = val

    #print(key[0], val)


export_data = {
        'country_population': popsizes,
        'country_area': areas,
}

fn = "country_data.json"
with open(fn, 'w') as outfile:
    json.dump(export_data , outfile) 

print("data written to %s" % fn)


