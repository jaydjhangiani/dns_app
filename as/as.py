import os
import json
import socket
import time
import pickle
import logging as log

# Configuration Constants
HOST_IP = "0.0.0.0"
SERVER_PORT = 53533
BUFFER_SIZE = 1024
AUTH_SERVER_DB_FILE = "/tmp/auth_db.json"
DNS_TYPE = "A"

def initialize_auth_server_db():
    if not os.path.exists(AUTH_SERVER_DB_FILE):
        with open(AUTH_SERVER_DB_FILE, "w") as f:
            json.dump({}, f, indent=4)

def save_dns_record(name, value, ttl):
    ttl_ts = time.time() + int(ttl)
    with open(AUTH_SERVER_DB_FILE, "r") as f:
        existing_records = json.load(f)
    existing_records[name] = (value, ttl_ts, ttl)
    with open(AUTH_SERVER_DB_FILE, "w") as f:
        json.dump(existing_records, f, indent=4)
    log.debug(f"Saving DNS record for {name}: {(value, ttl_ts, ttl)}")

def get_dns_record(name):
    with open(AUTH_SERVER_DB_FILE, "r") as f:
        existing_records = json.load(f)
    if name in existing_records:
        value, ttl_ts, ttl = existing_records[name]
        log.debug(f"Got DNS records for {name}: {existing_records[name]}")
        log.debug(f"Current time={time.time()} TTL timestamp={ttl_ts}")
        if time.time() > ttl_ts:
            log.info(f"TTL expired for {name}")
            return None
        return (DNS_TYPE, name, value, ttl_ts, ttl)
    log.info(f"No DNS record found for {name}")
    return None

def handle_client_request(udp_socket):
    msg_bytes, client_addr = udp_socket.recvfrom(BUFFER_SIZE)
    msg = pickle.loads(msg_bytes)
    log.info(f"Message from Client: {msg!r}")
    if len(msg) == 4:
        name, value, _, ttl = pickle.loads(msg_bytes)
        initialize_auth_server_db()
        save_dns_record(name, value, ttl)
    elif len(msg) == 2:
        _, name = msg
        dns_record = get_dns_record(name)
        response = dns_record if dns_record else ""
        response_bytes = pickle.dumps(response)
        udp_socket.sendto(response_bytes, client_addr)
    else:
        log.error(f"Expected msg of len 4 or 2, got: {msg!r}")
        udp_socket.sendto("Invalid message format", client_addr)


def main():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST_IP, SERVER_PORT))
    log.info(f"UDP server up and listening on "
             f"{socket.gethostbyname(socket.gethostname())}:{SERVER_PORT}")

    while True:
        try:
            handle_client_request(udp_socket)
        except Exception as e:
            log.error(f"An error occurred: {e}")


if __name__ == '__main__':
    
    log.basicConfig(format='[%(asctime)s %(filename)s:%(lineno)d] %(message)s',
                    datefmt='%I:%M:%S %p',
                    level=log.DEBUG)
    
    log.info("Spinning up authoritative server")
    main()