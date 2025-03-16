import socket
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py rs_hostname rudns_port")
        sys.exit(1)

    rs_hostname = sys.argv[1]
    rudns_port = int(sys.argv[2])
    current_id = 1
    resolved = []

    try:
        with open('hostnames.txt', 'r') as f:
            queries = f.readlines()
    except FileNotFoundError:
        print("hostnames.txt not found")
        sys.exit(1)

    for query_line in queries:
        query_line = query_line.strip()
        if not query_line:
            continue
        domain, mode = query_line.split()
        print(f"Processing query: {domain} {mode}")

        # Send query to RS
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((rs_hostname, rudns_port))
                query = f"0 {domain} {current_id} {mode}"
                s.sendall(query.encode())
                response = s.recv(1024).decode().strip()
                resolved.append(response)
                print(f"Received from RS: {response}")
            except Exception as e:
                print(f"Error connecting to RS: {e}")
                continue

        # Check if iterative and NS response
        parts = response.split()
        if mode == 'it' and len(parts) == 5 and parts[4] == 'ns':
            ts_hostname = parts[2]
            new_id = current_id + 1
            # Send query to TS
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ts_socket:
                try:
                    ts_socket.connect((ts_hostname, rudns_port))
                    new_query = f"0 {domain} {new_id} {mode}"
                    ts_socket.sendall(new_query.encode())
                    ts_response = ts_socket.recv(1024).decode().strip()
                    resolved.append(ts_response)
                    print(f"Received from TS: {ts_response}")
                except Exception as e:
                    print(f"Error connecting to TS: {e}")
            current_id = new_id + 1
        else:
            current_id += 1

    # Write resolved.txt
    with open('resolved.txt', 'w') as f:
        for res in resolved:
            f.write(f"{res}\n")

if __name__ == '__main__':
    main()