import pandas as pd


def get_data(coin_id, params):
    data_path = f"data/{params['interval']}/price_close/coin_{coin_id}.csv"
    df = pd.read_csv(data_path)
    data = df.to_dict("records")
    return data

