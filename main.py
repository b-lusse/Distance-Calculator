import numpy as np
from geopy.geocoders import Nominatim
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_garden.mapview import MapView, MapMarker
from kivy.graphics import Color, Line
from kivy.core.window import Window
# Init settings
Window.size = (450, 975)
distance = '0'


# Declare map
class Map(MapView):
    pass


# Declare all screens
# Initial Menu Screen
class MenuScreen(Screen):
    pass


# Selection Screen where locations are selected
class SelectionScreen(Screen):
    # Create function to get city locations and distance
    def get_locations(self, city1, city2):
        """
        :param city1: Name of origin city
        :param city2: Name of destination city
        :return:
        """
        global distance, lon1, lat1, lon2, lat2 # Use global variables to also use in other screens
        locator = Nominatim(user_agent='myGeocoder')
        location1 = locator.geocode(city1)
        lon1 = location1.longitude
        lat1 = location1.latitude
        location2 = locator.geocode(city2)
        lon2 = location2.longitude
        lat2 = location2.latitude
        distance = self.distance_calc(lon1, lat1, lon2, lat2)

    def distance_calc(self, longitude1, latitude1, longitude2, latitude2):
        """
        :param longitude1: Longitude of first location
        :param latitude1: Latitude of first location
        :param longitude2: Longitude of second location
        :param latitude2: Latitude of second location
        :return: Integer value of distance between locations
        """
        radius = 6371  # Radius of earth in km
        phi1 = np.radians(latitude1)
        phi2 = np.radians(latitude2)
        delta_phi = np.radians(latitude2 - latitude1)
        delta_lambda = np.radians(longitude2 - longitude1)
        a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
        result = radius * (2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a)))  # Distance in km
        return int(np.rint(result))

    def on_distance(value):
        """
        Change displayed distance when the string/value for distance changes.
        """
        app = App.get_running_app()
        app.Label1.text = str(value)

    pass


# Distance Screen where distance and map are displayed
class DistanceScreen(Screen):

    def marker(self):
        """
        Make markers for origin and destination and add to map.
        """
        self.marker1 = MapMarker(lat=lat1, lon=lon1, source='green_marker.png')
        self.marker2 = MapMarker(lat=lat2, lon=lon2, source='red_marker.png')
        self.ids.mapview.add_marker(self.marker1)
        self.ids.mapview.add_marker(self.marker2)

    def line_layer(self):
        """
        Calculate pixel positions of line and draw on maplayer canvas
        """
        screen_origin = self.ids.mapview.get_window_xy_from(lat1, lon1, self.ids.mapview.zoom)
        screen_destination = self.ids.mapview.get_window_xy_from(lat2, lon2, self.ids.mapview.zoom)
        point_list = [screen_origin[0], screen_origin[1], screen_destination[0], screen_destination[1]]

        with self.ids.line.canvas:
            self.ids.line.canvas.clear()

            Color(0, 0, 0, .6)
            Line(points=point_list, width=3, joint="bevel")

    def center_screen(self):
        """
        Center the screen on the calculated midpoint between origin and destination.
        Also select corresponding zoom level.
        """
        avg_lat, avg_lon = self.midpoint_euclidean(lat1, lon1, lat2, lon2)
        self.ids.mapview.center_on(avg_lat,avg_lon) # Set map center

        # Zoom levels dependent on distance
        if (distance < 5000) & (distance > 2500):
            self.ids.mapview.zoom = 3
        elif (distance < 2500) & (distance > 1500):
            self.ids.mapview.zoom = 4
        elif (distance < 1500) & (distance > 1000):
            self.ids.mapview.zoom = 5
        elif (distance < 1000) & (distance > 500):
            self.ids.mapview.zoom = 6
        elif (distance < 500) & (distance > 250):
            self.ids.mapview.zoom = 7
        elif (distance < 250) & (distance > 80):
            self.ids.mapview.zoom = 8
        elif (distance < 80) & (distance > 30):
            self.ids.mapview.zoom = 9
        elif (distance < 30) & (distance > 10):
            self.ids.mapview.zoom = 10
        elif (distance < 10) & (distance > 5):
            self.ids.mapview.zoom = 11
        elif (distance < 5) & (distance > 0):
            self.ids.mapview.zoom = 12
        else:
            self.ids.mapview.zoom = 2

        self.marker() # Put markers on map
        self.line_layer() # Draw line

    def midpoint_euclidean(self, x1, y1, x2, y2):
        """
        Calculate the euclidean midpoint between two locations specified by latitude and longitude coordinates.
        :param x1: Latitude of first location
        :param y1: Longitude of first location
        :param x2: Latitude of second location
        :param y2: Longitude of second location
        :return:
        - res_x: Latitude of midpoint location
        - res_y: Longitude of midpoint location
        """
        dist_x = abs(x1 - x2) / 2.
        dist_y = abs(y1 - y2) / 2.
        res_x = x1 - dist_x if x1 > x2 else x2 - dist_x
        res_y = y1 - dist_y if y1 > y2 else y2 - dist_y
        return res_x, res_y

    def clear(self):
        """
        Remove used markers when returning back to SelectionScreen. This way they don't interfere with markers drawn for
        next calculation
        """
        self.ids.mapview.remove_marker(self.marker1)
        self.ids.mapview.remove_marker(self.marker2)

    def update(self, **kwargs):
        """
        Update calculated distance to be displayed
        :return: String of distance in kilometers
        """
        self.ids.Label1.text = str(distance) + ' kilometers'

    pass


class DistanceApp(App):

    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        # Add screens
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(SelectionScreen(name='selection'))
        sm.add_widget(DistanceScreen(name='distance'))
        return sm


if __name__ == '__main__':
    DistanceApp().run()