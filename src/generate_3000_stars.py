import requests
from requests.adapters import HTTPAdapter, Retry
from pprint import pprint
import time
import os
from git import Repo
import pandas as pd

GITHUB_TOKEN = "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"


def get_url(low_star, high_star, page):
    return f"https://api.github.com/search/repositories?q=stars:{low_star}..{high_star}&sort=stars&order=desc&per_page=50&page={page}"


def get_last_page(response):
    if "Link" not in response.headers:
        return 1
    last_page = response.headers["Link"][
        -len('; rel="last"') - 10 : -len('; rel="last"')
    ]
    last_page = last_page[last_page.find("page") + len("page") + 1 :]
    last_page = last_page[: last_page.find(">")]
    last_page = int(last_page)
    return last_page


def main():
    range_list = list(range(3000, 20000, 100))
    s = requests.Session()
    retries = Retry(total=10, backoff_factor=1, status_forcelist=[403])
    s.mount("https://", HTTPAdapter(max_retries=retries))

    response_dfs = []
    range_gap = 99
    for start_range in range_list:
        print(f"Star range: {start_range} to {start_range + range_gap}")
        base_url = get_url(start_range, start_range + range_gap, 1)
        response = s.get(base_url, auth=("dzheng", GITHUB_TOKEN))
        last_page = 1
        while response.status_code != 200:
            print("Retrying")
            response = s.get(base_url, auth=("dzheng", GITHUB_TOKEN))
            time.sleep(5)
        if len(response.json()["items"]) == 50:
            last_page = get_last_page(response)
        print(f"Pages {last_page}")
        for i in range(last_page):
            print("Current Page", i + 1)
            cur_url = get_url(start_range, start_range + range_gap, i + 1)
            cur_response = s.get(base_url, auth=("dzheng", GITHUB_TOKEN))
            while cur_response.status_code != 200:
                print("Retrying")
                cur_response = s.get(base_url, auth=("dzheng", GITHUB_TOKEN))
            time.sleep(5)
            cur_response_df = pd.DataFrame(response.json()["items"])
            response_dfs.append(cur_response_df)
            time.sleep(2)
        print()

    # > 20k stars
    print("Star range: >20000")
    base_url = f"https://api.github.com/search/repositories?q=stars:>20000&sort=stars&order=desc&per_page=50&page="
    response = s.get(base_url, auth=("dzheng", GITHUB_TOKEN))
    last_page = get_last_page(response)
    print(f"Pages {last_page}")
    for i in range(last_page):
        print("Current Page", i + 1)
        cur_url = f"{base_url}{i+1}"
        cur_response = requests.get(base_url, auth=("dzheng", GITHUB_TOKEN))
        cur_response_df = pd.DataFrame(response.json()["items"])
        response_dfs.append(cur_response_df)
        time.sleep(2)

    response_df = pd.concat(response_dfs)
    response_df.to_pickle("out.pkl")


main()
