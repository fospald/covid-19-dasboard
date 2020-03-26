
import urllib.request
import os
import calendar
import time
import datetime
import shutil
import csv
import sys

def parse_us_date(d):
    a = d.split("/")
    if len(a[2]) < 4:
        return datetime.datetime.strptime(d, '%m/%d/%y')
    return datetime.datetime.strptime(d, '%m/%d/%Y')

states = [
    {'name': 'Baden-Württemberg', 'lat': '48.56', 'lng': '9.06'},
    {'name': 'Bayern', 'lat': '49.09', 'lng': '11.62'},
    {'name': 'Berlin', 'lat': '52.51', 'lng': '13.4'},
    {'name': 'Brandenburg', 'lat': '52.51', 'lng': '13.4'},
    {'name': 'Bremen', 'lat': '53.1', 'lng': '8.80'},
    {'name': 'Hamburg', 'lat': '53.55', 'lng': '10.00'},
    {'name': 'Hessen', 'lat': '50.63', 'lng': '9.035'},
    {'name': 'Mecklenburg-Vorpommern', 'lat': '53.8', 'lng': '12.64'},
    {'name': 'Niedersachsen', 'lat': '52.88', 'lng': '9.38'},
    {'name': 'Nordrhein-Westfalen', 'lat': '51.55', 'lng': '7.62'},
    {'name': 'Rheinland-Pfalz', 'lat': '49.8', 'lng': '7.44'},
    {'name': 'Saarland', 'lat': '49.40', 'lng': '6.966'},
    {'name': 'Sachsen', 'lat': '51.04', 'lng': '13.34'},
    {'name': 'Sachsen-Anhalt', 'lat': '51.96', 'lng': '11.7'},
    {'name': 'Schleswig-Holstein', 'lat': '54.13', 'lng': '9.90'},
    {'name': 'Thüringen', 'lat': '50.85', 'lng': '11.05'}
]

time = calendar.timegm(time.gmtime())

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
url = "https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html"
save_filename = "rki_data/latest"

if not os.path.exists(save_filename) or (time - os.path.getmtime(save_filename)) > 3*60*60:
    print("loading", url)
    req = urllib.request.Request(url=url, headers=headers)
    page = urllib.request.urlopen(req)
    data = page.read().decode("utf-8")
    with open(save_filename, "wt") as f:
        f.write(data)


for tm in ["060000", "180000"]:

    key = "20200229172202"
    last_key = ""

    while True:

        key = key[0:8] + tm

        if key == last_key:
            break

        save_filename = "rki_data/%s" % key
        data = ""

        if os.path.exists(save_filename):
            with open(save_filename, "rb") as f:
                data = f.read().decode("utf-8")

            pos = data.find("/_static/images/toolbar/wm_tb_nxt_off.png")
            if pos > 0 and (time - os.path.getmtime(save_filename)) > 3*60*60:
                # pull latest record again
                data = ""

        if data == "":
            url = "https://web.archive.org/web/%s/https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html" % key
            print("loading", url)
            page = urllib.request.urlopen(url)
            data = page.read().decode("utf-8")
            with open(save_filename, "wt") as f:
                f.write(data)

        pos = data.find("/_static/images/toolbar/wm_tb_nxt_on.png")

        if pos < 0:
            break
        pos = data.rfind("href", 0, pos)
        if pos < 0:
            break
        pos0 = data.find('"', pos)
        if pos0 < 0:
            break
        pos1 = data.find('"', pos0+1)
        if pos1 < 0:
            break
        url = data[pos0+1:pos1]

        pos0 = url.find("web/")
        if pos0 < 0:
            break
        pos1 = url.find("/", pos0+6)
        if pos1 < 0:
            break

        last_key = key
        key = url[pos0+4:pos1]


records = {}

nr = 0
for root, dirs, files in os.walk("rki_data"):
    for file in files:
        if file[0] == ".":
            continue
        with open("rki_data/%s" % file, "rb") as f:
            data = f.read().decode("utf-8")

        data = data.replace("­", "")

        colindex = 0
        death_colindex = -1
        pos0 = data.find("</th></tr><tr><th", 0)
        if pos0 < 0:
            pos0 = 0
        while True:
            pos0 = data.find('<th ', pos0+1)
            if pos0 < 0:
                break
            pos0 = data.find('>', pos0+1)
            if pos0 < 0:
                break
            pos1 = data.find('</th>', pos0+1)
            if pos1 < 0:
                break
            colname = data[(pos0+1):pos1]
            pos0 = pos1
            if colname[0:5] == "Todes":
                death_colindex = colindex
            colindex += 1

        pos0 = data.find("Stand:")
        if pos0 < 0:
            print("Problem")
            continue
        pos1 = data.find(".", pos0)
        if pos1 < 0:
            print("Problem")
            continue
        pos2 = data.find(".", pos1+1)
        if pos2 < 0:
            print("Problem")
            continue
        pos3 = pos2+5
        
        date = data[pos0+6:pos3].strip()
        date = datetime.datetime.strptime(date, '%d.%m.%Y')
        date = date.strftime('%m/%e/%y').replace(" ", "")
        if date[0] == "0":
            date = date[1:]

        for s in states:
            confirmed = 0
            deaths = 0
            recovered = 0
            pos = data.find(">%s<" % s['name'])
            if pos > 0:
                pos0 = data.find(">", pos + len(s['name']) + 6)
                if pos0 > 0:
                    pos1 = data.find("<", pos0)
                    txt = data[pos0+1:pos1]

                    pos0 = txt.find("(")
                    if pos0 > 0:
                        pos1 = txt.find(")")
                        confirmed = int(txt[0:pos0].strip().replace(".", ""))
                        deaths = int(txt[pos0+1:pos1].strip().replace(".", ""))
                    else:
                        confirmed = int(txt.strip().replace(".", ""))
                    
                        if death_colindex >= 0:
                            # skip 3 columns
                            pos0 = pos + len(s['name'])
                            for _i in range(death_colindex):
                                pos0 = data.find("<td", pos0+1)
                            pos0 = data.find(">", pos0)
                            pos1 = data.find("<", pos0)
                            deaths = data[pos0+1:pos1].strip()
                            deaths = int(deaths) if len(deaths) else 0

            key = s['name']

            if key in records:
                rec = records[key]
            else:
                rec = {'state': s['name'], 'timeseries_confirmed': {}, 'timeseries_deaths': {}, 'timeseries_recovered': {}, 'lat': s['lat'], 'lng': s['lng']}

            if date in rec['timeseries_confirmed']:
                rec['timeseries_confirmed'][date] = max(confirmed, rec['timeseries_confirmed'][date])
            else:
                rec['timeseries_confirmed'][date] = confirmed

            if date in rec['timeseries_deaths']:
                rec['timeseries_deaths'][date] = max(deaths, rec['timeseries_deaths'][date])
            else:
                rec['timeseries_deaths'][date] = deaths

            if date in rec['timeseries_recovered']:
                rec['timeseries_recovered'][date] = max(recovered, rec['timeseries_recovered'][date])
            else:
                rec['timeseries_recovered'][date] = recovered

            records[key] = rec



for k in ["Confirmed", "Recovered", "Deaths"]:
    ts_key = 'timeseries_' + k.lower()

    fn = "COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_" + k.lower() + "_global.csv"
    with open(fn) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            dates = row[4:]
            break

    current_day = parse_us_date(dates[-1])

    # append next day
    date = current_day + datetime.timedelta(days=1)
    date = date.strftime('%m/%e/%y').replace(" ", "")
    if date[0] == "0":
        date = date[1:]
    dates.append(date)

    fn_new = "COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-" + k + "-germany.csv"
    shutil.copyfile(fn, fn_new)
    with open(fn_new, "at") as f:
        for key, rec in records.items():
            cols = [rec['state'], 'Germany', rec['lat'], rec['lng']]
            val = 0
            for date in dates:
                if date in rec[ts_key]:
                    val = rec[ts_key][date]
                cols.append(str(val))
            f.write("\n")
            f.write(",".join(cols))


