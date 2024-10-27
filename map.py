import csv
import folium
from folium.plugins import MarkerCluster

def read_history(filename):
    """Read visit history from file."""
    history = []
    with open(filename, 'r') as f:
        for line in f:
            s = line.split(', ')
            history.append([s[0], s[1], s[2], s[3]])
    return history


Map = folium.Map(location=(23.58,120.58),zoom_start=8)
history = read_history('history.txt')
for line in history:
    #print(line)
    folium.Marker(location = [line[2],line[3]],popup=folium.Popup(line[1], parse_html=True, max_width=80)).add_to(Map)
Map.save('history.html')
print("Saving map... please wait.")
print("Done!")
