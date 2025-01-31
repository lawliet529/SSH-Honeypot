import paramiko
import socket
import threading
import time
from paramiko.ssh_exception import SSHException

# Generate host key with: ssh-keygen -t rsa -f host_key
HOST_KEY = paramiko.RSAKey(filename='keys/host_key')  # Update with your key path
LOG_FILE = 'logs/ssh_attempts.log'
PORT = 2222  # Use port 22 for real SSH (requires root)
CUSTOM_BANNER = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3"

class FakeSSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip
        self.username = None

    def check_auth_password(self, username, password):
        """Log password attempts and always reject authentication"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = (
            f"{timestamp},"
            f"{self.client_ip},"
            f"{username},"
            f"{password}\n"
        )
        
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
        
        print(f"Login attempt: {log_entry.strip()}")
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        """Reject public key authentication"""
        return paramiko.AUTH_FAILED

    def check_auth_interactive(self, username, submethods):
        """Reject interactive authentication"""
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        """Return allowed authentication methods"""
        return 'password,publickey,keyboard-interactive'

def handle_connection(client_sock, client_addr):
    """Handle incoming SSH connection"""
    transport = paramiko.Transport(client_sock)
    transport.add_server_key(HOST_KEY)
    transport.local_version = CUSTOM_BANNER
    
    try:
        server = FakeSSHServer(client_addr[0])
        transport.start_server(server=server)
        
        # Keep connection open to receive authentication attempts
        while transport.is_active():
            channel = transport.accept(1)
            if channel is not None:
                channel.close()
                break
    except SSHException:
        pass
    finally:
        transport.close()

def main():
    """Main server loop"""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('', PORT))
    server_sock.listen(100)

    print(f"Fake SSH server listening on port {PORT}...")
    
    while True:
        try:
            client_sock, client_addr = server_sock.accept()
            print(f"Connection from {client_addr[0]}:{client_addr[1]}")
            thread = threading.Thread(target=handle_connection, args=(client_sock, client_addr))
            thread.start()
        except Exception as e:
            print(f"Error: {str(e)}")
            break

if __name__ == '__main__':
    main()