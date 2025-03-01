import csv
import random
import folium
import subprocess
from numpy import sin, cos, arccos, pi, round
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
import webbrowser

# Global variables for file paths and settings
STATION_FILE = 'railway_station/station.csv'
HISTORY_FILE = 'history.txt'
DATA_FILE = 'data.txt'

# Function Definitions

def rad2deg(radians):
    """
    Convert radians to degrees.
    """
    return radians * 180 / pi

def deg2rad(degrees):   
    """
    Convert degrees to radians.
    """
    return degrees * pi / 180

def get_distance_between_points(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two geographic points using the Haversine formula.
    """
    theta = lon1 - lon2
    distance = 60 * 1.1515 * rad2deg(
        arccos(
            (sin(deg2rad(lat1)) * sin(deg2rad(lat2))) + 
            (cos(deg2rad(lat1)) * cos(deg2rad(lat2)) * cos(deg2rad(theta)))
        )
    )
    return round(distance * 1.609344, 2)

def load_stations(filename):
    """
    Load station data from a CSV file and store it in a dictionary.
    """
    stations = {}
    with open(filename, newline='') as csvfile:
        rows = csv.reader(csvfile)
        for i, row in enumerate(rows):
            stations[i] = row
    return stations

def find_next_stations_within_distance(stations, base_id, max_dist=40, min_dist=20):
    """
    Find all stations within a given distance range from a base station.
    """
    base_lat, base_lon = float(stations[base_id][6]), float(stations[base_id][7])
    return [
        (station_id, distance)
        for station_id in range(base_id + 1, len(stations))
        if (distance := get_distance_between_points(
            base_lat, base_lon, float(stations[station_id][6]), float(stations[station_id][7])
        )) >= min_dist and distance <= max_dist
    ]

def generate_next_station_within_distance(stations, previous_id):
    """
    Generate a random next station within the distance range from the previous station.
    """
    next_stations = find_next_stations_within_distance(stations, previous_id)
    if next_stations:
        while True:
            random_station_id, distance = random.choice(next_stations)
            if abs(random_station_id - previous_id) <= 20:
                return random_station_id, stations[random_station_id][2], distance
    return None, None, None

def read_data(filename):
    """
    Read a single integer (usually the last visited station ID) from a file.
    """
    with open(filename, 'r') as f:
        return int(f.read())

def save_data(filename, station_id):
    """
    Save the station ID to a file.
    """
    with open(filename, 'w') as f:
        f.write(str(station_id))

def write_history(filename, station_id, name, stations):
    """
    Write a station's visit history to a file.
    """
    with open(filename, 'a') as f:
        f.write(f"{station_id}, {name}, {float(stations[station_id][6])}, {float(stations[station_id][7])}, {stations[station_id][4]}\n")

def read_history(filename):
    """
    Read the station visit history from a file.
    """
    with open(filename, 'r') as f:
        return [line.split(', ')[1].strip() for line in f]

def read_history_map(filename):
    """
    Read and parse the station visit history in a format suitable for mapping.
    """
    with open(filename, 'r') as f:
        return [line.split(', ') for line in f]

def generate_map():
    """
    Generate an interactive map showing the station visit history and save it as an HTML file.
    """
    map_ = folium.Map(location=(23.58, 120.58), zoom_start=8)
    history = read_history_map(HISTORY_FILE)
    for line in history:
        popup_html = f"<h1>{history.index(line)+1}. {line[1]}</h1><h5>{line[4]}</h5><h5>{line[2]}°N, {line[3]}°E</h5>" \
                     f"<b><a href=https://google.com/maps/?q={line[2]},{line[3]} target=\"_blank\">Google Maps</a></b>"
        popup = folium.Popup(folium.Html(popup_html, script=True), max_width=280)
        folium.Marker(location=[float(line[2]), float(line[3])], popup=popup, 
                      icon=folium.Icon(icon='glyphicon-pushpin', color='darkblue', prefix='glyphicon')).add_to(map_)
    map_.save('history.html')
    subprocess.call(['open', 'history.html'])

# GUI Setup

stations = load_stations(STATION_FILE)

def initialize():
    """
    Initialize the app by setting the starting station to Taipei and clearing the history.
    """
    save_data(DATA_FILE, 0)
    open(HISTORY_FILE, 'w').close()
    with open(HISTORY_FILE, 'a') as f:
        f.write("100, 台北站, 25.0479239, 121.517081, 台北市中正區黎明里北平西路3號\n")
    update_current_station()
    update_history_list()
    messagebox.showinfo("Initialize", "Starting point set to 台北站, history cleared.")

def random_station():
    """
    Select a random station within the range of 10 to 40 km from the current station.
    """
    previous_id = read_data(DATA_FILE)
    new_station_id, name, distance = generate_next_station_within_distance(stations, previous_id)
    if new_station_id is not None:
        write_history(HISTORY_FILE, new_station_id, name, stations)
        save_data(DATA_FILE, new_station_id)
        update_current_station()
        update_history_list()
    else:
        messagebox.showinfo("Random Station", "No station found within the specified distance.\nThank you for the trip!")

def add_station():
    """
    Add a station by name to the history if it exists in the station list.
    """
    station_name = entry_station_name.get()
    for key, station in stations.items():
        if f"{station_name}站" == station[2]:
            write_history(HISTORY_FILE, key, station[2], stations)
            save_data(DATA_FILE, key)
            update_current_station()
            update_history_list()
            return
    messagebox.showwarning("Add Station", "Station not found.")

def update_current_station():
    """
    Update the label showing the current station based on the station ID.
    """
    station_id = read_data(DATA_FILE)
    station_name = stations[station_id][2]
    current_station_label.config(text=f"Current Station: {station_name}")

def update_history_list():
    """
    Update the listbox displaying the visit history.
    """
    history_list.delete(0, tk.END)
    history = read_history(HISTORY_FILE)
    for station in history:
        history_list.insert(tk.END, station)

def callback(url):
    """
    Open a URL in a web browser.
    """
    webbrowser.open_new(url)

# Set up tkinter window

root = tk.Tk()
root.title("TRA Lottery")
root.geometry("480x600")
root.minsize(480, 600)
root.resizable(True, True)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(6, weight=1)

# Current Station Label
current_station_label = tk.Label(root, text="Current Station: ")
current_station_label.grid(row=0, column=0, columnspan=2, pady=20, padx=10, sticky="ew")

# Buttons for Initializing and Random Station
tk.Button(root, text="Initialize", command=initialize).grid(row=1, column=0, padx=10, pady=5, sticky="W")
tk.Button(root, text="Random Station", command=random_station).grid(row=2, column=0, padx=10, pady=5, sticky="W")
Initialize_label = tk.Label(root, text="Set the starting station to Taipei")
Initialize_label.grid(row=1, column=1, columnspan=2, pady=10, padx=10, sticky="e")
Random_label = tk.Label(root, text="Pick random station in range 10 ~ 40 km")
Random_label.grid(row=2, column=1, columnspan=2, pady=10, padx=10, sticky="e")

# Frame for adding a specific station
frame_add_station = tk.Frame(root)
frame_add_station.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew", padx=10)
tk.Label(frame_add_station, text="Enter Station Name:").grid(row=0, column=0, padx=5, sticky="w")
entry_station_name = tk.Entry(frame_add_station)
entry_station_name.grid(row=0, column=1, pady=5, sticky="ew")
frame_add_station.grid_columnconfigure(1, weight=1)
tk.Button(root, text="Add Station", command=add_station).grid(row=4, column=0, pady=5, sticky="w", padx=10)
Add_label = tk.Label(root, text="Add station above, does not have to include '站'")
Add_label.grid(row=4, column=1, columnspan=2, pady=5, padx=10, sticky="e")

# History Listbox with label
tk.Label(root, text="Visit History:").grid(row=5, column=0, columnspan=2, pady=10, padx=10)
history_list = tk.Listbox(root, height=10, width=50)
history_list.grid(row=6, column=0, columnspan=2, pady=5, sticky="nsew", padx=10)

root.grid_rowconfigure(6, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Map Button
tk.Button(root, text="Show Map", command=generate_map).grid(row=7, column=0, columnspan=2, pady=5, sticky="e", padx=10)
Credit_label = tk.Label(root, text="Code by Ethane H., 2024.")
Credit_label.grid(row=8, column=0, pady=15, padx=10, columnspan=2,sticky="W")

# Link button
link1 = tk.Label(root, text="    >>> Source code")
f = tkFont.Font(link1, link1.cget("font"))
f.configure(underline=True)
link1.configure(font=f)
link1.bind("<Button-1>", lambda e: callback("https://github.com/Ethane1755/TRA-station-lottery"))
link1.grid(row=8, column=1, pady=0, padx=10, columnspan=2,sticky="W")

# Start GUI
update_current_station()
update_history_list()
root.mainloop()
