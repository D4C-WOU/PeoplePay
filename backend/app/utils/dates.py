from datetime import date, timedelta


def daterange(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def inclusive_days(start: date, end: date) -> int:
    return (end - start).days + 1
