import math


def create_data_config(params):
    # import json
    # print("params: ", json.dumps(params, indent=4))
    return {
        "indicators": [
            {
                "type": "price_close",
                "name": "price_close",
                "params": {
                    "interval": params["interval"]
                }
            },
            {
                "type": "peaks",
                "name": "price_peaks",
                "params": {
                    "indicator_type": "price_close",
                    "indicator_name": "price_close",
                    "indicator_params": {
                        "interval": params["interval"]
                    },
                    "peak_lookback": params["peak_lookback"],
                    "peak_lookahead": params["peak_lookahead"],
                    "sdev_boundary": params["sdev_boundary"],
                    "sdev_length": params["sdev_length"]
                }
            }
        ]
    }


def signal(t, data, params):
    if math.isnan(data[t]["price_peaks"]):
        return False, None
    else:
        meta = {
            "signal_period": t,
            "signal_timestamp": int(data[t]["timestamp"])
        }
        return True, meta
