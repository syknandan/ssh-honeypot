#!/usr/bin/env python3
"""
Basic SSH Honeypot for Learning
WARNING: Run in isolated environment only!
"""

import socket
import threading
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('honeypot.log'),
        logging.StreamHandler()
    ]
)

class SSH_Honeypot:
    def __init__(self, host='0.0.0.0', port=2222):
        self.host = host
        self.port = port
        self.banner = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3\r\n"
        
    def handle_connection(self, client_socket, address):
        """Handle individual connections"""
        try:
            logging.info(f"New connection from {address[0]}:{address[1]}")
            
            # Send SSH banner
            client_socket.send(self.banner.encode())
            
            # Log connection details
            with open('connections.log', 'a') as f:
                f.write(f"{datetime.now()} - Connection from {address[0]}:{address[1]}\n")
            
            # Simple interaction loop
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    # Log received data
                    decoded_data = data.decode('utf-8', errors='ignore')
                    logging.info(f"Data from {address[0]}: {decoded_data.strip()}")
                    
                    # Send fake response
                    response = "Permission denied, please try again.\r\n"
                    client_socket.send(response.encode())
                    
                except socket.timeout:
                    break
                except Exception as e:
                    logging.error(f"Error handling data: {e}")
                    break
                    
        except Exception as e:
            logging.error(f"Connection handling error: {e}")
        finally:
            client_socket.close()
            logging.info(f"Connection closed from {address[0]}:{address[1]}")
    
    def start(self):
        """Start the honeypot server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            logging.info(f"Honeypot listening on {self.host}:{self.port}")
            print("=== HONEYPOT STARTED ===")
            print("Listening for connections on port 2222...")
            print("Press Ctrl+C to stop the honeypot")
            print("=" * 30)
            
            while True:
                client_socket, address = server_socket.accept()
                client_socket.settimeout(30)  # 30 second timeout
                
                # Handle each connection in a separate thread
                client_thread = threading.Thread(
                    target=self.handle_connection,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            logging.info("Honeypot shutting down...")
            print("\nHoneypot stopped by user")
        except Exception as e:
            logging.error(f"Server error: {e}")
        finally:
            server_socket.close()

if __name__ == "__main__":
    # Safety warning
    print("🚨 WARNING: This is a honeypot. Only run in isolated environments!")
    print("🚨 Do not run on networks with important systems!")
    answer = input("Do you understand and want to continue? (yes/no): ")
    
    if answer.lower() in ['yes', 'y']:
        honeypot = SSH_Honeypot(port=2222)
        honeypot.start()
    else:
        print("Good choice! Exiting safely.")