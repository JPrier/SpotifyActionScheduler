# SpotifyActionScheduler

A lightweight, configurable Python tool to sync between your Spotify “Liked Songs” and any number of playlists — in either direction — while avoiding duplicates. Built for easy local use and Docker deployment, with a CI pipeline to enforce tests and linting.

---


[![CI](https://github.com/JPrier/SpotifyActionScheduler/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/JPrier/SpotifyActionScheduler/actions/workflows/ci.yml)

## 🚀 Features

- **Bidirectional sync**  
  - Liked Songs → Playlist  
  - Playlist → Liked Songs  
  - Optional two-way sync in a single action  
- **Dynamic configuration**  
  - Define any number of sync “actions” in a human-readable JSON file  
- **Duplicate-safe**  
  - By default, checks existing tracks before adding  
- **Manual or cron-driven**  
  - Run on demand via `python -m service/onDemandHandler.py`  
  - Schedule periodic runs with cron (no internal scheduler required)  
- **Docker-ready**  
  - One-step build & run with environment-variable configuration  
- **CI pipeline**  
  - GitHub Actions for linting (Flake8), unit tests (pytest), and branch protection  

---

## 📦 Getting Started

### Prerequisites

- Python 3.13  
- A Spotify developer account with **Client ID**, **Client Secret**, and a valid **Redirect URI**  
- (Optional) Docker & Docker CLI  

### Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/JPrier/SpotifyActionScheduler.git
   cd SpotifyActionScheduler
