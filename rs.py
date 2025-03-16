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

def send_query_to_ts(domain, ts_hostname, ts_port, query_id):
    try:
        print(f"Attempting to connect to {ts_hostname}:{ts_port} for domain: {domain}")  # Debug
        ts_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ts_socket.connect((ts_hostname, ts_port))
        query = f"0 {domain} {query_id} rd"
        ts_socket.send(query.encode())
        response = ts_socket.recv(1024).decode()
        ts_socket.close()
        print(f"Received response from {ts_hostname}: {response}")  # Debug
        return response
    except Exception as e:
        print(f"Error connecting to {ts_hostname}:{ts_port}: {e}")  # Debug
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python rs.py <rudns_port>")
        return

    rudns_port = int(sys.argv[1])

    rs_database = load_database("rsdatabase.txt")
    ts1_hostname = rs_database.get("com")
    ts2_hostname = rs_database.get("edu")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', rudns_port))
    server_socket.listen(5)

    print(f"Root Server listening on port {rudns_port}")

    responses = []

    while True:
        client_socket, addr = server_socket.accept()
        query = client_socket.recv(1024).decode()
        parts = query.split()
        domain = parts[1]
        query_id = parts[2]
        flag = parts[3]

        print(f"Received query: {query}")  # Debug

        # Initialize response variable
        response = None

        if domain.endswith(".com") and ts1_hostname:
            if flag == "it":
                response = f"1 {domain} {ts1_hostname} {query_id} ns"
            else:
                ts_response = send_query_to_ts(domain, ts1_hostname, rudns_port, query_id)
                if ts_response:
                    ts_parts = ts_response.split()
                    if ts_parts[4] == "aa":
                        response = f"1 {domain} {ts_parts[2]} {query_id} ra"
                    else:
                        response = ts_response
        elif domain.endswith(".edu") and ts2_hostname:
            print(f"Forwarding .edu domain {domain} to TS2 at {ts2_hostname}:{rudns_port}")  # Debug
            if flag == "it":
                response = f"1 {domain} {ts2_hostname} {query_id} ns"
            else:
                ts_response = send_query_to_ts(domain, ts2_hostname, rudns_port, query_id)
                if ts_response:
                    ts_parts = ts_response.split()
                    if ts_parts[4] == "aa":
                        response = f"1 {domain} {ts_parts[2]} {query_id} ra"
                    else:
                        response = ts_response
        else:
            ip = rs_database.get(domain, "0.0.0.0")
            if ip != "0.0.0.0":
                response = f"1 {domain} {ip} {query_id} aa"
            else:
                response = f"1 {domain} 0.0.0.0 {query_id} nx"

        # Ensure response is assigned before using it
        if response is None:
            response = f"1 {domain} 0.0.0.0 {query_id} nx"

        print(f"Sending response: {response}")  # Debug
        responses.append(response)
        client_socket.send(response.encode())
        client_socket.close()

        with open("rsresponses.txt", "w") as file:
            for resp in responses:
                file.write(resp + "\n")

if __name__ == "__main__":
    main()