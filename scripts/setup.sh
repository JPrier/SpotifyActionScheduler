#!/usr/bin/env bash
set -euo pipefail

UV_BIN="$HOME/.local/bin"
RC="$HOME/.bashrc"

# Install uv if missing
if ! command -v uv &>/dev/null; then
  echo "[INFO] Installing uv…"
  curl -LsSf https://astral.sh/uv/install.sh | sh
else
  echo "[INFO] uv already installed."
fi

# ------------- ENVIRONMENT SETUP -------------
echo "[INFO] Setting up environment…"

# Ensure uv tools are live in THIS session
export PATH="$UV_BIN:$HOME/.cargo/bin:$PATH"

# Source .env files
set -a
source spotifyActionService/spotify.env
source project.env
set +a


# --------------- INSTALL TOOLS ---------------
# Sync & install tools/deps
echo "[INFO] Syncing & installing tools…"
uv add --dev . 
uv sync                                      

# Append to ~/.bashrc if necessary
if ! grep -Fqx "export PATH=\"$UV_BIN:\$PATH\"" "$RC" 2>/dev/null; then
  printf "\n# uv tools\nexport PATH=\"$UV_BIN:\$PATH\"\n" >> "$RC"
  echo "[INFO] Added uv bin to $RC"
else
  echo "[INFO] $RC already contains uv bin"
fi

# Reload ~/.bashrc so just is immediately available
#    (only if we're in a bash interactive shell)
if [[ -n "${BASH_VERSION:-}" && -t 1 ]]; then
  # shellcheck disable=SC1090
  source "$RC"
fi

echo "[SUCCESS] All tools installed and your PATH updated in Git Bash!"


