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


def ascend_signal_to_zero(signal):
    signal_min = min(signal)
    if signal_min < 0:
        signal = [s - signal_min for s in signal]
    return signal


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


def apply_fir_filter(time_series, granularity, allow_negatives=False):
    if not time_series:
        return time_series
    time_series = [x if x else 0 for x in time_series]
    year_length = 365.259
    if granularity == "1d":
        fs = year_length / 365
        f1, f2 = 0.000001, 0.1  # Band-pass frequencies [Hz percentiles]
        filter_length_by_signal_length = min(int(len(time_series) * 0.2), 91)
    elif granularity == "1w":
        fs = year_length / 7
        f1, f2 = 0.000001, 0.33  # Band-pass frequencies [Hz percentiles]
        filter_length_by_signal_length = min(int(len(time_series) * 0.33), 27)
    elif granularity == "1M":
        fs = year_length / 30
        f1, f2 = 0.000001, 0.5  # Band-pass frequencies [Hz percentiles]
        filter_length_by_signal_length = min(int(len(time_series) * 0.5), 13)
    elif granularity == "1q":
        fs = year_length / 90
        f1, f2 = 0.000001, 0.9  # Band-pass frequencies [Hz percentiles]
        filter_length_by_signal_length = min(int(len(time_series) * 0.7), 7)
    elif granularity == "1y":
        fs = year_length / 1
        f1, f2 = 0.000001, 0.95  # Band-pass frequencies [Hz percentiles]
        filter_length_by_signal_length = min(int(len(time_series)), 5)
    else:
        raise Exception("Granularity not implemented")

    if filter_length_by_signal_length % 2 == 0:
        filter_length_by_signal_length += 1
    coefficients = filter_coefficients(f1, f2, fs, filter_length_by_signal_length)

    # Делаем фильтрацию
    filtered_data = filtfilt(coefficients, 1.0, time_series, method="gust")
    if not allow_negatives:
        filtered_data = ascend_signal_to_zero(filtered_data)
    return filtered_data


def unique_ize(list, key):
    seen = set()
    results = []
    for obj in list:
        if key(obj) not in seen:
            results.append(obj)
            seen.add(key(obj))
    return results


def get_user_group(user):
    group = (hasattr(user, "expert") and user.expert.group) or \
            (hasattr(user, "viewer") and user.viewer.group)
    return group
