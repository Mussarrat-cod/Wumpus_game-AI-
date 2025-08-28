# Wumpus World – Flask Web App

A Python-first Wumpus World web game with manual play and a simple heuristic AI agent.

## Features
- Flask backend with clean JSON API
- Python `WumpusWorld` logic (classic percepts: breeze, stench, glitter, scream)
- Actions: move, grab, shoot, climb
- Simple AI agent (`/api/ai/step`) that explores safely and exits with gold
- Configurable board size and pit count
- Reveal button for debugging/teaching
- Keyboard support: arrows to move, `g` grab, `c` climb, `s` shoot

## Quick Start


pip install -r requirements.txt
python app.py
