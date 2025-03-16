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
        print("Usage: python ts2.py <rudns_port>")
        return

    rudns_port = int(sys.argv[1])

    ts2_database = load_database("ts2database.txt")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', rudns_port))
    server_socket.listen(5)

    print(f"TS2 Server listening on port {rudns_port}")

    while True:
        client_socket, addr = server_socket.accept()
        query = client_socket.recv(1024).decode()
        parts = query.split()
        domain = parts[1]
        query_id = parts[2]

        ip = ts2_database.get(domain, "0.0.0.0")
        if ip != "0.0.0.0":
            response = f"1 {domain} {ip} {query_id} aa"
        else:
            response = f"1 {domain} 0.0.0.0 {query_id} nx"

        client_socket.send(response.encode())
        client_socket.close()

if __name__ == "__main__":
    main()