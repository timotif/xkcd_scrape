import argparse
import requests
from bs4 import BeautifulSoup
import os
import shutil
from urllib.parse import urlparse

URL = "https://xkcd.com/"
PAGE_FOLDER = "./pages/"

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

def download_page(page_number):
    response = requests.get(f"{URL}/{page_number}")
    response.raise_for_status()
    print(response.status_code)
    main_html = response.content
    return main_html

def find_resources(page, page_number):
    resources = []
    soup = BeautifulSoup(page, "html.parser")
    for tag in soup.find_all(["img", "link", "script"]):
        if tag.has_attr("src"):
            resources.append(tag["src"])
            local_resource_url = os.path.basename(urlparse(tag["src"]).path)
            tag["src"] = local_resource_url
        elif tag.name == "link":
            resources.append(tag["href"])
            local_resource_url = os.path.basename(urlparse(tag["href"]).path)
            tag["href"] = local_resource_url
    with open (f"{PAGE_FOLDER}/{page_number}/index.html", "wb") as file:
        file.write(soup.encode())
    return resources

def download_resources(page_number, resources):
    for resource in resources:
        if resource.startswith("//"):
            resource = "https:" + resource
        elif resource.startswith("/"):
            resource = URL + resource
        filename = os.path.basename(urlparse(resource).path)
        print("Resource "+ resource + " filename " + filename)
        response = requests.get(resource)
        with open (f"{PAGE_FOLDER}{page_number}/{filename}", "wb") as file:
            file.write(response.content)

def main():
    args = parse_arguments()
    validate_arguments(args)
    shutil.rmtree(PAGE_FOLDER, ignore_errors=True)
    os.mkdir(PAGE_FOLDER)
    for p in range(args.from_page, args.to_page + 1):    
        os.mkdir(f"{PAGE_FOLDER}{p}")
        main_html = download_page(p)
        resources = find_resources(main_html, p)
        download_resources(p, resources)

if __name__ == "__main__":
    main()