import argparse
import requests
from bs4 import BeautifulSoup
import os
import shutil

URL = "https://xkcd.com/"
FOLDER = "./comics/"

def parse_arguments():
    parser = argparse.ArgumentParser(description="Scrape XKCD comics")
    parser.add_argument('from_page', type=int)
    parser.add_argument('to_page', type=int)
    return parser.parse_args()

def validate_arguments(args):
    if args.from_page < 1:
        raise ValueError("From_page must be greater than 0")
    # If the range is backwards, swap the values
    if args.from_page > args.to_page:
        temp = args.from_page
        args.from_page = args.to_page
        args.to_page = temp

def find_link(page):
    response = requests.get(URL + page.__str__())
    response.raise_for_status()
    website_html = response.text
    soup = BeautifulSoup(website_html, "html.parser")
    return soup.find(id="comic").find("img")["src"]

def main():
    args = parse_arguments()
    validate_arguments(args)
    shutil.rmtree(FOLDER, ignore_errors=True)
    os.mkdir(FOLDER)
    for p in range(args.from_page, args.to_page + 1):    
        img_url = find_link(p)
        img_response = requests.get(URL + img_url)
        img_response.raise_for_status()
        with open(f"{FOLDER}comic{p}.jpg", mode="wb") as file:
            file.write(img_response.content)

if __name__ == "__main__":
    main()