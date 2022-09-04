

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
    """
    format:
    {
        indicators: {
            ...
        },
        queries: {
            query_name_1: query_data_1
        }
    }
    """
    # todo: just get the data directly from here
    records = []
    price_close_records = data["queries"]["price_close"]
    for d in price_close_records:
        records.append({
            "timestamp": d["timestamp"],
            "value": d["price_close"]
        })
    return records


    records = []
    query_data = data["queries"]["price_close"]  # note: name of query is price_close
    # note: reversed because query returns in desc order
    for d in reversed(query_data["aggregations"]["resample"]["buckets"]):
        _source = d["close"]["hits"]["hits"][0]["_source"]
        records.append({
            "timestamp": _source["timestamp_close"],
            "value": _source["price_close"],
        })
    return records



