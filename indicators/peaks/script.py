import numpy as np


def create_data_config(params):
    return {
        "indicators": [
            {
                "type": params["indicator_type"],
                "name": params["indicator_name"],
                "params": params["indicator_params"]
            }
        ]
    }


def calculate(data, params):
    """
    format of `data`:
    {
        "indicators": {
            "indicator_name_1": [
                {
                    "timestamp": ...,
                    "value": ...
                }
            ],
            ...
        }
    }
    """

    output = []
    indicator_name = params["indicator_name"]
    series_records = data["indicators"][indicator_name]  # [{timestamp: ..., value: ...}]
    series_arr = np.array([r["value"] for r in series_records])
    for t in range(len(series_arr)):
        if is_peak(t, series_arr, **params):
            output.append({
                "timestamp": series_records[t]["timestamp"],
                "value": series_records[t]["value"]
            })
        else:
            output.append({
                "timestamp": series_records[t]["timestamp"],
                "value": None
            })
    return output


def is_peak(t, series_arr, sdev_length, sdev_boundary, peak_lookback, peak_lookahead, **kwargs):
    window_from = t - peak_lookback
    window_until = t + peak_lookahead
    sdev_until = t + peak_lookahead
    sdev_from = sdev_until - sdev_length

    if window_from < 0 or sdev_from < 0:
        return False
    # note: series like rsi have None values in the beginning
    if series_arr[window_from] is None or series_arr[sdev_from] is None:
        return False
    if window_until > len(series_arr) - 1:
        return False

    window = series_arr[window_from: window_until + 1]
    max_val = np.max(window)
    mid_val = series_arr[t]
    if mid_val != max_val:
        return False

    left_val = window[0]
    right_val = window[-1]
    # note: for more precision (less recall) let delta = min(...)
    delta = max(max_val - left_val, max_val - right_val)
    sdev = np.std(series_arr[sdev_from:sdev_until + 1])

    if delta > sdev_boundary * sdev:
        return True
    else:
        return False

