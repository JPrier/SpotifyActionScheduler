#!/usr/bin/env bash
set -euo pipefail

# ----------- BINS & PATHS -----------
UV_BIN="$HOME/.local/bin"
JUST_BIN="$HOME/.local/bin"
RC="$HOME/.bashrc"

# Ensure ~/.local/bin exists
mkdir -p "$UV_BIN"

# ----------- SETUP PATH for this session -----------
export PATH="$JUST_BIN:$UV_BIN:$HOME/.cargo/bin:$PATH"
export UV_LINK_MODE=copy

# ----------- SOURCE LOCAL ENV for dev -----------
echo "[INFO] Setting up environment…"
set -a
source spotifyActionService/spotify.env 2>/dev/null || true
set +a

# ----------- CI-ONLY: write spotify.env from secrets -----------
if [[ -n "${GITHUB_ACTIONS-}" ]]; then
  cat > spotifyActionService/spotify.env <<EOF
SPOTIFY_CLIENT_ID=${SPOTIFY_CLIENT_ID:-}
SPOTIFY_CLIENT_SECRET=${SPOTIFY_CLIENT_SECRET:-}
SPOTIFY_REDIRECT_URI=${SPOTIFY_REDIRECT_URI:-}
SPOTIPY_REFRESH_TOKEN=${SPOTIPY_REFRESH_TOKEN:-}
EOF

  # Decrypt actions.json if encrypted
  if [[ -f spotifyActionService/actions.json.gpg ]]; then
    echo "[INFO] Decrypting actions.json…"
    gpg --quiet --batch --yes \
      --passphrase "${GPG_PASSPHRASE:-}" \
      --pinentry-mode loopback \
      --output spotifyActionService/actions.json \
      --decrypt spotifyActionService/actions.json.gpg
  fi
fi

# ----------- INSTALL & SYNC TOOLS -----------
if [[ -z "${GITHUB_ACTIONS-}" ]]; then
  echo "[INFO] Syncing & installing tools…"
  uv sync
fi

# ----------- LOCAL-ONLY: persist PATH to ~/.bashrc -----------
if [[ -n "${BASH_VERSION:-}" && -t 1 && -z "${GITHUB_ACTIONS-}" ]]; then
  if ! grep -Fqx "export PATH=\"$UV_BIN:\$PATH\"" "$RC" 2>/dev/null; then
    printf "\n# uv tools\nexport PATH=\"$UV_BIN:\$PATH\"\n" >> "$RC"
    echo "[INFO] Added uv bin to $RC"
  else
    echo "[INFO] $RC already contains uv bin"
  fi
  source "$RC"
fi

echo "[SUCCESS] Environment ready!"
