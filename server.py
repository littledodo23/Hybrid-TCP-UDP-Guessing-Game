# Hybrid TCP/UDP Guessing Game Server
import socket
import threading
import random
import time

# Server settings
SERVER_HOST = '0.0.0.0'
TCP_PORT = 6000
UDP_PORT = 6001
MIN_PLAYERS = 2
MAX_PLAYERS = 4

# Global variables
players = {}  # {conn: (username, udp_address)}
player_udp_ports = {}  # {username: (ip, port)}
lock = threading.Lock()
target_number = random.randint(1, 100)
game_started = threading.Event()

# TCP server setup
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server.bind((SERVER_HOST, TCP_PORT))
tcp_server.listen()

# UDP server setup
udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server.bind((SERVER_HOST, UDP_PORT))

print(f"[SERVER] TCP Server running on {SERVER_HOST}:{TCP_PORT}")
print(f"[SERVER] UDP Server running on {SERVER_HOST}:{UDP_PORT}")
print("[SERVER] Waiting for players to register...")

def broadcast_tcp(message):
    for conn in list(players.keys()):
        try:
            conn.sendall(message.encode())
        except:
            continue

def handle_client(conn, addr):
    global players
    try:
        print(f"[TCP] New connection from {addr}")
        conn.sendall(b"Welcome! Please enter your player name:\n")

        while True:
            username = conn.recv(1024).decode().strip()
            if not username:
                continue

            with lock:
                if any(u == username for _, (u, _) in players.items()):
                    conn.sendall(b"Name already taken. Please choose another one:\n")
                else:
                    players[conn] = (username, None)
                    conn.sendall(b"Registration successful! Send your UDP port number:\n")
                    break

        # Receive client's UDP port
        udp_port_data = conn.recv(1024).decode().strip()
        udp_port = int(udp_port_data)
        player_udp_ports[username] = (addr[0], udp_port)

        print(f"[TCP] {username} registered with UDP port {udp_port}")
        conn.sendall(b"[CLIENT] Registered. Waiting for the game to start...\n")

        with lock:
            if len(players) == MIN_PLAYERS:
                print("[SERVER] Minimum players reached. Starting game...")
                game_started.set()

        # Wait for game start
        game_started.wait()

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")

def start_game():
    global target_number
    game_started.wait()
    print(f"[SERVER] Target number is: {target_number}")
    broadcast_tcp("\n[GAME] Game is starting! Guess the number between 1 and 100 using UDP.\n")
    winner = None
    start_time = time.time()

    while time.time() - start_time < 60:
        if winner:
            break
        try:
            udp_server.settimeout(1.0)
            data, client_addr = udp_server.recvfrom(1024)
            guess_data = data.decode().strip()

            for username, addr in player_udp_ports.items():
                if addr == client_addr:
                    try:
                        guess = int(guess_data)
                    except ValueError:
                        continue

                    print(f"[UDP] {username} guessed {guess}")

                    if guess < 1 or guess > 100:
                        udp_server.sendto(b"Warning: Out of the range, miss your chance", client_addr)
                        continue

                    if guess == target_number:
                        udp_server.sendto(b"Correct!", client_addr)
                        winner = username
                    elif guess < target_number:
                        udp_server.sendto(b"Lower", client_addr)
                    else:
                        udp_server.sendto(b"Higher", client_addr)
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[UDP ERROR] {e}")

    if winner:
        broadcast_tcp(f"\n=== GAME RESULTS ===\nTarget number was: {target_number}\nWinner: {winner}\n")
        print(f"[SERVER] {winner} WON THE GAME!! 🎉")
    else:
        broadcast_tcp(f"\n=== GAME RESULTS ===\nTarget number was: {target_number}\nNo one won this game.\n")
        print("[SERVER] Game ended without a winner.")

    broadcast_tcp("\n[SERVER] Closing connection...\n")
    close_all_connections()

def close_all_connections():
    for conn in list(players.keys()):
        try:
            conn.sendall(b"[SERVER] Closing connection.\n")
            conn.close()
        except:
            pass
    tcp_server.close()
    udp_server.close()
    print("[SERVER] All connections closed.")

def accept_players():
    threading.Thread(target=start_game, daemon=True).start()
    while len(players) < MAX_PLAYERS:
        conn, addr = tcp_server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    # Keep the server open after the game ends
    input("\nPress Enter to close the server...")

accept_players()
