import requests
from requests.adapters import HTTPAdapter, Retry
from pprint import pprint
import time
import os
from git import Repo
import pandas as pd

GITHUB_TOKEN = "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"


def find_all(name, path):
    result = []
    for root, _, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result


def main():
    response_df = pd.read_pickle("3000_stars_or_more.pkl").reset_index(drop=True)

    from tqdm import tqdm

    start = 2254 + 104 + 2680
    # print(os.listdir())
    for i in tqdm(range(start, response_df.shape[0])):
        repo_url = response_df.iloc[i]["clone_url"]
        # print(repo_url)
        os.makedirs("./cur_repo", exist_ok=True)
        os.system(
            "rm -fr ./cur_repo"
        )  # cant be done using os.remove as we need to force
        Repo.clone_from(repo_url, "./cur_repo")
        pre_com_hooks_list = find_all(
            ".pre-commit-config.yaml", "./cur_repo"
        )  # potentially too slow

        if pre_com_hooks_list:
            response_df.iloc[
                i, response_df.columns.get_loc("has_pre_commit_hooks")
            ] = True

        for hook in pre_com_hooks_list:
            hook_folder = "found_hooks"
            file_name = f"{repo_url[repo_url.find('github.com')+len('github.com')+1:-4].replace('/', '-')}.yaml"
            os.system(f"cp {hook} ./{hook_folder}/{file_name}")
        # print()

    response_df.to_pickle("out_commit_hooks.pkl")


main()
