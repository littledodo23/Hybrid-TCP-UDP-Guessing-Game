# Hybrid TCP/UDP Guessing Game Client
import socket
import threading

SERVER_IP = '127.0.0.1'
TCP_PORT = 6000
UDP_PORT = 0  # OS assigns an available port automatically

def listen_for_feedback(udp_sock):
    # Thread to continuously listen for feedback from server
    while True:
        try:
            data, _ = udp_sock.recvfrom(1024)
            message = data.decode()
            print(f"[FEEDBACK] {message}")
            if "Correct" in message or "GAME RESULTS" in message:
                break
        except:
            break

def main():
    # TCP connection for control messages
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((SERVER_IP, TCP_PORT))
    print(f"[CLIENT] Connected to server at {SERVER_IP}:{TCP_PORT}")

    # Receive welcome and enter username
    welcome_msg = tcp_sock.recv(1024).decode()
    print(welcome_msg, end="")
    username = input("Enter your name: ")
    tcp_sock.sendall(username.encode())

    # Loop to retry username if it's already taken
    while True:
        response = tcp_sock.recv(1024).decode()
        print(response, end="")
        if "Send your UDP port number" in response:
            break
        username = input("enter your name  ")
        tcp_sock.sendall(username.encode())

    # Setup UDP socket
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('', 0))  # Bind to an available port
    udp_port = udp_sock.getsockname()[1]
    print(f"[CLIENT] Listening for UDP feedback on port {udp_port}...")

    # Send UDP port to server via TCP
    tcp_sock.sendall(str(udp_port).encode())
    wait_msg = tcp_sock.recv(1024).decode()
    print(wait_msg, end="")

    # Wait for game start broadcast from TCP
    while True:
        msg = tcp_sock.recv(1024).decode()
        print(msg, end="")
        if "Game is starting!" in msg:
            break

    # Start UDP listener thread
    feedback_thread = threading.Thread(target=listen_for_feedback, args=(udp_sock,), daemon=True)
    feedback_thread.start()

    # Begin guessing loop
    while True:
        try:
            guess = input("[GUESS] Enter your number (1-100): ")
            if not guess.isdigit() or not (1 <= int(guess) <= 100):
                print("Warning: Out of the range, miss your chance")
                continue
            udp_sock.sendto(guess.encode(), (SERVER_IP, 6001))

        except:
            break

    tcp_sock.close()
    udp_sock.close()

if __name__ == "__main__":
    main()