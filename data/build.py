
import csv
import sys
import datetime
import time
import copy
import json


ref_time = datetime.datetime(1970,1,1)

data = {}

for k in ["Confirmed", "Recovered", "Deaths"]:
    ts_key = 'timeseries_' + k.lower()

    fn = "data/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-" + k + ".csv"
    with open(fn) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:

            if line_count == 0:
                header = row

                for i in range(4,len(row)):
                    header[i] = int((datetime.datetime.strptime(row[i], '%m/%d/%y') - ref_time).total_seconds())

                line_count += 1
                continue
                
            line_count += 1

            key = row[1] + '/' + row[0]
            if key in data:
                rec = data[key]
            else:
                rec = {'id': key, 'province': row[0], 'country': row[1], 'lat': float(row[2]), 'lng': float(row[3])}

            timeseries = {}
            for i in range(4,len(row)):
                timeseries[header[i]] = int(row[i])

            rec[ts_key] = timeseries
            data[key] = rec

    # group by country
    keys = list(data.keys())
    for key in keys:
        if data[key]['province'].strip() != "":
            group_key = row[1] + '/'
            if group_key in data:
                new_group_data = data[group_key]
                add_timeseries = copy.deepcopy(data[key][ts_key])
                if ts_key in new_group_data:
                    for k,v in add_timeseries.items():
                        if k in new_group_data[ts_key]:
                            new_group_data[ts_key][k] += v
                        else:
                            new_group_data[ts_key][k] = v
                else:
                    new_group_data[ts_key] = add_timeseries
            else:
                new_group_data = copy.deepcopy(data[key])
                new_group_data['id'] = group_key
                new_group_data['province'] = ''
                new_group_data['is_group'] = True
            data[group_key] = new_group_data



# add german province data
for k in ["Confirmed"]:
    ts_key = 'timeseries_' + k.lower()

    fn = "data/COVID-19-Germany/germany_with_source.csv"
    with open(fn) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:

            if line_count == 0:
                header = row
                line_count += 1
                continue
                
            line_count += 1

            date = int((datetime.datetime.strptime(row[1], '%m/%d/%Y') - ref_time).total_seconds())
            country = "Germany"

            key = country + '/' + row[2] + '/' + row[3]
            if key in data:
                rec = data[key]
            else:
                try:
                    rec = {'id': key, 'province': row[2], 'district': row[3], 'country': country, 'lat': float(row[4]), 'lng': float(row[5]), ts_key: {}, 'timeseries_deaths': {}, 'timeseries_recovered': {}}
                except:
                    continue

            if date in rec[ts_key]:
                rec[ts_key][date] += 1
            else:
                rec[ts_key][date] = 1

            data[key] = rec

# calculate distance to earest neighbour

min_date = 10000000000000
max_date = 0
for k1 in data.keys():
    radius = 10000
    for k2 in data.keys():
        if k2 == k1:
            continue

        dx = data[k1]['lat'] - data[k2]['lat'];
        dy = data[k1]['lng'] - data[k2]['lng'];
        r = (dx*dx + dy*dy)**0.5
        if r < radius:
            radius = r
    data[k1]['approx_radius'] = radius;

    min_date = min(min_date, min(data[k1]['timeseries_confirmed'].keys()))
    max_date = max(max_date, max(data[k1]['timeseries_confirmed'].keys()))


export_data = {
        'cases': data,
        'min_date': min_date,
        'max_date': max_date
}

fn = "../public_html/data.json"
with open(fn, 'w') as outfile:
    json.dump(export_data , outfile) 

print("data written to %s" % fn)

