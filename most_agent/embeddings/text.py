
from most_agent.db.models import MediaItem


def _clean_text(value: str | None) -> str | None:
    """Normalize whitespace and ignore empty values."""
    if value is None:
        return None

    value = " ".join(value.split())

    return value or None


def _format_list(values: list[str] | None) -> str | None:
    """Normalize, deduplicate, and sort list values."""
    if not values:
        return None

    cleaned = {
        cleaned_value
        for value in values
        if (cleaned_value := _clean_text(value)) is not None
    }

    if not cleaned:
        return None

    return ", ".join(sorted(cleaned, key=str.casefold))


def build_search_text(media: MediaItem) -> str:
    """
    Build consistent search text for movies, series, and episodes.
    """

    if media.media_type not in ("movie", "series", "episode"):
        raise ValueError(
            f"Unsupported media type: {media.media_type}"
        )

    name = _clean_text(media.name)

    if name is None:
        raise ValueError("Media name cannot be empty")

    lines = [
        f"title: {name}",
        f"media type: {media.media_type}",
    ]

    # Common media information
    description = _clean_text(media.description)

    if description:
        lines.append(f"description: {description}")

    if media.release_year is not None:
        lines.append(f"release year: {media.release_year}")

    elif media.release_date is not None:
        lines.append(
            f"release date: {media.release_date.isoformat()}"
        )

    genres = _format_list(media.genres)

    if genres:
        lines.append(f"genres: {genres}")

    countries = _format_list(media.countries)

    if countries:
        lines.append(f"countries: {countries}")

    # Movie-specific validation
    if media.media_type == "movie":
        if media.movie_details is None:
            raise ValueError(
                f"MovieDetails missing for {media.imdb_id}"
            )

    # Series-specific information
    elif media.media_type == "series":
        details = media.series_details

        if details is None:
            raise ValueError(
                f"SeriesDetails missing for {media.imdb_id}"
            )

        if details.end_year is not None:
            lines.append(f"end year: {details.end_year}")

        elif details.end_date is not None:
            lines.append(
                f"end date: {details.end_date.isoformat()}"
            )

    # Episode-specific information
    elif media.media_type == "episode":
        details = media.episode_details

        if details is None:
            raise ValueError(
                f"EpisodeDetails missing for {media.imdb_id}"
            )

        series_media = details.series.media

        lines.append(f"series: {series_media.name}")

        if details.season_number is not None:
            lines.append(
                f"season number: {details.season_number}"
            )

        if details.episode_number is not None:
            lines.append(
                f"episode number: {details.episode_number}"
            )

    return "\n".join(lines)
