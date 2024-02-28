import csv
import json
import time

import geopy.distance
import requests
from scapy.layers.inet import IP, ICMP
from scapy.sendrecv import sr


def get_ip(filename):
    ip_list = []
    with open(filename, mode='r', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)

        for row in csvreader:
            ip_list.append(row['ip'])

    return ip_list


def get_local_address():
    response = requests.get('https://ipinfo.io/json')
    data = response.json()

    location = data['loc'].split(',')
    latitude = location[0]
    longitude = location[1]

    return latitude, longitude


def get_ip_location(ip):
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}')
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code

        # Before decoding JSON, ensure that the response is indeed JSON.
        if 'json' in response.headers.get('Content-Type'):
            data = response.json()
            if data['status'] == 'success':
                return data['lat'], data['lon']
            else:
                print(f"Error from ip-api: {data.get('message', 'Unknown error')}")
        else:
            print(f"Non-JSON response received, status code: {response.status_code}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as e:
        print(f"Request error occurred: {e}")
    except json.decoder.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err}")
    return None


def calculate_rtt(seq, ip):
    rtt = None
    pck = IP(dst=ip) / ICMP(seq=seq)
    ans, unans = sr(pck, verbose=False, timeout=0.8)
    if ans is not None and len(ans) > 0:
        query = ans[0][0]
        response = ans[0][1]
        rtt = (response.time - query.sent_time) * 1000
    return rtt


def calculate_distance(src_addr, dst_addr):
    dis = geopy.distance.distance(src_addr, dst_addr)
    return dis


if __name__ == '__main__':
    filename = '../server_list.csv'
    ip_list = get_ip(filename)
    local_address = get_local_address()
    start_time = time.time()
    locate_counter = 0
    average_RTT = []
    with open('../rtt_distance.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['avg_rtt', 'distance'])
    for ip in ip_list:
        print(f'Processing ip: {ip}')
        RTT = []
        congestion_counter = 0
        dst_address = get_ip_location(ip)
        locate_counter += 1
        if locate_counter >= 30:
            end_time = time.time()
            elapsed_time = end_time - start_time
            if elapsed_time < 61:
                sleep_time = 61 - elapsed_time
                print(f"Program ran for {elapsed_time:.2f} seconds. Sleeping for {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
            else:
                print(f"Program ran for {elapsed_time:.2f} seconds. No need to sleep.")
            locate_counter = 0
            start_time = time.time()
        for x in range(0, 20):
            rtt = calculate_rtt(seq=x, ip=ip)
            if rtt is None:
                congestion_counter += 1
                print(f"{ip} can not reach: {congestion_counter}")
            else:
                RTT.append(rtt)
                congestion_counter = 0
            if congestion_counter >= 5:
                break
        if len(RTT) > 0 and dst_address is not None:
            average_rtt = sum(RTT) / len(RTT)
            dis = calculate_distance(local_address, dst_address)
            print(f"Average rtt is {average_rtt} for {ip} with distance {dis}, the location is {dst_address}")
            with open('../rtt_distance.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([average_rtt, dis])
