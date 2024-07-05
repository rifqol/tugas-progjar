import socket
import datetime

def send_request(server_ip, server_port):
    try:
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to the server
        client_socket.connect((server_ip, server_port))
        
        # Prompt the user for a command (TIME or QUIT)
        command = input("Enter 'TIME' to request current time, or 'QUIT' to exit: ").strip().upper()
        
        # Validate the command
        if command not in ["TIME", "QUIT"]:
            print("Invalid command. Please enter 'TIME' or 'QUIT'.")
            return
        
        # Send the command to the server
        client_socket.sendall(f"{command}\r\n".encode('utf-8'))
        
        # Receive and process the server response
        response = client_socket.recv(1024).decode('utf-8').strip()
        
        if command == "TIME":
            print(f"Server response (TIME): {response}")
        elif command == "QUIT":
            print("Quit request sent to server.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        client_socket.close()
        print("Connection closed.")

def main():
    # Replace with the actual IP address and port number of the server
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 45000
    
    # Continuously prompt the user for commands until they decide to quit
    while True:
        send_request(SERVER_IP, SERVER_PORT)
        if input("Do you want to send another request? (y/n): ").strip().lower() != 'y':
            break

if __name__ == "__main__":
    main()

