import csv
import re
import socket

import requests
from bs4 import BeautifulSoup


def extract_hostname(url):
    match = re.match(r'^(?:http|https|ftp|rsync)://([A-Za-z0-9.-]+)(/|$)', url)
    return match.group(1) if match else None


def get_urls_from_page(url):
    page = requests.get(url)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, 'html.parser')
    urls = set()

    for link in soup.find_all('a', href=True):
        href = link['href']
        if re.match(r'^(?:http|https|ftp|rsync)://', href):  # 只处理包含协议的URL
            hostname = extract_hostname(href)
            if hostname:
                urls.add(hostname)

    return urls


def save_urls_to_csv(urls, filename):
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
    ip = None
    try:
        ip = socket.gethostbyname(url)
        print(f'The IP address of {url} is {ip}')
    except socket.gaierror as e:
        print(f'Unable to resolve hostname: {url}. Error: {e}')
    return ip


if __name__ == '__main__':
    gnupg_urls = get_urls_from_page('https://www.gnu.org/prep/ftp.html')
    debian_urls = get_urls_from_page('https://www.debian.org/mirror/list')
    all_urls = sorted(gnupg_urls.union(debian_urls))
    save_urls_to_csv(all_urls, 'server_list.csv')
