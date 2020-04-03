from datetime import datetime, timedelta
import ephem
import numpy as np
from PIL import Image
from math import degrees
import requests
import matplotlib
import matplotlib.animation # noqa
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt # noqa
from matplotlib.offsetbox import AnnotationBbox, OffsetImage # noqa
from mpl_toolkits.basemap import Basemap # noqa


def process_image(image, shape_color=(0, 0, 0, 255)):
    new_data = []
    data = image.getdata()
    background_color = data[0]

    for pixel in data:
        if pixel == background_color:
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append(shape_color)
    image.putdata(new_data)
    return image


req = requests.get("http://www.celestrak.com/NORAD/elements/stations.txt")
tle = req.text.split("\n")[0:3]
line1 = tle[0]
line2 = tle[1]
line3 = tle[2]

# line1 = 'ISS (ZARYA)'
# line2 = '1 25544U 98067A   19015.25189318  .00000401  00000-0  13432-4 0  9995' # noqa
# line3 = '2 25544  51.6418  41.9123 0002387 289.9764 167.0424 15.53761231151490' # noqa

iss_pos = ephem.readtle(line1, line2, line3)

fig = plt.figure(figsize=(8, 6), edgecolor='w')
map = Basemap(projection='mill', lon_0=0)
map.drawcoastlines()
map.drawparallels(np.arange(-90, 90, 30), labels=[1, 0, 0, 0])
map.drawmeridians(np.arange(map.lonmin, map.lonmax + 30, 60),
                  labels=[0, 0, 0, 1])
map.drawmapboundary(fill_color='aqua')
map.fillcontinents(color='coral', lake_color='aqua')
map.nightshade(datetime.utcnow())

# text = plt.text(0, 0, 'International\n Space Station', fontweight='bold',
#                 color=(0, 0.2, 1))
# iss_point, = plt.plot([], [], 'ob', markersize=10)

iss_image = Image.open('icon/iss_new.png')
# process_image(iss_image, (12, 12, 36))
# iss_image.save('icon/iss_new.png')

imagebox = OffsetImage(iss_image, zoom=0.08)
iss_icon = AnnotationBbox(imagebox, map(0, 0), xybox=(0, -4), xycoords='data',
                          boxcoords='offset points', frameon=False)
map._check_ax().add_artist(iss_icon)


def get_coords(time):
    iss_pos.compute(time)
    lon = degrees(iss_pos.sublong)
    lat = degrees(iss_pos.sublat)
    return lon, lat


def show_route():
    lon_list = []
    lat_list = []
    # ISS route from the past
    for seconds in range(-1000, 1, 10):
        lon, lat = get_coords(datetime.utcnow() + timedelta(seconds=seconds))
        lon_list.append(lon)
        lat_list.append(lat)
    x, y = map(lon_list, lat_list)
    map.plot(x, y, 'or', markersize=2)

    lon_list = []
    lat_list = []
    # ISS route from the future
    for seconds in range(0, 1001, 10):
        lon, lat = get_coords(datetime.utcnow() + timedelta(seconds=seconds))
        lon_list.append(lon)
        lat_list.append(lat)
    x, y = map(lon_list, lat_list)
    map.plot(x, y, 'ob', markersize=1)


def animate(i):
    lon, lat = get_coords(datetime.utcnow() + timedelta(seconds=1000))
    x, y = map(lon, lat)
    map.plot(x, y, 'ob', markersize=1)

    lon, lat = get_coords(datetime.utcnow())
    plt.title(f'''Date: {datetime.utcnow().strftime("%d %b %Y %H:%M:%S")} UTC
                  ISS position: latitude: {lat:.2f}, longitude: {lon:.2f} ''')
    x, y = map(lon, lat)
    map.plot(x, y, 'or', markersize=2)

    iss_icon.xy = [x, y]
    # iss_point.set_data(x, y)
    # text.set_position((x+5, y+5))


def main():
    show_route()
    ani = matplotlib.animation.FuncAnimation(fig, animate, frames=2,  # noqa
                                             interval=5000, repeat=True)
    plt.show()


if __name__ == "__main__":
    main()

#  iss icon from: https://www.iconspng.com/uploads/iss-silhouette/iss-silhouette.png # noqa
