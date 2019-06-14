#!/usr/bin/env python
#-*- coding: utf-8 -*-
import json
import os
import re
import requests
import sys
import urllib

def get_url_redirects(url: str) -> list:
    """Follow URL redirects and record the redirections
    and return them as a list.
    
    If there are no redirects, the returned list
    only contain the input URL.
    
    If there is an error, an empty list is returned,
    and the error is printed."""
    if not url:
        return []
    try:
        req = requests.get(url) 
    except Exception as e:
        print(f"Error during request to {url}: {e}")
        return []
    l = []
    for hist in req.history:
        l.append(hist.url) 
    l.append(req.url)
    return l

def is_valid_url(url: str) -> bool:
    """Check if input is a valid URL. 
    
    Returns True if valid URL, otherwise False."""
    DOMAIN_FORMAT = re.compile(
        r"(?:^(\w{1,255}):(.{1,255})@|^)"
        r"(?:(?:(?=\S{0,253}(?:$|:))"
        r"((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
        r"(?:[a-z0-9]{1,63})))"
        r"|localhost)"
        r"(:\d{1,5})?",
        re.IGNORECASE
    )
    SCHEME_FORMAT = re.compile(
        r"^(http|hxxp|ftp|fxp)s?$",
        re.IGNORECASE
    )
    url = url.strip()
    if not url:
        return False
    elif len(url) > 2048:
        return False    
    result = urllib.parse.urlparse(url)
    scheme = result.scheme
    domain = result.netloc
    if not scheme:
        return False
    elif not re.fullmatch(SCHEME_FORMAT, scheme):
        return False
    elif not domain:
        return False
    elif not re.fullmatch(DOMAIN_FORMAT, domain):
        return False
    return True

def convert_urls_to_list(text: str, separator="\n") -> list:
    """Convert string with URLs to a list of URLs.
       
    If the string contain non-URLs, they are not 
    added to the list.
    
    The URLs should be separated by a new line.
    Change this behavior using the `seperator` argument."""
    if not text:
        return []
    l = []
    for url in text.split(separator):
        if is_valid_url(url):
            l.append(url.strip())
    return l

def convert_to_unique_list(data: list) -> list:
    """Return list with only unique values from list."""
    return list(set(data))

def get_file_contents(filename: str, encoding="utf8") -> str:
    """Read the file contents."""
    if not os.path.isfile(filename):
        print("File not found: {}".format(filename))
        return None
    with open(filename, "r", encoding=encoding) as f:
        return f.read()

def follow_redirects(urls: list) -> list:
    """Takes a list of URLs and follow each URL. Returns list of dictionaries
    with each URL and its redirects."""
    l = []
    if urls:
        for url in convert_to_unique_list(urls):
            l.append({"url": url, "redirects": get_url_redirects(url)})
    else:
        print("Found 0 URLs")
    return l

def display_help():
    """Display available commands."""
    print("Follow URL redirects and display results as JSON.")
    print()
    print("Arguments:")
    print("  -f     Text file with one URL per line.")
    print("  -h     Show this help screen.")
    print("")
    print("Examples:")
    print("  {} http://wikipedia.org http://example.org".format(sys.argv[0]))
    print("  {} -f urls.txt".format(sys.argv[0]))

def main(params: list):
    """Main program to handle input parameters."""
    if len(params) == 1:
        display_help()
    else:
        if params[1] == "-h":
            display_help()
            return
        elif params[1] == "-f":
            if len(params) <= 2:
                print("Please provide a file name.")
                print("Example:")
                print("  {} -f urls.txt".format(sys.argv[0]))
                return
            else:
                # Read URLs from input file.
                data = get_file_contents(params[2])
                if not data:
                    return
                data = convert_urls_to_list(data)
        else:
            # Read URLs from command line.
            data = params[1:]
        # Follow URLs.
        data = follow_redirects(data)
        print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main(sys.argv)