import contextlib
from dataclasses import dataclass

from bs4 import BeautifulSoup
from bs4.element import ResultSet


@dataclass
class Athlete:
    strava_id: int
    name: str


@dataclass
class Activity:
    strava_id: int
    moving_time: int
    distance: int
    num_activities: int
    ascent: int


class PageParser:

    def __init__(self, page_html: str):
        self.create_objects(page_html)

    def create_objects(self, page_html: str):
        self.items = self.get_items(page_html)

        self.athletes = []
        self.data = []

        if not self.items:
            return

        for item in self.items:
            try:
                strava_id = self.get_strava_id(item)
                name = self.get_name(item)
                moving_time = self.get_time(item)
                distance = self.get_distance(item)
                num_activities = self.get_num_activities(item)
                ascent = self.get_ascent(item)
            except TypeError:
                continue

            self.athletes.append(Athlete(strava_id, name))
            self.data.append(Activity(strava_id, moving_time, distance, num_activities, ascent))

    def get_items(self, page: str) -> ResultSet:
        """
        Get items from a page using BeautifulSoup.
        Args:
            page (str): The HTML content of the page.
        Returns:
            ResultSet: A collection of items found in the page.
        """
        content = BeautifulSoup(page, "html.parser")
        table = content.find_all("table")
        if not table:
            return None

        return table[0].find_all("tbody")[0].find_all("tr")

    def get_strava_id(self, item: ResultSet) -> int:
        """
        Parses the strava id from a given feed item.
        Args:
            item (bs4.element.ResultSet): The feed item to parse.
        Returns:
            int: The strava id.
        """
        link = item.find("a", {"class": "athlete-name"})["href"]
        # href="/athletes/5577666"
        return int(link.split("/")[-1])

    def get_name(self, item: ResultSet) -> str:
        """
        Parses the strava id from a given feed item.
        Args:
            item (bs4.element.ResultSet): The feed item to parse.
        Returns:
            str: The strava athlete name.
        """
        return item.find("a", {"class": "athlete-name"}).text

    def get_num_activities(self, item: ResultSet) -> int:
        """
        Parses the distance from a given feed item.
        Args:
            item (bs4.element.ResultSet): The feed item to parse.
        Returns:
            int: Number of activities.
        """
        num_str = item.find("td", {"class": "num_activities"}).text

        return int(num_str)


    def get_distance(self, item: ResultSet) -> int:
        """
        Parses the distance from a given feed item.
        Args:
            item (bs4.element.ResultSet): The feed item to parse.
        Returns:
            int: The distance in meters.
        """
        distance_str = item.find("td", {"class": "distance"}).text

        try:
            distance, _ = distance_str.split(" ")
        except ValueError:
            return 0

        return int(float(distance) * 1000)

    def get_time(self, item: ResultSet) -> int:
        """
        Parses the time from a given feed item and returns the total number of seconds.
        Args:
            item (bs4.element.ResultSet): The feed item to parse.
        Returns:
            int: The total number of seconds.
        """
        total_seconds = 0

        time_string = item.find("td", {"class": "moving_time"}).text
        time_components = time_string.split()

        for component in time_components:
            value = int(component[:-1])  # Extract the numerical value without the unit
            if "h" in component:
                total_seconds += value * 3600  # Convert hours to seconds
            elif "m" in component:
                total_seconds += value * 60  # Convert minutes to seconds
            elif "s" in component:
                total_seconds += value  # Seconds

        return total_seconds

    def get_ascent(self, item: ResultSet) -> int:
        """
        Parses the ascent from a given feed item.
        Args:
            item (bs4.element.ResultSet): The feed item to parse.
        Returns:
            int: The ascent in meters.
        """
        ascent_str = item.find("td", {"class": "elev_gain"}).text

        try:
            ascent, _ = ascent_str.split(" ")
        except ValueError:
            return 0

        with contextlib.suppress(IndexError):
            parts = ascent.split(",")
            ascent = "".join(parts) if len(parts[1]) >= 3 else parts[0]

        return int(ascent)
