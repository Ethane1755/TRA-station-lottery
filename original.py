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

def get_distance_between_points(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points given their latitude and longitude."""
    theta = lon1 - lon2
    distance = 60 * 1.1515 * rad2deg(
        arccos(
            (sin(deg2rad(lat1)) * sin(deg2rad(lat2))) + 
            (cos(deg2rad(lat1)) * cos(deg2rad(lat2)) * cos(deg2rad(theta)))
        )
    )
    return round(distance * 1.609344, 2)

def load_stations(filename):
    """Load station data from a CSV file."""
    stations = {}
    with open(filename, newline='') as csvfile:
        rows = csv.reader(csvfile)
        for i, row in enumerate(rows):
            stations[i] = row
    return stations

def find_next_stations_within_distance(stations, base_id, max_dist=40, min_dist=10):
    """Find stations within a specific distance from the base station in one direction."""
    base_lat, base_lon = float(stations[base_id][6]), float(stations[base_id][7])
    return [
        (station_id, distance)
        for station_id in range(base_id + 1, len(stations))
        if (distance := get_distance_between_points(
            base_lat, base_lon, float(stations[station_id][6]), float(stations[station_id][7])
        )) >= min_dist and distance <= max_dist
    ]

def generate_next_station_within_distance(stations, previous_id):
    """Choose the next station within a specific distance from the previous station."""
    next_stations = find_next_stations_within_distance(stations, previous_id)
    if next_stations:
        random_station_id, distance = random.choice(next_stations)
        print(f"Chosen station: {stations[random_station_id][2]} within {distance} km of {stations[previous_id][2]}")
        return random_station_id
    print("No stations fouåçnd within the specified distance.")
    return None

def read_data(filename):
    """Read an integer from a data file."""
    with open(filename, 'r') as f:
        return int(f.read())

def get_station_name(stations, station_id):
    """Get the station name by station number."""
    return stations.get(station_id)[2]

def write_history(filename, station_id, name, stations):
    """Append station visit history to a file."""
    with open(filename, 'a') as f:
        f.write(f"{station_id}, {name}, {float(stations[station_id][6])}, {float(stations[station_id][7])}, {stations[station_id][4]}\n")

def read_history(filename):
    """Read visit history from a file."""
    with open(filename, 'r') as f:
        return [(line.split(', ')[0], line.split(', ')[1].strip()) for line in f]

def save_data(filename, station_id):
    """Save the new station number to data file."""
    with open(filename, 'w') as f:
        f.write(str(station_id))

def init_data(filename):
    """Initialize starting point to 台北站"""
    save_data(filename, 33)

def init_history(filename):
    """Clear last history"""
    open(filename, 'w').close()

def read_history_map(filename):
    """Read visit history for mapping purposes."""
    with open(filename, 'r') as f:
        return [line.split(', ') for line in f]

def generate_map():
    map_ = folium.Map(location=(23.58, 120.58), zoom_start=8)
    history = read_history_map('history.txt')
    for line in history:
        popup_html = f"<h1>{line[1]}</h1><h5>{line[4]}</h5><h5>{line[2]}°N, {line[3]}°E</h5>" \
                     f"<b><a href=https://google.com/maps/?q={line[2]},{line[3]} target=\"_blank\">Google Maps</a></b>"
        popup = folium.Popup(folium.Html(popup_html, script=True), max_width=250)
        folium.Marker(location=[float(line[2]), float(line[3])], popup=popup, 
                      icon=folium.Icon(icon='glyphicon-pushpin', color='darkblue', prefix='glyphicon')).add_to(map_)
    map_.save('history.html')
    print("Saving map... Done!")

def main():
    stations = load_stations('railway_station/station.csv')
    
    while True:
        previous_id = read_data('data.txt')
        move = input("What do you want to do? (init/random/add/map/exit) ")
        if move == 'init':
            init_data('data.txt')
            init_history('history.txt')
            print("Initializing... Done!")
        elif move in {'random', 'r'}:
            new_station_id = generate_next_station_within_distance(stations, previous_id)
            if new_station_id is not None:
                name = get_station_name(stations, new_station_id)
                print(f"Station ID: {new_station_id}, Name: {name}")
                write_history('history.txt', new_station_id, name, stations)
                save_data('data.txt', new_station_id)
            else:
                print("No new station chosen within the specified distance.")
        elif move == 'add':
            station_name = input("Where do you want to go? ")
            for key, station in stations.items():
                if f"{station_name}站" == station[2]:
                    print(f"{key} {station[2]} added.")
                    write_history('history.txt', key, station[2], stations)
                    save_data('data.txt', key)
        elif move == 'map':
            generate_map()
            subprocess.call(['open', 'history.html'])
        elif move == 'exit':
            print("Thank you, have a nice trip.")
            break
        else:
            print('Invalid input. Please try again. (init/random/add/map/exit)')

if __name__ == "__main__":
    main()