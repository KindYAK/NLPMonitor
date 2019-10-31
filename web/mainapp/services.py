import datetime
from scipy.signal import firwin, filtfilt


def batch_qs(qs, batch_size=1000):
    total = qs.count()
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        yield qs[start:end]


def date_generator(date_start, date_finish):
    while date_start <= date_finish:
        yield date_start
        date_start = date_start + datetime.timedelta(days=1)


# Band-pass fir-filter
# f1 - начальная пропускная граница; f1 in (0,1]
# f2 - конечная пропускная граница; f2 in (0,1]
# fs - частота дискретизации сигнала (частота с которой производились дискретные выборки сигнала)
# N - порядок фильтра (чем больше значение тем более гладкой получается фильтрация; с увеличением N увеличивается и время вычисления)
# N должно быть положительным нечётным числом
def filter_coefficients(f1, f2, fs, N):
    if N % 2 == 0:
        N += 1
    nyq = 0.5 * fs  # Половинная частота (частота Найквиста)
    return firwin(N, [f1 * nyq, f2 * nyq], scale=True, nyq=0.5 * fs, pass_zero=False)


def apply_fir_filter(time_series, granularity):
    year_length = 365.259
    if granularity == "1d":
        fs = year_length / 365
    elif granularity == "1w":
        # Мы получаем одну выборку сигнала в неделю.
        # Соответственно частота дискретизации для данного сигнала: [число дней в году]/7
        fs = year_length / 7
    elif granularity == "1M":
        fs = year_length / 30
    elif granularity == "1q":
        fs = year_length / 90
    elif granularity == "1y":
        fs = year_length / 1
    else:
        raise Exception("Granularity not implemented")

    # FILTER SETTINGS !!!
    f1, f2 = 0.0001, 0.01  # Band-pass frequencies [Hz]
    N = 20  # Length of the filter (number of coefficients)
    coefficients = filter_coefficients(f1, f2, fs, N)

    # Делаем фильтрацию
    filtered_data = filtfilt(coefficients, 1.0, time_series)
    return filtered_data
