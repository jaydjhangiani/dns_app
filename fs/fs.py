from flask import Flask, request
import socket
import pickle
app = Flask(__name__)
BUFFER_SIZE = 1024

@app.route('/')
def home():
    return "FS - Fibonacci Server"


# Fibonacci Function
def get_fib(n):
    if n < 0:
        raise ValueError("n should be greater than or equal to 0")
    elif n == 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    else:
        return get_fib(n - 1) + get_fib(n - 2)

# Calculating Fibonacci
@app.route('/fibonacci')
def fibonacci():
    n = int(request.args.get('number'))
    result = get_fib(n)
    return str(result)

# Registering Service
@app.route('/register', methods=['PUT'])
def register():
    body = request.json
    if not body:
        raise ValueError("Request body is empty")
    
    # Get Data
    hostname = body["hostname"]
    fs_ip    = body["fs_ip"]
    as_ip    = body["as_ip"]
    as_port  = body["as_port"]
    ttl      = body["ttl"]

    # Prepare and send the registration message to the AS (Application Server)

    registration_data = (hostname, fs_ip, "A", ttl)
    msg_bytes = pickle.dumps(registration_data)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto(msg_bytes, (as_ip, as_port))

    return "Registration Successful!"

if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=9090,
            debug=True)