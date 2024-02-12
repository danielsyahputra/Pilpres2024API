"""Timer utils module."""

import pyrootutils

ROOT = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git"],
    pythonpath=True,
    dotenv=True,
)

from datetime import datetime, time, timedelta, timezone

import src.utils.exceptions as exceptions


def now(utc: bool = False, str: bool = True) -> datetime:
    """
    Get current time in ISO format (YYYY-MM-DDTHH:MM:SS.mmmmmm)

    Args:
        utc (bool, optional): UTC time.
        str (bool, optional): Return as string.

    Returns:
        str: Current time.

    Examples:
        >>> t.now()
        2023-01-03T21:16:08.282540
        >>> t.now(utc=True)
        2023-01-03T14:16:08.282565+00:00
    """
    at_now = datetime.now().isoformat()
    if utc:
        at_now = datetime.now(timezone.utc).isoformat()
    if str:
        return at_now
    return datetime.fromisoformat(at_now)


def today() -> str:
    """
    Get current date in ISO format (YYYY-MM-DD).

    Returns:
        str: Current date.

    Examples:
        >>> t.today()
        2023-01-03
    """
    return datetime.now().strftime("%Y-%m-%d")


def elapsed(start: datetime, end: datetime = None) -> float:
    """
    Get elapsed time between two datetime objects.

    Args:
        start (datetime): start time
        end (datetime, optional): end time

    Returns:
        float: Elapsed time.

    Examples:
        >>> start = datetime.now()
        >>> end = start + timedelta(seconds=1)
        >>> t.elapsed(start, end)
        420.69
    """
    if not end:
        end = datetime.now()
    if not isinstance(start, datetime):
        start = datetime.fromisoformat(start)
    if not isinstance(end, datetime):
        end = datetime.fromisoformat(end)
    return round((end - start).total_seconds() * 1000, 2)


def is_valid_date(date: str) -> bool:
    """
    Check if date is valid.

    Args:
        date (str): date

    Returns:
        bool: True if date is valid.

    Examples:
        >>> t.is_valid_date("2023-01-03")
        True
        >>> t.is_valid_date("2023-01-32")
        False
    """
    try:
        date = datetime.strptime(str(date), "%Y-%m-%d")
        if date > datetime.now():
            return False
        return True
    except ValueError:
        return False


def is_valid_datetime(datetime_at: datetime) -> bool:
    """
    Check if datetime is valid.

    Args:
        datetime_at (str): datetime

    Returns:
        bool: True if datetime is valid.

    Examples:
        >>> t.is_valid_datetime("2023-01-03T21:16:08.282540")
        True
        >>> t.is_valid_datetime("2023-01-32T21:16:08.282540")
        False
    """
    try:
        datetime_at = datetime.strptime(str(datetime_at), "%Y-%m-%dT%H:%M:%S.%f")
        if datetime_at > datetime.now():
            return False
        return True
    except ValueError:
        return False


def get_date_range(start_date: datetime, end_date: datetime) -> list:
    """
    Get date range between start date and end date.

    Args:
        start_date (str): Start date in %Y-%m-%d format.
        end_date (str): End date in %Y-%m-%d format.

    Returns:
        list: List of dates between start date and end date.

    Examples:
        >>> timestamp = Timestamp()
        >>> timestamp.get_date_range("2022-12-11", "2022-12-13")
        ['2022-12-11', '2022-12-12', '2022-12-13']

    """
    date_range = []
    while start_date <= end_date:
        date_range.append(start_date.strftime("%Y-%m-%d"))
        start_date += timedelta(days=1)
    return date_range


def get_day(date: datetime) -> str:
    """
    Get day of the week.

    Args:
        date (datetime): Date.

    Returns:
        str: Day of the week.

    Examples:
        >>> t.get_day(datetime.now())
        'Wednesday'
    """
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")
    return date.strftime("%A")


def convert_sec_to_time(seconds: int) -> time:
    """
    Convert seconds to time.

    Args:
        seconds (int): Seconds.

    Returns:
        time: Time.

    Examples:
        >>> t.convert_sec_to_time(3600)
        '01:00:00'
    """
    if not isinstance(seconds, int):
        seconds = int(seconds)
    return time(
        hour=seconds // 3600, minute=(seconds % 3600) // 60, second=seconds % 60
    )


if __name__ == "__main__":
    """Debugging."""
    start_datetime = datetime.now()
    start = now()
    print(start_datetime, type(start_datetime))
    print(start, type(start))