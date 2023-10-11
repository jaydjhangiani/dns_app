import pickle
import requests
import socket
from flask import Flask, request

app = Flask(__name__)
BUFFER_SIZE = 2048

@app.route('/')
def home():
    return 'US - User Server'


@app.route('/fibonacci', methods=["GET"])
def fibonacci():

    #get data
    hostname = request.args.get('hostname').replace('"','')
    fs_port  = int(request.args.get('fs_port'))
    number   = int(request.args.get('number'))
    as_ip    = request.args.get('as_ip').replace('"','')
    as_port  = int(request.args.get('as_port'))

    # Create UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Prepare and send a request to the AS (Application Server)
    request_data = ("A", hostname)
    udp_socket.sendto(pickle.dumps(request_data), (as_ip, as_port))

    # Receive and deserialize the response from the AS
    response, _ = udp_socket.recvfrom(BUFFER_SIZE)
    response = pickle.loads(response)
    hostname, fs_ip, = response

    if not fs_ip:
        return "Couldn't retrieve fs_ip"
    return requests.get(f"http://{fs_ip}:{fs_port}/fibonacci",
                        params={"number": number}).content


app.run(host='0.0.0.0',
        port=8080,
        debug=True)