import socket
import sys

def send_query(domain, flag, hostname, port, query_id):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((hostname, port))
        query = f"0 {domain} {query_id} {flag}"
        print(f"Sending query: {query} to {hostname}:{port}")  # Debug
        client_socket.send(query.encode())
        response = client_socket.recv(1024).decode()
        client_socket.close()
        print(f"Received response: {response} from {hostname}:{port}")  # Debug
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py <rs_hostname> <rs_port>")
        return

    rs_hostname = sys.argv[1]
    rs_port = int(sys.argv[2])

    with open("hostnames.txt", "r") as file:
        queries = file.readlines()

    resolved = []
    query_id = 1

    for query in queries:
        domain, flag = query.strip().split()
        response = send_query(domain, flag, rs_hostname, rs_port, query_id)
        
        if response:
            resolved.append(response)  # Log the initial response
            print(f"Resolved: {response}")

            parts = response.split()
            if parts[4] == "ns":  # Handle ns response (iterative resolution)
                tld_hostname = parts[2]
                print(f"Redirecting to TLD server: {tld_hostname}")  # Debug
                query_id += 1  # Increment query ID for the new query
                response = send_query(domain, flag, tld_hostname, rs_port, query_id)
                if response:
                    resolved.append(response)  # Log the final response
                    print(f"Resolved: {response}")
        
        query_id += 1  # Increment query ID for the next domain

    with open("resolved.txt", "w") as file:
        for response in resolved:
            file.write(response + "\n")

if __name__ == "__main__":
    main()