
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from most_agent.db.models import (
    EpisodeDetails,
    MediaItem,
    MovieDetails,
    SeriesDetails,
)
from most_agent.db.session import SessionFactory


def update_fields(instance, values: dict) -> bool:
    """Update only fields whose values have changed."""
    changed = False

    for field, value in values.items():
        if getattr(instance, field) != value:
            setattr(instance, field, value)
            changed = True

    return changed


def get_or_create_media(
    session: Session,
    imdb_id: str,
    media_type: str,
    values: dict,
) -> tuple[MediaItem, bool, bool]:
    """Find an existing media item or create a new one."""

    media = session.scalar(
        select(MediaItem).where(MediaItem.imdb_id == imdb_id)
    )

    if media is None:
        media = MediaItem(
            imdb_id=imdb_id,
            media_type=media_type,
            **values,
        )
        session.add(media)

        return media, True, False

    if media.media_type != media_type:
        raise ValueError(
            f"Media type mismatch for {imdb_id}: "
            f"expected {media_type}, got {media.media_type}"
        )

    changed = update_fields(media, values)

    return media, False, changed


def seed_record(
    session: Session,
    report: dict,
    *,
    imdb_id: str,
    media_type: str,
    media_values: dict,
    details_relationship: str,
    details_class: type,
    details_values: dict,
) -> MediaItem:
    """Create or update a media item and its details."""

    media, created, media_changed = get_or_create_media(
        session,
        imdb_id,
        media_type,
        media_values,
    )

    details = getattr(media, details_relationship)

    if details is None:
        details_class(
            media=media,
            **details_values,
        )
        details_changed = True
    else:
        details_changed = update_fields(
            details,
            details_values,
        )

    if created:
        status = "created"
    elif media_changed or details_changed:
        status = "updated"
    else:
        status = "unchanged"

    report[media_type][status] += 1

    return media


def main() -> None:
    report = {
        media_type: {
            "created": 0,
            "updated": 0,
            "unchanged": 0,
        }
        for media_type in ("movie", "series", "episode")
    }

    with SessionFactory.begin() as session:

        # ---------------------------------------
        # 1. Movies
        # ---------------------------------------

        seed_record(
            session,
            report,
            imdb_id="mock-movie-001",
            media_type="movie",
            media_values={
                "name": "The Last Signal",
                "description": (
                    "A radio astronomer discovers a mysterious "
                    "signal coming from a distant star."
                ),
                "poster": None,
                "release_year": 2021,
                "release_date": None,
                "imdb_url": None,
                "imdb_rating": Decimal("7.8"),
                "genres": ["Science Fiction", "Thriller"],
                "countries": ["United States"],
            },
            details_relationship="movie_details",
            details_class=MovieDetails,
            details_values={
                "runtime_minutes": 116,
            },
        )

        seed_record(
            session,
            report,
            imdb_id="mock-movie-002",
            media_type="movie",
            media_values={
                "name": "Paper Kingdom",
                "description": (
                    "A young journalist uncovers a political "
                    "conspiracy hidden inside an old newspaper."
                ),
                "poster": None,
                "release_year": 2023,
                "release_date": None,
                "imdb_url": None,
                "imdb_rating": Decimal("8.1"),
                "genres": ["Drama", "Mystery"],
                "countries": ["United Kingdom"],
            },
            details_relationship="movie_details",
            details_class=MovieDetails,
            details_values={
                "runtime_minutes": 104,
            },
        )

        # ---------------------------------------
        # 2. Series
        # ---------------------------------------

        series = seed_record(
            session,
            report,
            imdb_id="mock-series-001",
            media_type="series",
            media_values={
                "name": "Northbound",
                "description": (
                    "A group of strangers travel across a "
                    "frozen country after a global blackout."
                ),
                "poster": None,
                "release_year": 2022,
                "release_date": None,
                "imdb_url": None,
                "imdb_rating": Decimal("8.5"),
                "genres": ["Drama", "Adventure", "Mystery"],
                "countries": ["Canada"],
            },
            details_relationship="series_details",
            details_class=SeriesDetails,
            details_values={
                "typical_episode_runtime_minutes": 42,
                "season_count": 1,
                "episode_count": 2,
            },
        )

        series_details = series.series_details
        assert series_details is not None

        # ---------------------------------------
        # 3. Episodes
        # ---------------------------------------

        seed_record(
            session,
            report,
            imdb_id="mock-episode-001",
            media_type="episode",
            media_values={
                "name": "The Crossing",
                "description": (
                    "The survivors begin their journey north "
                    "and discover an abandoned station."
                ),
                "poster": None,
                "release_year": 2022,
                "release_date": None,
                "imdb_url": None,
                "imdb_rating": Decimal("8.2"),
                "genres": ["Drama", "Mystery"],
                "countries": ["Canada"],
            },
            details_relationship="episode_details",
            details_class=EpisodeDetails,
            details_values={
                "series": series_details,
                "season_number": 1,
                "episode_number": 1,
            },
        )

        seed_record(
            session,
            report,
            imdb_id="mock-episode-002",
            media_type="episode",
            media_values={
                "name": "Night Train",
                "description": (
                    "The group finds a working train, but "
                    "something is waiting inside."
                ),
                "poster": None,
                "release_year": 2022,
                "release_date": None,
                "imdb_url": None,
                "imdb_rating": Decimal("8.7"),
                "genres": ["Drama", "Thriller"],
                "countries": ["Canada"],
            },
            details_relationship="episode_details",
            details_class=EpisodeDetails,
            details_values={
                "series": series_details,
                "season_number": 1,
                "episode_number": 2,
            },
        )

    # ---------------------------------------
    # 4. Import report
    # ---------------------------------------

    print("\n========== MOCK MEDIA SEED REPORT ==========\n")

    for media_type, counts in report.items():
        total = sum(counts.values())

        print(f"{media_type.title()}: {total}")
        print(f"  Created:   {counts['created']}")
        print(f"  Updated:   {counts['updated']}")
        print(f"  Unchanged: {counts['unchanged']}")

    total_records = sum(
        sum(counts.values())
        for counts in report.values()
    )

    print("\n--------------------------------------------")
    print(f"Total media records processed: {total_records}")
    print("Seed completed successfully!")
    print("============================================")


if __name__ == "__main__":
    main()
