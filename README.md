# Game Specification

## 🧩 Overview
A real-time, round-based multiplayer number guessing game using Python sockets. Hybrid model with:
- **TCP** for control & setup
- **UDP** for fast guessing

## 🎮 Features
- 2–4 player support
- Real-time feedback: "Higher", "Lower", "Correct"
- Unique username enforcement
- Range checks & guess validation
- 10s timeout per guess

## 🔁 Protocol Workflow

### TCP Phase (Setup)
- Clients connect, send username
- Server checks:
  - Is username unique?
  - Have enough players joined?
- Server sends rules and signals game start

### UDP Phase (Gameplay)
- Server generates a number (1–100)
- Clients send guesses over UDP
- Server replies:
  - "Higher", "Lower", or "Correct"
- Round ends on correct guess or timeout
- Results sent via TCP

## 🧠 Architecture

### Server:
- Listens on both TCP/UDP
- Manages all game logic, players, and fairness

### Client:
- Uses TCP for registration and updates
- Uses UDP for gameplay
- Displays server feedback
