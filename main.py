import csv
import random
import folium
import subprocess
from numpy import sin, cos, arccos, pi, round

def rad2deg(radians):
    """Convert radians to degrees."""
    return radians * 180 / pi

def deg2rad(degrees):
    """Convert degrees to radians."""
    return degrees * pi / 180

def get_distance_between_points(latitude1, longitude1, latitude2, longitude2):
    """Calculate the distance between two points given their latitude and longitude."""
    theta = longitude1 - longitude2
    distance = 60 * 1.1515 * rad2deg(
        arccos(
            (sin(deg2rad(latitude1)) * sin(deg2rad(latitude2))) + 
            (cos(deg2rad(latitude1)) * cos(deg2rad(latitude2)) * cos(deg2rad(theta)))
        )
    )
    return round(distance * 1.609344, 2)

def load_stations(filename):
    """Load station data from a CSV file."""
    stations = {}
    stations1 = []
    with open(filename, newline='') as csvfile:
        rows = csv.reader(csvfile)
        for i, row in enumerate(rows):
            stations[i] = row
    return stations

def find_next_stations_within_distance(stations, base_station_id, max_distance=40, min_distance = 10):
    """Find next stations within a specific distance from the base station, in one direction only."""
    base_lat, base_lon = float(stations[base_station_id][6]), float(stations[base_station_id][7])
    next_stations = []
    for station_id in range(base_station_id + 1, len(stations)):  # Only check stations ahead
        station = stations[station_id]
        distance = get_distance_between_points(base_lat, base_lon, float(station[6]), float(station[7]))
        if min_distance <= distance <= max_distance:
            next_stations.append((station_id, distance))
    return next_stations

def generate_next_station_within_distance(stations, previous_station_id):
    """Choose the next station within the specified distance of the previous station in one direction."""
    next_stations = find_next_stations_within_distance(stations, previous_station_id)
    if next_stations:
        random_station_id, distance = random.choice(next_stations)
        print(f"Chosen station: {stations[random_station_id][2]} within {distance} km of {stations[previous_station_id][2]}")
        return random_station_id
    else:
        print("No stations found within the specified distance.")
        return None

def read_data(filename):
    """Read an integer from a data file."""
    with open(filename, 'r') as f:
        return int(f.read())

def get_station_name(stations, station_id):
    """Get the station name by station number."""
    return stations.get(station_id)[2]

def write_history(filename, station_id, name, stations):
    """Append station visit history to file."""
    with open(filename, 'a') as f:
        f.write(f"{station_id}, {name}, {float(stations[station_id][6])}, {float(stations[station_id][7])}, {stations[station_id][4]}\n")

def read_history(filename):
    """Read visit history from file."""
    history = []
    with open(filename, 'r') as f:
        for line in f:
            s = line.split(', ')
            history.append((s[0], s[1].strip()))
    return history

def save_data(filename, station_id):
    """Save the new station number to data file."""
    with open(filename, 'w') as f:
        f.write(str(station_id))

def init_data(filename):
    """Initialize starting point to 台北站"""
    with open(filename, 'w') as f:
        f.write(str(33))
    f.close()

def init_history(filename):
    """Clear last history"""
    open(filename,'w').close()

def read_history_map(filename):
    """Read visit history from file."""
    history = []
    with open(filename, 'r') as f:
        for line in f:
            s = line.split(', ')
            history.append([s[0], s[1], s[2], s[3], s[4]])
    return history

def map():
    Map = folium.Map(location=(23.58,120.58),zoom_start=8)
    history = read_history_map('history.txt')
    for line in history:
        #print(line)
        test = folium.Html(f"<h1>{line[1]}</h1> \
                             <h5>{line[4]}</h5> \
                             <h5>{line[2]}°N, {line[3]}°E</h5> \
                             <b><a href=https://google.com/maps/?q={line[2]},{line[3]} target=\"_blank\">Google Maps</a></b>",
                             script=True)
        popup = folium.Popup(test, max_width=250)
        folium.Marker(location = [line[2],line[3]],
                      popup=popup, 
                      icon=folium.Icon(icon='glyphicon-pushpin',color='darkblue',prefix='glyphicon')).add_to(Map)
    Map.save('history.html')
    print("Saving map... please wait.")
    print("Done!")


def main():
    stations = load_stations('railway_station/station.csv')
    
    while True:
        previous_station_id = read_data('data.txt')
        move = input("What do you want to do? (init/random/add/map/exit) ")
        if move == 'init':
            init_data('data.txt')
            init_history('history.txt')
            print("Initializing... Done!")
        elif move == 'random' or move == 'r':
            new_station_id = generate_next_station_within_distance(stations, previous_station_id)
            if new_station_id is not None:
                name = get_station_name(stations, new_station_id)
                print(f"Station ID: {new_station_id}, Name: {name}")

                write_history('history.txt', new_station_id, name, stations)
                #history = read_history('history.txt')
                #print("History:", history)

                save_data('data.txt', new_station_id)
            else:
                print("No new station chosen within the specified distance.")
        elif move == 'add':
            station_name = input("Where do you want to go? ")
            for key in stations:
                #print(f"{station_name}站",stations[key][2])
                if f"{station_name}站" == stations[key][2]:
                    new_station_id = key
                    name = stations[key][2]
                    #print(new_station_id, name)
                    print(f"{new_station_id} {name} added.")
                    write_history('history.txt', new_station_id, name, stations)
                    save_data('data.txt', new_station_id)
        elif move == 'map':
            map()
            url = 'history.html'
            subprocess.call(['open', url])
        elif move == 'exit':
            print("Thank you, have a nice trip.")
            break
        else:
            print('Input not defined, please try again. (init/random/add/map/exit)')
if __name__ == "__main__":
    main()