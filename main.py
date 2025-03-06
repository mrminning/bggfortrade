# Find games for trade on BGG
# Enter your BGG id and City to search in.
import argparse
import os
import threading
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Defaults
PLEASE_WAIT = "Please try again later for access."
PLEASE_WAIT_429 = "Please try again later for access. Too many requests."
WAIT_TIME = 10
RETRIES = 3
threadLock = threading.Lock()


def get_users_from_page(page):
    users = []
    soup = BeautifulSoup(page, 'html.parser')
    result = soup.select('div.username')
    for item in result:
        link = item.find('a')
        users.append(link.string)
    return users


def get_games_in_xml(xml_data):
    games = {}
    bs_content = BeautifulSoup(xml_data, features="xml")
    for item in bs_content.find_all("item", {"subtype": "boardgame"}):
        bgg_id = int(item.get("objectid"))
        name = str(item.find("name").text)
        games[bgg_id] = name
    return games


def check_for_wanted_games(wanted_games, games):
    matches = {}
    for id, game in wanted_games.items():
        if id in games:
            matches[id] = game
    return matches


def get_users_wanted_games(user_name):
    xml_data = get_bgg_data_for_user(user_name, False, True)
    if xml_data is None:
        return {}
    else:
        return get_games_in_xml(xml_data)


def build_url_for_user_want_data(user_name):
    return "https://api.geekdo.com/xmlapi2/collection?username=" + user_name + "&type=thing&subtype=boardgame&want=1"


def build_url_for_user_fortrade_data(user_name):
    return "https://api.geekdo.com/xmlapi2/collection?username=" + user_name + "&type=thing&subtype=boardgame&trade=1"


def build_url_for_users_in_city(country, city, page):
    return "https://boardgamegeek.com/users/page/" + str(page) + "?country=" + country + "&state=&city=" + city


def get_bgg_data_for_user(user_name, trade, want):
    if want:
        url = build_url_for_user_want_data(user_name)
    else:
        url = build_url_for_user_fortrade_data(user_name)

    for i in range(RETRIES):
        content = make_request(url)
        if content is None:
            return None
        if PLEASE_WAIT_429 in str(content):
            time.sleep(WAIT_TIME * 2)
            get_bgg_data_for_user(user_name, trade, want)
        elif PLEASE_WAIT in str(content):
            time.sleep(WAIT_TIME)
            get_bgg_data_for_user(user_name, trade, want)
        else:
            return content


def get_users_in_city(country, city, page):
    if page is None:
        page = 1
    url = build_url_for_users_in_city(country, city, page)
    content = make_request(url)
    return get_users_from_page(content)


def make_request(url):
    req = requests.get(url)
    if req.status_code == 202:
        return PLEASE_WAIT
    if req.status_code == 429:
        return PLEASE_WAIT_429
    if req.status_code == 200:
        return req.content
    else:
        print("Unhandled response " + str(req.status_code) + " for " + url)
        return None


def get_all_users_in_city(country, city):
    page = 1
    users = get_users_in_city(country=country, city=city, page=page)
    all_users = users
    while len(users) > 0:
        page = page + 1
        users = get_users_in_city(country=country, city=city, page=page)
        all_users = all_users + users
    return all_users


def main(country, city, wanting_user, show_traders):
    TAKE = 10
    cities = city.split(",")
    wanted_games = get_users_wanted_games(wanting_user)
    print("%d games wanted in trade by user %s" % (len(wanted_games), wanting_user))
    for city in cities:
        clean_city = city.strip()
        if len(clean_city) == 0:
            continue
        all_users = get_all_users_in_city(country, clean_city)
        print("City: " + clean_city + " had " + str(len(all_users)) + " users")

        current = 0
        users = all_users[current:current + TAKE]
        while len(users) > 0:
            i = 0
            threads = []
            for user in users:
                i = i + 1
                thread = searcher(i, user, wanted_games, show_traders)
                print("Searching: " + user)
                thread.start()
                threads.append(thread)
            for t in threads:
                t.join()
            print ("Wait for threads")
            time.sleep(WAIT_TIME)
            current = current + TAKE
            users = all_users[current:current + TAKE]
    print("Done")


class searcher(threading.Thread):
    def __init__(self, thread_id, name, games, show_traders):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.games = games
        self.show_traders = show_traders

    def run(self):
        available_games = self.get_users_games_for_trade()
        print_link = False
        if len(available_games) > 0:
            with threadLock:
                if self.show_traders:
                    print("[%s] %s games for trade:" % (self.name, self.name))
                    for game_id, title in available_games.items():
                        print("[%s]    %s" % (self.name, title))
                        print_link = True
                matches = check_for_wanted_games(self.games, available_games)
                if len(matches) > 0:
                    print("[%s] %s has the following games you want for trade:" % (self.name, self.name))
                    for game_id, title in matches.items():
                        print("[%s]    %s" % (self.name, title))
                        print_link = True
                if print_link:
                    print("[%s]    https://boardgamegeek.com/collection/user/%s?trade=1&subtype=boardgame&ff=1" % (
                        self.name, self.name))

    def get_users_games_for_trade(self):
        xml_data = get_bgg_data_for_user(self.name, True, False)
        if xml_data is None:
            return {}
        else:
            return get_games_in_xml(xml_data)


if __name__ == '__main__':
    print("Searches BGG after games for trade near you")
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", help="Use env to get all inputs", action='store_true')
    args = parser.parse_args()
    print(args.env)
    load_dotenv()
    if args.env:
        main(os.getenv("country"), os.getenv("city"), os.getenv("user"), os.getenv("show"))
        exit(0)

    parser = argparse.ArgumentParser()
    parser.add_argument("country", help="The what country do you wish to search for traders")
    parser.add_argument("city", help="The what city do you wish to search for traders")
    parser.add_argument("user", help="User to get 'want in trade' list from")
    parser.add_argument("--show", help="Show all games for trade", action='store_true')
    args = parser.parse_args()
    print(args.env)
    main(args.country, args.city, args.user, args.show)
