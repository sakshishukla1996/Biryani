from typing import List, Dict, Tuple
import datetime
import re
from lxml import html
import requests
from enum import Enum
import json


class ParseDateError(Exception):
    """This exception is raised when the date cannot be parsed."""

    pass


class Location(Enum):
    """This enum provides the possible mensa locations."""

    ESSLINGEN_STADTMITTE = 1
    FLANDERNSTRASSE = 2
    KUNSTAKADEMIE = 3
    LUDWIGSBURG = 4
    MUSIKHOCHSCHULE = 5
    STUTTGART_MITTE = 6
    STUTTGART_VAIHINGEN = 7


class DishType(Enum):
    """This enum provides the dish types used in the mensa menu."""

    Starter = "starter"
    Buffet = "buffet"
    MainDish = "main_dish"
    SideDish = "side_dish"
    Dessert = "dessert"

    @staticmethod
    def from_website_name(website_name: str) -> "DishType":
        """Converts the type as listed on the website into the type used in the dialog system.

        Args:
            website_name: The name as used in the response to the POST request.

        Returns:
            The corresponding enum member.

        """

        if website_name == "STARTER":
            return DishType.Starter
        elif website_name == "BUFFET":
            return DishType.Buffet
        elif website_name == "MAIN DISH":
            return DishType.MainDish
        elif website_name == "SIDE DISH":
            return DishType.SideDish
        elif website_name == "DESSERT":
            return DishType.Dessert


class CuisineType(Enum):
    """This enum provides the dish types used in the mensa menu."""

    Indian = "indian"
    Thai = "thai"
    Vietnamese = "vietnamese"
    Mexican = "mexican"
    Italian = "italian"
    German = "german"
    Chinese = "chinese"
    Greek = "greek"
    Turkish = "turkish"

    @staticmethod
    def from_website_name(website_name: str) -> "CuisineType":
        """Converts the type as listed on the website into the type used in the dialog system.

        Args:
            website_name: The name as used in the response to the POST request.

        Returns:
            The corresponding enum member.

        """

        if website_name == "INDIAN":
            return CuisineType.Indian
        elif website_name == "THAI":
            return CuisineType.Thai
        elif website_name == "VIETNAMESE":
            return CuisineType.Vietnamese
        elif website_name == "MEXICAN":
            return CuisineType.Mexican
        elif website_name == "ITALIAN":
            return CuisineType.Italian
        elif website_name == "GERMAN":
            return CuisineType.German
        elif website_name == "CHINESE":
            return CuisineType.Chinese
        elif website_name == "GREEK":
            return CuisineType.Greek
        elif website_name == "TURKISH":
            return CuisineType.Turkish


class Rest:
    def __init__(self, cuisine: str, location: str, restaurants: str):
        """The class for a  meal consisting of a name and several properties (slot-value pairs).

        Args:
                name: The name of the meal.
                day: The day on which the meal is offered.
                prices: The price for students and guests.
                price_quantity: The unit for which the price is valid.
                allergens: The allergens of this meal.
                vegan: Whether the meal is vegan or not.
                vegetarian: Whether the meal is vegetarian or not.
                fish: Whether the meal contains fish or not.
                pork: Whether the meal contains pork or not.
                dish_type: The type of the dish. (Starter, Buffet, Main Dish, Side Dish or Buffet)

        """
        self.cuisine = cuisine
        self.location = location
        self.restaurants = restaurants

    def as_dict(self) -> Dict[str, str]:
        """A dict representation of the meal."""

        return {"cuisine": self.cuisine, "location": self.location, "restaurants": self.restaurants}

    def __str__(self) -> str:
        """The string representation of the meal."""

        return f"Rest(cuisine={self.cuisine}, location={self.location}, restaurants={self.restaurants})"

    def __repr__(self) -> str:
        """The string representation of the meal."""

        return str(self)


class RestaurantParser:
    def __init__(self, cache: bool = True):
        """
        The class to issue post requests and parse the response. Will also take care of caching the
        parser's results.

        Args:
                cache (bool): Whether to cache results or not.

        """

        #: dict of str: storgae to cache parsed meals
        self.storage = {}
        self.cache = cache

    def _parse(self, cuisine: str, location: str) -> List[Rest]:
        """
                Issues a request for the given date. The response will be parsed and a list of meals
                returned.

        Args:
            date: The date for which the data will be parsed.

        Returns:
            :obj:`list` of Meal: List of parsed meals

        """

        # issue post request
        # print(f"HITTING API WITH {location} and CUisiNE: {cuisine}")
        response = requests.get(f"http://127.0.0.1:8000/location/{location}", params={"cuisine": cuisine})
        tree = json.loads(response.content.decode(response.encoding))
        results = [
            self._parse_restaurant(location=tree["location"], cuisine=tree["cuisine"], restaurants=rest)
            for rest in tree["restaurants"]
        ]
        # This will send results which are objects of [Rest()]
        return results

    def _parse_restaurant(self, location: str, cuisine: str, restaurants: str) -> Rest:
        """Parse all necessary properties of a meal from html.

        Args:
                meal: The html.HtmlElement which will be parsed.
                day: The day for which this meal is valid.
        """
        return Rest(cuisine=cuisine, location=location, restaurants=restaurants)

    def get_meals(self, cuisine: str, location: str, use_cache: bool = True) -> List[Rest]:
        """
                Gets the meals for a specified day by either looking them up in the cache or by issuing and
                parsing a post request.

                Args:
            date (str): The date for which the data will be returned.
                                Can be a string in the format 'Y-m-d' or one of today, tomorrow and monday-sunday.
            use_cache (bool): If False will always query the server instead of using the cache.

        Returns:
            :obj:`list` of Meal: List of meals for specified date
        """

        # date = self._parse(date)
        # if use_cache and date.date() in self.storage:
        #     # NOTE data could be deprecated
        #     return self.storage[date.date()]
        # else:
        #     # issue request to server
        #
        if cuisine == None:
            cuisine = "indian"
        if location == None:
            location = "stuttgart"
        return self._parse(cuisine, location=location)
