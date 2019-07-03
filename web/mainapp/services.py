import datetime


def batch_qs(qs, batch_size=1000):
    total = qs.count()
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        yield qs[start:end]


def date_generator(date_start, date_finish):
    while date_start <= date_finish:
        yield date_start
        date_start = date_start + datetime.timedelta(days=1)
