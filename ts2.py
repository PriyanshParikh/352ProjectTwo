import socket
import sys

def load_database(filename):
    database = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    key = parts[0].lower()
                    database[key] = (parts[0], parts[1])
    except Exception as e:
        print(f"Error loading database: {e}")
        sys.exit(1)
    return database

def main():
    if len(sys.argv) != 2:
        print("Usage: python ts2.py rudns_port")
        sys.exit(1)

    rudns_port = int(sys.argv[1])
    database = load_database('ts2database.txt')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', rudns_port))
        s.listen()
        print(f"TS2 listening on port {rudns_port}")

        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024).decode().strip()
                if not data:
                    continue
                parts = data.split()
                if len(parts) != 4 or parts[0] != '0':
                    continue
                domain = parts[1]
                req_id = parts[2]
                flags = parts[3]

                key = domain.lower()
                if key in database:
                    orig_domain, ip = database[key]
                    response = f"1 {orig_domain} {ip} {req_id} aa"
                else:
                    response = f"1 {domain} 0.0.0.0 {req_id} nx"

                conn.sendall(response.encode())
                with open('ts2responses.txt', 'a') as log:
                    log.write(f"{response}\n")

if __name__ == '__main__':
    main()