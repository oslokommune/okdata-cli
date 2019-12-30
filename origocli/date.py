from datetime import datetime, date

DATE_SHORT_FORMAT = "%Y-%m-%d"
DATE_METADATA_EDITION_FORMAT = "%Y-%m-%dT%H:%M:%S+02:00"


def date_add_years(d, years):
    """
    Add N-year(s) to a current date object

    See: https://stackoverflow.com/questions/15741618/add-one-year-in-current-date-python
    """
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))


def date_now():
    return datetime.now()
