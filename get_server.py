import csv
import re
import socket

import requests
from bs4 import BeautifulSoup


def extract_hostname(url):
    """
    Extracts the hostname from a given URL.

    Args:
        url (str): The input URL.

    Returns:
        str: Extracted hostname or None if not found.
    """
    match = re.match(r'^(?:http|https|ftp|rsync)://([A-Za-z0-9.-]+)(/|$)', url)
    return match.group(1) if match else None


def get_urls_from_page(url):
    """
    Retrieves unique server hostnames from a webpage.

    Args:
        url (str): The URL of the webpage.

    Returns:
        set: A set of unique server hostnames.
    """
    page = requests.get(url)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, 'html.parser')
    urls = set()

    for link in soup.find_all('a', href=True):
        href = link['href']
        if re.match(r'^(?:http|https|ftp|rsync)://', href):  # Only process URLs with protocols
            hostname = extract_hostname(href)
            if hostname:
                urls.add(hostname)

    return urls


def save_urls_to_csv(urls, filename):
    """
    Saves server hostnames and their corresponding IP addresses to a CSV file.

    Args:
        urls (set): A set of server hostnames.
        filename (str): The name of the CSV file.
    """
    ip_list = []
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['server', 'ip'])
        for url in urls:
            ip = url2ip(url)
            if ip is not None and ip not in ip_list:
                writer.writerow([url, ip])
                ip_list.append(ip)


def url2ip(url):
    """
    Resolves the IP address of a given hostname.

    Args:
        url (str): The input hostname.

    Returns:
        str: The resolved IP address or None if unable to resolve.
    """
    ip = None
    try:
        ip = socket.gethostbyname(url)
        print(f'The IP address of {url} is {ip}')
    except socket.gaierror as e:
        print(f'Unable to resolve hostname: {url}. Error: {e}')
    return ip


if __name__ == '__main__':
    # Retrieve server URLs from GNU and Debian websites
    gnupg_urls = get_urls_from_page('https://www.gnu.org/prep/ftp.html')
    debian_urls = get_urls_from_page('https://www.debian.org/mirror/list')

    # Combine and sort the URLs
    all_urls = sorted(gnupg_urls.union(debian_urls))

    # Save server hostnames and IP addresses to a CSV file
    save_urls_to_csv(all_urls, 'server_list.csv')

"""
This script generates the 'server_list.csv' file based on the URL lists obtained from 'https://www.gnu.org/prep/ftp.html' 
and 'https://www.debian.org/mirror/list'.

The process involves extracting unique server hostnames from the provided URLs, resolving their corresponding IP addresses, 
and saving the results in a CSV file. Each row in the CSV file contains the server hostname and its corresponding IP address.

Note: Ensure that the 'requests', 'bs4' (BeautifulSoup), and 'socket' modules are installed before running this script.
"""
