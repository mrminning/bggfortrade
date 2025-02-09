import pytest
from itertools import count
import os
import sys

current_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current_directory)

sys.path.append(parent_directory)

from main import get_users_from_page, get_games_in_xml, build_url_for_user_want_data, build_url_for_user_fortrade_data, \
    build_url_for_users_in_city


def test_get_users_from_city():
    with open("tests/assets/city.html", "r") as assetpage:
        users = get_users_from_page(assetpage)
        assert len(users) == 2
        assert users[1] == "Testuser2"


def test_get_games_in_xml():
    xml_data = get_test_file("fortrade.xml")
    games = get_games_in_xml(xml_data)
    assert len(games) == 12


def get_test_file(filename):
    # Open an example file of users
    with open('tests/assets/' + filename, 'r') as file:
        return file.read().replace('\n', '')


def test_build_url_for_user_want_data():
    url = build_url_for_user_want_data("user_name")
    assert url == 'https://api.geekdo.com/xmlapi2/collection?username=user_name&type=thing&subtype=boardgame&want=1'


def test_build_url_for_user_fortrade_data():
    url = build_url_for_user_fortrade_data("user_name")
    assert url == 'https://api.geekdo.com/xmlapi2/collection?username=user_name&type=thing&subtype=boardgame&trade=1'


def test_build_url_for_user_fortrade_data():
    url = build_url_for_users_in_city("Country", "City", 3)
    assert url == 'https://boardgamegeek.com/users/page/3?country=Country&state=&city=City'
