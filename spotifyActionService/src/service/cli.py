import click

from .mainHandler import (
    do_archive,
    do_sync,
    do_sync_liked,
    run_actions_once,
    start_scheduled_actions,
)


@click.group(help="spotify-actions: manage your Spotify playlists from the CLI")
def cli() -> None:
    pass


@cli.command(help="Sync SOURCE_PLAYLIST_ID into TARGET_PLAYLIST_ID")
@click.argument("source_playlist_id")
@click.argument("target_playlist_id")
@click.option(
    "--no-duplicates/--allow-duplicates",
    default=True,
    help=(
        "Skip tracks already in target by default; use --allow-duplicates to disable."
    ),
)
def sync(
    source_playlist_id: str,
    target_playlist_id: str,
    no_duplicates: bool,
) -> None:
    do_sync(
        source_playlist_id,
        target_playlist_id,
        avoid_duplicates=no_duplicates,
    )


@cli.command(help="Archive from SOURCE to TARGET (or remove if TARGET is omitted)")
@click.argument("source_playlist_id")
@click.argument("target_playlist_id", required=False)
@click.option(
    "--days",
    "-d",
    type=int,
    default=30,
    show_default=True,
    help="Only archive tracks older than this many days",
)
@click.option(
    "--no-duplicates/--allow-duplicates",
    default=True,
    help="Skip tracks already in the target playlist",
)
@click.option(
    "--no-time-filter/--filter-time",
    default=True,
    help=("Archive tracks older than --days; use --no-time-filter to archive all."),
)
def archive(
    source_playlist_id: str,
    target_playlist_id: str | None,
    days: int,
    no_duplicates: bool,
    no_time_filter: bool,
) -> None:
    do_archive(
        source_playlist_id,
        target_playlist_id,
        days=days,
        avoid_duplicates=no_duplicates,
        filter_by_time=no_time_filter,
    )


@cli.command(
    "sync-liked",
    help="Sync tracks Liked in the last N hours into TARGET_PLAYLIST_ID",
)
@click.argument("target_playlist_id")
@click.option(
    "--hours",
    "-h",
    type=int,
    default=24,
    show_default=True,
    help="Only sync tracks liked within this many hours",
)
@click.option(
    "--no-duplicates/--allow-duplicates",
    default=True,
    help="Skip tracks already in the target playlist",
)
@click.option(
    "--max-tracks",
    type=int,
    default=500,
    show_default=True,
    help="Maximum number of liked tracks to scan",
)
def sync_liked(
    target_playlist_id: str,
    hours: int,
    no_duplicates: bool,
    max_tracks: int,
) -> None:
    do_sync_liked(
        target_playlist_id,
        hours=hours,
        avoid_duplicates=no_duplicates,
        max_tracks=max_tracks,
    )


@cli.command(
    "run-once",
    help="Process all actions one time (on-demand)",
)
def run_once() -> None:
    run_actions_once()


@cli.command(
    "schedule",
    help="Start the scheduler (runs indefinitely)",
)
def schedule() -> None:
    start_scheduled_actions()


if __name__ == "__main__":
    cli()
