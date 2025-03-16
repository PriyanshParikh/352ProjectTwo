import socket
import sys

def load_database(filename):
    database = {}
    with open(filename, "r") as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 2:
                database[parts[0]] = parts[1]
    return database

def main():
    if len(sys.argv) != 2:
        print("Usage: python ts1.py <rudns_port>")
        return

    rudns_port = int(sys.argv[1])

    ts1_database = load_database("ts1database.txt")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', rudns_port))
    server_socket.listen(5)

    print(f"TS1 Server listening on port {rudns_port}")

    responses = []

    while True:
        print("Waiting for connection...")  # Debug
        client_socket, addr = server_socket.accept()
        print(f"Connection received from {addr}")  # Debug
        query = client_socket.recv(1024).decode()
        print(f"Query received: {query}")  # Debug

        parts = query.split()
        if len(parts) < 3:
            print(f"Invalid query format: {query}")  # Debug
            client_socket.close()
            continue

        domain = parts[1]
        query_id = parts[2]

        print(f"Looking up domain: {domain}")  # Debug
        ip = ts1_database.get(domain, "0.0.0.0")
        print(f"IP found: {ip}")  # Debug

        if ip != "0.0.0.0":
            response = f"1 {domain} {ip} {query_id} aa"
        else:
            response = f"1 {domain} 0.0.0.0 {query_id} nx"

        print(f"Sending response: {response}")  # Debug
        responses.append(response)
        client_socket.send(response.encode())
        client_socket.close()

        with open("ts1responses.txt", "w") as file:
            for resp in responses:
                file.write(resp + "\n")

if __name__ == "__main__":
    main()