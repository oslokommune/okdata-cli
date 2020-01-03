from datetime import datetime

DATE_SHORT_FORMAT = "%Y-%m-%d"
DATE_METADATA_EDITION_FORMAT = "%Y-%m-%dT%H:%M:%S+02:00"


def date_now():
    return datetime.now()
