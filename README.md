# SpotifyActionScheduler

[![CI](https://github.com/JPrier/SpotifyActionScheduler/actions/workflows/ci.yml/badge.svg)](https://github.com/JPrier/SpotifyActionScheduler/actions)
[![PyPI Version](https://img.shields.io/pypi/v/spotify-actions?color=brightgreen)](https://pypi.org/project/spotify-actions)
[![License](https://img.shields.io/github/license/JPrier/SpotifyActionScheduler)](./LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/JPrier/SpotifyActionScheduler)](https://github.com/JPrier/SpotifyActionScheduler/commits/master)

**SpotifyActionScheduler** is a small Python utility that automates simple playlist maintenance tasks.  It can copy tracks from one playlist into another and it can archive older tracks from a playlist into a separate archive playlist.  A minimal scheduler is included so actions may run on a timer, or you can trigger them on demand.

## Features

* **Playlist Sync:** Copy tracks from a source playlist into a target playlist. Only missing tracks are added.
* **Archive Tracks:** Copy older items from a playlist into a new archive playlist named `<source>-Archive`.
* **Configurable Actions:** Define sync and archive actions in a simple JSON file.
* **Built‑in Scheduler:** Actions can run once or at regular intervals using the bundled scheduler.
* **Duplicate Prevention:** When enabled, the service skips tracks that already exist in the destination playlist.
* **CI Pipeline:** GitHub Actions run linting and tests to keep the codebase healthy.

## Installation

### Prerequisites

* **Python 3.12+** – The code targets modern Python and is tested with Python 3.12.
* **Spotify Developer Account:** You’ll need a Spotify API Client ID, Client Secret, and a Redirect URI for OAuth. (See **Configuration** below.)
* *(Optional but recommended)* **uv** – a fast Python dependency manager: https://github.com/astral-sh/uv

### Install (PyPI)

The easiest way to install SpotifyActionScheduler is from PyPI:

##### via pip

```bash
pip install spotifyactionscheduler
```

##### via uv

```bash
uv venv .venv
source .venv/bin/activate  # (or .venv\\Scripts\\activate on Windows)
uv pip install spotifyactionscheduler
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

   * **Option 1: Using pip**
    This will install all necessary libraries (Spotify API client, etc.) for the scheduler to run.
    ```bash
    pip install -e .
    pip install -r requirements.txt
    ```

   * ***Preferred* -- Option 2: Using uv:**
    ✅ This installs dependencies from uv.lock and installs the project in editable mode.

    ```bash
    uv venv .venv
    source .venv/bin/activate  # (or .venv\\Scripts\\activate on Windows)
    uv sync
    ```


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

* **source\_playlist\_id** – The Spotify Playlist ID to sync from.
* **target\_playlist\_id** – The Spotify Playlist ID to sync to.
* **avoid\_duplicates** – *(Optional, boolean)* Whether to skip adding a track if it already exists in the target. Defaults to `true` if not provided.

Each action will cause the scheduler to copy all songs from the source playlist into the target playlist. The tool does not currently support synchronising in the opposite direction automatically.

Here’s an example **`actions.json`** with a couple of typical scenarios:

```json
[
  {
    "type": "sync",
    "source_playlist_id": "37i9dQZF1DX8FwnYE6PRvL",
    "target_playlist_id": "37i9dQZF1DX2TRYkJECvfB",
    "avoid_duplicates": true
  },
  {
    "type": "archive",
    "source_playlist_id": "37i9dQZF1DX8FwnYE6PRvL",
    "avoid_duplicates": true,
    "timeBetweenActInSeconds": 86400
  }
]
```

**How to find Spotify Playlist IDs:** You can get the playlist ID from the Spotify app or web URL. For example, in a Spotify playlist link like `https://open.spotify.com/playlist/37i9dQZF1DX2TRYkJECvfB`, the string after `/playlist/` (here `37i9dQZF1DX2TRYkJECvfB`) is the playlist ID.

Once you’ve created your `actions.json` file with the actions you want, place it in the working directory where you will run the scheduler (or in the project directory if running from source). By default, the scheduler will look for a file named **`actions.json`** in its directory. Ensure the JSON file is valid (structure and quotes, etc.); the application will parse this and run the specified sync actions.

### 3. Validation Actions
Before running the scheduler, you can validate your actions.json configuration file using the provided validation script.

Run the following command:

```bash
python scripts/actionValidation.py
```
This will parse your actions.json and check for:

* ✅ JSON syntax validity
* ✅ Required fields (type, target_playlist_id, etc.)
* ✅ Duplicate or conflicting actions
* ✅ Unsupported action types

If the script prints no errors, your config is valid! Otherwise, it will report issues you should fix before running the scheduler.

👉 **Recommendation**: Always validate your actions after editing actions.json to catch mistakes early.

## Running the Scheduler

With your environment variables and actions configured, you are ready to run the SpotifyActionScheduler.

### On-Demand Run (Manual Execution)

If you installed via pip or from source on your local machine, you can run the sync process with a single command. Make sure you are in the project directory (where your `.env` and `actions.json` live) or have set the environment variables in your shell:

* **Using the CLI command:**
  After installing the package you can run all configured actions once with:

  ```bash
  spotify-actions run-once
  ```

  This executes the scheduler’s main routine and processes the actions from your `actions.json`.

* **Using the provided module (source install):**
  If running from the cloned source you can invoke the on‑demand handler directly:

  ```bash
  python -m service.onDemandHandler
  ```

  This loads your config and processes all actions once.


When you run the scheduler, you’ll see logs in the console for each action, such as fetching tracks from the source, checking for duplicates, and adding missing tracks to the target. On the first run, it will prompt you to authorize the Spotify API access (open a browser window). After authorization, it will begin syncing. Subsequent runs should use the cached token and proceed without prompts.

### Scheduled Runs (Cron or Task Scheduler)

The project includes a small scheduler based on the `schedule` library. You can let it run continuously or invoke it via an external scheduler such as cron or the Windows Task Scheduler.

**Example (cron on Linux):** to run the sync every hour, add a cron entry by running `crontab -e` and adding a line like:

```
0 * * * * cd /path/to/your/project && /usr/bin/env bash -c 'source .env && spotify-actions schedule'
```

This will change directory to your project and run the scheduler on the hour, every hour. Make sure to adjust the path to your project and Python. We source the `.env` in the command so that the environment variables (Client ID/Secret/etc.) are loaded in the cron context.

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
