import socket
import sys

def load_database(filename):
    tld_servers = {}
    own_mappings = {}
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            if len(lines) < 2:
                raise ValueError("RS database must have at least two lines")
            tld1 = lines[0].strip().split()
            tld_servers[tld1[0].lower()] = tld1[1]
            tld2 = lines[1].strip().split()
            tld_servers[tld2[0].lower()] = tld2[1]
            for line in lines[2:]:
                line = line.strip()
                if line:
                    parts = line.split()
                    own_mappings[parts[0].lower()] = (parts[0], parts[1])
    except Exception as e:
        print(f"Error loading database: {e}")
        sys.exit(1)
    return tld_servers, own_mappings

def get_tld(domain):
    parts = domain.split('.')
    return parts[-1].lower() if parts else ''

def main():
    if len(sys.argv) != 2:
        print("Usage: python rs.py rudns_port")
        sys.exit(1)

    rudns_port = int(sys.argv[1])
    tld_servers, own_mappings = load_database('rsdatabase.txt')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', rudns_port))
        s.listen()
        print(f"RS listening on port {rudns_port}")

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
                tld = get_tld(domain)

                if tld in tld_servers:
                    ts_hostname = tld_servers[tld]
                    if flags == 'it':
                        response = f"1 {domain} {ts_hostname} {req_id} ns"
                        conn.sendall(response.encode())
                        with open('rsresponses.txt', 'a') as log:
                            log.write(f"{response}\n")
                    elif flags == 'rd':
                        try:
                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ts_conn:
                                ts_conn.connect((ts_hostname, rudns_port))
                                ts_conn.sendall(data.encode())
                                ts_response = ts_conn.recv(1024).decode().strip()
                                ts_parts = ts_response.split()
                                # Modify aa to ra
                                if ts_parts[4] == 'aa':
                                    new_response = f"1 {ts_parts[1]} {ts_parts[2]} {req_id} ra"
                                else:
                                    new_response = ts_response
                                conn.sendall(new_response.encode())
                                with open('rsresponses.txt', 'a') as log:
                                    log.write(f"{new_response}\n")
                        except Exception as e:
                            response = f"1 {domain} 0.0.0.0 {req_id} nx"
                            conn.sendall(response.encode())
                            with open('rsresponses.txt', 'a') as log:
                                log.write(f"{response}\n")
                else:
                    key = domain.lower()
                    if key in own_mappings:
                        orig_domain, ip = own_mappings[key]
                        response = f"1 {orig_domain} {ip} {req_id} aa"
                    else:
                        response = f"1 {domain} 0.0.0.0 {req_id} nx"
                    conn.sendall(response.encode())
                    with open('rsresponses.txt', 'a') as log:
                        log.write(f"{response}\n")

if __name__ == '__main__':
    main()