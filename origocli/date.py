from datetime import datetime, date

DATE_SHORT_FORMAT = "%Y-%m-%d"
DATE_METADATA_EDITION_FORMAT = "%Y%m%dT%H%M%S"


def date_add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    See: https://stackoverflow.com/questions/15741618/add-one-year-in-current-date-python
    """
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))


def date_now():
    return datetime.now()
