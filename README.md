# SpotifyActionScheduler

[![CI](https://github.com/JPrier/SpotifyActionScheduler/actions/workflows/ci.yml/badge.svg)](https://github.com/JPrier/SpotifyActionScheduler/actions)
[![PyPI Version](https://img.shields.io/pypi/v/spotifyactionscheduler?color=brightgreen)](https://pypi.org/project/spotifyactionscheduler)
[![Docker Image](https://img.shields.io/docker/pulls/jprier/spotifyactionscheduler?logo=docker\&label=Docker%20image)](https://hub.docker.com/r/jprier/spotifyactionscheduler)
[![License](https://img.shields.io/github/license/JPrier/SpotifyActionScheduler)](./LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/JPrier/SpotifyActionScheduler)](https://github.com/JPrier/SpotifyActionScheduler/commits/master)

**SpotifyActionScheduler** is a lightweight, configurable Python tool to keep your Spotify music in sync. It can synchronize your Spotify **Liked Songs** with any number of playlists – in either direction – while avoiding duplicates. The project is designed for easy local use or deployment via Docker, and it includes a continuous integration pipeline to ensure code quality.

## Features

* **Bidirectional Sync:** Sync tracks **from Liked Songs to a playlist** or **from a playlist to Liked Songs**. You can even perform a two-way sync between a playlist and Liked Songs in one go. (Spotify does not allow deleting from Liked Songs via API, so sync adds missing tracks but does not remove tracks that were unliked.)
* **Dynamic Configuration:** Define your sync actions in a simple JSON file. You can configure any number of “actions” specifying which playlists to sync and in what direction.
* **Duplicate Prevention:** The scheduler checks for existing tracks before adding new ones, ensuring no duplicate entries are created in your playlists by default.
* **Manual or Scheduled Runs:** Run the sync on-demand whenever you like, or schedule it to run periodically using cron (there’s no internal scheduler; you control the schedule).
* **Docker-Ready:** Easily containerize the application. The Docker setup allows one-step build and run with configuration via environment variables, making deployment simple on any system.
* **CI Pipeline:** Quality is enforced with GitHub Actions for linting (Flake8), testing (pytest), and other checks. This ensures stability and maintainability of the project.

## Installation

### Prerequisites

* **Python 3.13+** – Ensure you have Python installed (the project targets Python 3.13).
* **Spotify Developer Account:** You’ll need a Spotify API Client ID, Client Secret, and a Redirect URI for OAuth. (See **Configuration** below.)
* *(Optional)* **Docker** – If you plan to use the Docker container, install Docker Engine and CLI on your system.
* *(Optional but recommended)* **uv** – a fast Python dependency manager: https://github.com/astral-sh/uv

### Install (PyPI)

The easiest way to install SpotifyActionScheduler is from PyPI:

##### via pip

```bash
pip install spotifyactionscheduler
```

##### via uv

```bash
uv install spotifyactionscheduler
```

This will install the `spotifyActionService` package and its dependencies. You can then skip to the **Configuration** section below to set up your credentials and actions.

### Install from source (GitHub)

If you prefer to use the latest code from GitHub or contribute to the project:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/JPrier/SpotifyActionScheduler.git
   cd SpotifyActionScheduler
   ```

2. **Install the package and dependencies:**

   * You can install in editable/development mode using pip:

     ```bash
     pip install -e .
     ```

   * *Alternatively*, install the requirements directly:

     ```bash
     pip install -r requirements.txt
     ```

     ```bash
     uv sync
     ```

   This will install all necessary libraries (Spotify API client, etc.) for the scheduler to run.

### Using Docker

If you want to run the scheduler in a containerized environment, you have two options:

* **Pull the Docker image** (if available on Docker Hub):

  ```bash
  docker pull jprier/spotifyactionscheduler:latest
  ```

  This fetches a pre-built image with the application.

* **Build the Docker image locally:**

  ```bash
  git clone https://github.com/JPrier/SpotifyActionScheduler.git
  cd SpotifyActionScheduler
  docker build -t spotify-action-scheduler .
  ```

  This will create a local Docker image named `spotify-action-scheduler`.

After pulling or building the image, see **Running the Scheduler** below for how to configure and launch the container.

## Configuration

Before running SpotifyActionScheduler, you need to provide two pieces of configuration: **Spotify API credentials** (so the app can access your account) and **Sync Actions** (to tell the scheduler what to sync).

### 1. Spotify API Credentials (.env file)

You need to supply your Spotify API credentials via environment variables. The application uses the following **environment variables** (in line with [Spotipy’s](https://spotipy.readthedocs.io/en/latest/#authorized-requests) conventions):

* `SPOTIPY_CLIENT_ID` – Your Spotify Client ID
* `SPOTIPY_CLIENT_SECRET` – Your Spotify Client Secret
* `SPOTIPY_REDIRECT_URI` – The Redirect URI you set for your Spotify app

Create a file named **`.env`** (or any way to set env vars in your environment) and add your credentials:

```ini
SPOTIPY_CLIENT_ID=<your_spotify_client_id>
SPOTIPY_CLIENT_SECRET=<your_spotify_client_secret>
SPOTIPY_REDIRECT_URI=<your_redirect_uri>
```

> **Note:** The Redirect URI should match one of the allowed callback URLs in your Spotify developer app settings. If you don’t have a Spotify application yet, go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) to create an app and get these credentials. You can use a placeholder redirect URI such as `http://localhost:8888/callback` (and add it in your app settings) for the authorization flow.

When you run the scheduler for the first time, it will use these credentials to open a Spotify authorization page in your browser. **Log in and authorize** the application. After authorization, the app will receive an access token (and refresh token) for your account. The token will be saved locally (by default Spotipy stores it in a `.cache` file in the working directory). On subsequent runs, it will reuse the cached token so you won’t need to re-authenticate each time.

### 2. Defining Sync Actions (actions.json)

Next, tell the scheduler what you want to sync. This is done by creating an **actions JSON configuration** (by default, the app looks for a file named `actions.json`). You can start by copying the provided template from the repository (`spotifyActionService/actions.json.template`) and filling in your details. The configuration is a JSON array of action objects. Each action can specify:

* **source\_playlist\_id** – The Spotify Playlist ID to sync *from* (omit this to use your Liked Songs as the source).
* **target\_playlist\_id** – The Spotify Playlist ID to sync *to* (omit this to use Liked Songs as the target).
* **avoid\_duplicates** – *(Optional, boolean)* Whether to skip adding a track if it already exists in the target. Defaults to `true` if not provided.

Each action will cause the scheduler to take all songs from the source and ensure they exist in the target. If **both** `source_playlist_id` and `target_playlist_id` are provided, the tool will treat this as a two-way sync between those two playlists (adding any missing tracks in either direction in one run).

Here’s an example **`actions.json`** with a couple of typical scenarios:

```json
[
  {
    "type": "sync",
    "target_playlist_id": "37i9dQZF1DX2TRYkJECvfB",
    // This action will sync your Liked Songs into the playlist with ID above.
    // Since no source_playlist_id is provided, Liked Songs is assumed as source.
    "avoid_duplicates": true
  },
  {
    "type": "sync",
    "source_playlist_id": "37i9dQZF1DX8FwnYE6PRvL",
    // This action will sync the playlist with ID above into your Liked Songs.
    // target_playlist_id is omitted, so Liked Songs is the target.
    "avoid_duplicates": true
  },
  {
    "type": "sync",
    "source_playlist_id": "37i9dQZF1DWYDFZzt7nEFV",
    "target_playlist_id": "37i9dQZF1EuUwS6SL1VFV7",
    // This action will two-way sync between the two playlists IDs above.
    // Tracks from the first playlist will be added to the second, and vice-versa.
    "avoid_duplicates": true
  }
]
```

**How to find Spotify Playlist IDs:** You can get the playlist ID from the Spotify app or web URL. For example, in a Spotify playlist link like `https://open.spotify.com/playlist/37i9dQZF1DX2TRYkJECvfB`, the string after `/playlist/` (here `37i9dQZF1DX2TRYkJECvfB`) is the playlist ID.

Once you’ve created your `actions.json` file with the actions you want, place it in the working directory where you will run the scheduler (or in the project directory if running from source). By default, the scheduler will look for a file named **`actions.json`** in its directory. Ensure the JSON file is valid (structure and quotes, etc.); the application will parse this and run the specified sync actions.

## Running the Scheduler

With your environment variables and actions configured, you are ready to run the SpotifyActionScheduler.

### On-Demand Run (Manual Execution)

If you installed via pip or from source on your local machine, you can run the sync process with a single command. Make sure you are in the project directory (where your `.env` and `actions.json` live) or have set the environment variables in your shell:

* **Using the Python module:**
  Run the module directly with Python:

  ```bash
  python -m spotifyActionService
  ```

  This will execute the scheduler’s main routine and process all actions defined in your `actions.json` sequentially.

* **Using the provided script (source install):**
  If running from the cloned source, you can use the helper script:

  ```bash
  python scripts/onDemandHandler.py
  ```

  This does the same thing – it loads your config and performs the sync actions immediately.

* **Using the CLI command (pip install):**
  If installed as a package, a console entry-point may be available (for example, `spotify-action-scheduler` command). *(If this command is not available, use the `python -m` method above.)*

When you run the scheduler, you’ll see logs in the console for each action, such as fetching tracks from the source, checking for duplicates, and adding missing tracks to the target. On the first run, it will prompt you to authorize the Spotify API access (open a browser window). After authorization, it will begin syncing. Subsequent runs should use the cached token and proceed without prompts.

### Scheduled Runs (Cron or Task Scheduler)

To keep your playlists in sync continuously, you can schedule the scheduler to run at regular intervals using an external scheduler like cron (on Linux/Mac) or the Task Scheduler on Windows. Since SpotifyActionScheduler doesn’t include an internal scheduler, you control the timing.

**Example (cron on Linux):** to run the sync every hour, add a cron entry by running `crontab -e` and adding a line like:

```
0 * * * * cd /path/to/your/project && /usr/bin/env bash -c 'source .env && python -m spotifyActionService'
```

This will change directory to your project and run the scheduler on the hour, every hour. Make sure to adjust the path to your project and Python. We source the `.env` in the command so that the environment variables (Client ID/Secret/etc.) are loaded in the cron context.

If you containerized the app, you could instead run the Docker container on a schedule or keep it running continuously with an entrypoint script. A simple approach is to use host cron to invoke `docker run`:

```
0 * * * * docker run --rm --env-file /path/to/your/.env -v /path/to/your/actions.json:/app/spotifyActionService/actions.json spotify-action-scheduler
```

This example will, every hour, launch the Docker container (using the image name we built/pulled). It passes the `.env` file for credentials and mounts the local `actions.json` into the container at the expected location (`/app/spotifyActionService/actions.json`). The container runs the sync and exits (`--rm` removes the container after each run).

> **Tip:** Ensure the token cache is maintained between runs. If using Docker for scheduled runs, the Spotify OAuth token (stored in a `.cache` file) will reset each time unless you persist it. You can mount a volume to preserve the token cache file. For example, add `-v /path/to/cache/dir:/app/.cache` and set an environment variable `SPOTIPY_CACHE_PATH=/app/.cache` so that the token is reused. Alternatively, perform one initial run locally to generate the `.cache` file, then mount it into the container.

### Command-Line Options

The scheduler’s behavior is mainly driven by the `actions.json` configuration rather than command-line flags. However, there are a few things you can control:

* **Duplicate checking:** By default, `avoid_duplicates` is true for each action (either by default or as set in config). If for some reason you want to allow duplicates in a specific sync action, set `"avoid_duplicates": false` in that action’s JSON entry.
* **Logging verbosity:** The tool uses Python’s logging to output info. By default it prints info-level messages. Currently, there isn’t a specific CLI flag to toggle verbosity, but you can modify the logging level in the code or future releases may add an option.
* **Config file location:** By default, it looks for `actions.json` in the package directory or current working directory. If you wish to manage multiple config files, you currently would swap out or edit the `actions.json` file. (Future enhancements might include a CLI option to specify an alternate config file path.)

## Contributing

Contributions are welcome! If you have an idea for improvement or found a bug, feel free to open an issue or submit a pull request. When contributing code, please keep the following in mind:

* **Project Setup:** For development, install the package in editable mode as described above. It’s recommended to also install any dev dependencies (if provided, e.g. via a `requirements-dev.txt` or Poetry extras). This project uses a `justfile` for common tasks – if you have [just](https://github.com/casey/just) installed, you can run tasks like `just format` or `just test` if defined.
* **Coding Style:** The code is linted with **Flake8** in CI. Please run `flake8` (or `just lint`) to catch styling issues before committing.
* **Testing:** Ensure that you run **pytest** and that all tests pass. If you add new features, add corresponding unit tests. The CI pipeline will run the test suite on each pull request.
* **Commit Messages:** Follow clear and descriptive commit messages. If your PR addresses an open issue, please reference it in the description.
* **Branching Workflow:** It’s generally recommended to create a new branch for your feature or fix (don’t commit to `master` on your fork) and then open a PR from that branch.

Before starting significant work, you can also open an issue for discussion or to let others know you are working on something. We also recommend reading the [CONTRIBUTING](CONTRIBUTING.md) guide if available (to be added) for more details on the development workflow and standards.

## License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for details. This means you are free to use, modify, and distribute this software, but any copies or substantial portions of the software must include the original MIT license notice.

---

*Happy syncing! If you like this project or find it useful, consider giving it a star on GitHub. Feel free to share your feedback or questions via GitHub issues.*
