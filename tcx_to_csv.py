import xml.etree.ElementTree as ET
import pandas as pd
import dateutil.parser as dp
from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime as dt
from sys import argv

NAMESPACES = {
    'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
    'ns2': 'http://www.garmin.com/xmlschemas/UserProfile/v2',
    'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
    'ns4': 'http://www.garmin.com/xmlschemas/ProfileExtension/v1',
    'ns5': 'http://www.garmin.com/xmlschemas/ActivityGoals/v1'
}

if __name__ == '__main__':
    # You can either specify the filename from command line when you run the script or leave it blank and specify it here
    try:
        filename = argv[1]
    except:
        filename = 'D:/Downloads/activity_9918653664.tcx'

    
    tree = ET.parse(filename)
    root = tree.getroot()
    run = root[0][0]

    # Make a dataframe with all the trackpoint data
    data_list = []
    for lap_number, lap in enumerate(run.findall('ns:Lap', NAMESPACES)):
        for tp in lap.find('ns:Track', NAMESPACES).findall('ns:Trackpoint', NAMESPACES):
            data = {}
            data['Time'] = dp.parse(tp.find('ns:Time', NAMESPACES).text)
            data['Latitude'] = float(tp.find('ns:Position', NAMESPACES)[0].text)
            data['Longitude'] = float(tp.find('ns:Position', NAMESPACES)[1].text)
            data['Elevation'] = round(float(tp.find('ns:AltitudeMeters', NAMESPACES).text), 4)
            data['Distance'] = round(float(tp.find('ns:DistanceMeters', NAMESPACES).text), 2)
            data['Heart_rate'] = int(tp.find('ns:HeartRateBpm', NAMESPACES)[0].text)
            data['Speed'] = round(float(tp.find('ns:Extensions', NAMESPACES)[0][0].text), 3)
            data['Cadence'] = int(tp.find('ns:Extensions', NAMESPACES)[0][1].text)*2 #Cadence is recorded in Garmin as half the number most people use
            data['Lap'] = lap_number+1
            data_list.append(data)
    df = pd.DataFrame(data_list)

    # Simple manipulations to trackpoint data
    df['HR_smooth'] = df['Heart_rate'].rolling(20).mean()
    df['Distance_miles'] = df['Distance']/1609.34
    df['Elevation_feet'] = df['Elevation']*3.2808
    df['dElevation'] = df['Elevation_feet'].diff()
    
    # Save file
    timestamp = dt.now().strftime("%m-%d-%Y_%H%M%S")
    outfile = filename[:-4] + '_' + timestamp + '.csv'
    df.to_csv(outfile)