

def create_data_config(params):
    return {
        "queries": [
            {
                "type": "price_close",
                "name": "price_close",
                "params": {
                    "interval": params["interval"]
                }
            }
        ]
    }


def calculate(data, params):
    records = []
    price_close_records = data["queries"]["price_close"]
    for d in price_close_records:
        records.append({
            "timestamp": d["timestamp"],
            "value": d["price_close"]
        })
    return records


