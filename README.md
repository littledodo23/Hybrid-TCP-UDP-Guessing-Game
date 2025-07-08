# 🔢 Hybrid TCP/UDP Number Guessing Game

A Python-based multiplayer number guessing game using hybrid socket communication. TCP handles player registration and control flow; UDP handles fast real-time number guesses and feedback.

## 🎯 Overview

- Players connect via TCP, register with a unique username, and send their local UDP port.
- Once the minimum number of players join, the game starts.
- Each player guesses a number (1–100) via UDP.
- The server responds with real-time feedback: **Higher**, **Lower**, or **Correct**.
- First player to guess correctly wins. If time runs out, the game ends with no winner.

## 👥 Player Rules

- **Minimum players**: 2  
- **Maximum players**: 4  
- **Timeout**: 60 seconds per game round  
- **Range**: Guesses must be between 1 and 100 (inclusive)

## 🧠 Server Setup

Run the server first:
```bash
python server.py
python client.py
