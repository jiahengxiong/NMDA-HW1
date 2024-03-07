import csv
import json
import time

import geopy.distance
import requests
from scapy.layers.inet import IP, ICMP
from scapy.sendrecv import sr


def get_ip(filename):
    """
    Retrieves a list of IP addresses from a CSV file.

    Args:
        filename (str): The name of the CSV file.

    Returns:
        list: A list containing IP addresses.
    """
    ip_list = []
    with open(filename, mode='r', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            ip_list.append(row['ip'])
    return ip_list


def get_local_address():
    """
    Retrieves the latitude and longitude of the local machine using the 'ipinfo.io' API.

    Returns:
        tuple: A tuple containing latitude and longitude.
    """
    response = requests.get('https://ipinfo.io/json')
    data = response.json()
    location = data['loc'].split(',')
    latitude = location[0]
    longitude = location[1]
    return latitude, longitude


def get_ip_location(ip):
    """
    Retrieves the latitude and longitude of a given IP address using the 'ip-api.com' API.

    Args:
        ip (str): The IP address.

    Returns:
        tuple: A tuple containing latitude and longitude.
    """
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}')
        response.raise_for_status()
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
    """
    Calculates the Round-Trip Time (RTT) to a given IP address using Scapy.

    Args:
        seq (int): Sequence number for the ICMP packet.
        ip (str): The IP address.

    Returns:
        float: The RTT in milliseconds.
    """
    rtt = None
    pck = IP(dst=ip) / ICMP(seq=seq)
    ans, unans = sr(pck, verbose=False, timeout=3)
    if ans is not None and len(ans) > 0:
        query = ans[0][0]
        response = ans[0][1]
        rtt = (response.time - query.sent_time) * 1000
    return rtt


def calculate_distance(src_addr, dst_addr):
    """
    Calculates the geodesic distance between two sets of coordinates using the geopy library.

    Args:
        src_addr (tuple): Source coordinates (latitude, longitude).
        dst_addr (tuple): Destination coordinates (latitude, longitude).

    Returns:
        float: The geodesic distance in kilometers.
    """
    dis = geopy.distance.distance(src_addr, dst_addr).km
    return dis


if __name__ == '__main__':
    # Load a list of server IP addresses from the 'server_list.csv' file.
    filename = 'server_list.csv'
    ip_list = get_ip(filename)

    # Get the local machine's coordinates (latitude, longitude).
    local_address = get_local_address()

    # Record the start time for tracking the elapsed time.
    start_time = time.time()
    locate_counter = 0
    average_RTT = []

    # Open or create a CSV file to store the calculated average RTT and geodesic distance.
    with open('rtt_distance.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['avg_rtt', 'distance'])

    # Iterate through each server IP address in the list.
    for ip in ip_list:
        print(f'Processing IP: {ip}')
        RTT = []
        congestion_counter = 0

        # Get the coordinates (latitude, longitude) of the server IP address.
        dst_address = get_ip_location(ip)
        locate_counter += 1

        # To avoid rate-limiting, sleep for a brief period after processing every 30 IP addresses.
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

        # Perform 20 rounds of ICMP ping to calculate Round-Trip Time (RTT).
        for x in range(0, 20):
            rtt = calculate_rtt(seq=x, ip=ip)
            if rtt is None:
                congestion_counter += 1
                print(f"{ip} cannot be reached: {congestion_counter}")
            else:
                RTT.append(rtt)
                congestion_counter = 0

            # If there are 20 consecutive failures to reach the server, stop further attempts.
            if congestion_counter >= 20:
                break

        # Calculate the average RTT and geodesic distance if successful pings were recorded.
        if len(RTT) > 0 and dst_address is not None:
            average_rtt = sum(RTT) / len(RTT)
            dis = calculate_distance(local_address, dst_address)
            print(f"Average RTT is {average_rtt} for {ip} with distance {dis}, the location is {dst_address}")

            # Write the results to the 'rtt_distance.csv' file.
            with open('rtt_distance.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([average_rtt, dis])
