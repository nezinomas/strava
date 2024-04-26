import contextlib
import re
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from bs4.element import ResultSet


class PageParser:

    def __init__(self, page):
        self.items = self.get_items(page)

    def get_items(self, page: str) -> ResultSet:
        """
        Get items from a page using BeautifulSoup.
        Args:
            page (str): The HTML content of the page.
        Returns:
            ResultSet: A collection of items found in the page.
        """
        content = BeautifulSoup(page, "html.parser")
        return content.find_all("div", id=lambda x: x and x.startswith("feed-entry-"))

    def get_entry_id(self, item: ResultSet) -> int:
        """
        Parses the entry id from a given feed item.
        Args:
            item (bs4.element.ResultSet): The feed item to parse.
        Returns:
            int: The entry id.
        """
        pattern = re.compile(r'feed-entry-(\d+)')
        res = re.findall(pattern, str(item))
        return int(res[0])

    def get_strava_id(self, item: ResultSet) -> int:
        """
        Parses the strava id from a given feed item.
        Args:
            item (bs4.element.ResultSet): The feed item to parse.
        Returns:
            int: The strava id.
        """
        link = item.find("a", attrs={"data-testid": "owners-name"})["href"]
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
        return item.find("a", attrs={"data-testid": "owners-name"}).text

    def get_date(self, item: ResultSet) -> datetime:
        """
        Parses the date from a given feed item.
        Args:
            item (bs4.element.ResultSet): The feed item to parse.
        Returns:
            datetime: The date and time.
        """
        date_str = item.find("time", attrs={"data-testid": "date_at_time"}).text

        if "Today" in date_str:
            date_str = date_str.replace("Today", datetime.now().strftime("%B %d, %Y"))

        if "Yesterday" in date_str:
            date_str = date_str.replace(
                "Yesterday",
                (datetime.now() - timedelta(days=1)).strftime("%B %d, %Y"),
            )

        formats = [
            "%d %B %Y",
            "%d %B %Y at %H:%M",
            "%B %d %Y",
            "%B %d, %Y",
            "%B %d, %Y at %I:%M %p",
            "%B %d, %Y at %I:%M",
            "%B %d, %Y at %H:%M"
        ]

        for fmt in formats:
            with contextlib.suppress(ValueError):
                return datetime.strptime(date_str, fmt)

        raise ValueError(f"Unrecognized datetime format {date_str}")

    def get_activity(self, item: ResultSet) -> str:
        """
        Parses the activity from a given feed item.
        Args:
            item (bs4.element.ResultSet): The feed item to parse.
        Returns:
            str: The activity name.
        """
        activity_type_str = item.find("title")

        return "Workout" if activity_type_str is None else activity_type_str.text

    def get_distance(self, item: ResultSet) -> int:
        """
        Parses the distance from a given feed item.
        Args:
            item (bs4.element.ResultSet): The feed item to parse.
        Returns:
            int: The distance in meters.
        """
        distance_str = item.find("span", string="Distance")
        if distance_str is None:
            return 0

        distance, units = distance_str.next_sibling.text.split(" ")

        if units == "m":
            distance = distance.split(",")[0]
        else:
            distance = float(distance) * 1000

        return int(distance)

    def get_time(self, item: ResultSet) -> int:
        """
        Parses the time from a given feed item and returns the total number of seconds.
        Args:
            item (bs4.element.ResultSet): The feed item to parse.
        Returns:
            int: The total number of seconds.
        """
        total_seconds = 0

        time_string = item.find("span", string="Time").next_sibling.text
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
        ascent_str = item.find("span", string="Elev Gain")
        if ascent_str is None:
            return 0

        return int(ascent_str.next_sibling.text.split(" ")[0])
