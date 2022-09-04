import pandas as pd
import importlib
import json
from functools import partial
import warnings
from datetime import datetime


def create_script_id(script_type, script_name, script_params):
    params_str = json.dumps(script_params)
    script_id = f"{script_type}+{script_name}+{params_str}"
    return script_id


def create_script_data_config(script_name, script_params):
    module = importlib.import_module(f"scripts.patterns.{script_name}.script")
    create_data_config_func = getattr(module, "create_data_config")
    data_config = create_data_config_func(script_params)
    return data_config


def parse_script_id(script_id):
    script_type, script_name, params_str = script_id.split("+")
    params = json.loads(params_str)
    # params = dict(parse.parse_qsl(params_str))
    # convert to int, float if detected:
    for k, v in params.items():
        try:
            params[k] = int(v)
            continue
        except:
            pass
        try:
            params[k] = float(v)
        except:
            pass
    return script_type, script_name, params


class IndicatorSchemaBuilder(object):
    def __init__(self, config_list):
        self.config_list = config_list
        self.schema = {}
        for config in self.config_list:
            s = self.get_schema_of_indicator(
                indicator_type=config["type"],
                indicator_name=config["name"],
                indicator_params=config["params"]
            )
            self.schema.update(s)

    def get_indicator_data_config(self, indicator_type, indicator_params):
        indicator_module = importlib.import_module(f"scripts.indicators.{indicator_type}.script")
        create_data_config_func = getattr(indicator_module, "create_data_config")
        indicator_data_config = create_data_config_func(indicator_params)
        return indicator_data_config

    def get_schema_of_indicator(self, indicator_type, indicator_name, indicator_params):
        schema = {}
        indicator_id = create_script_id(
            script_type=indicator_type,
            script_name=indicator_name,
            script_params=indicator_params
        )
        indicator_data_config = self.get_indicator_data_config(
            indicator_type=indicator_type,
            indicator_params=indicator_params
        )
        if "queries" not in indicator_data_config and "indicators" not in indicator_data_config:
            return schema
        else:
            schema[indicator_id] = {}

        if "queries" in indicator_data_config:
            for c in indicator_data_config["queries"]:
                query_type = c["type"]
                query_params = c["params"]
                query_id = create_script_id(
                    script_type=query_type,
                    script_name=query_type,
                    script_params=query_params
                )
                if "queries" not in schema[indicator_id]:
                    schema[indicator_id].update({"queries": []})
                schema[indicator_id]["queries"].append(query_id)

        if "indicators" in indicator_data_config:
            for c in indicator_data_config["indicators"]:
                child_indicator_type = c["type"]
                child_indicator_name = c["name"]
                child_indicator_params = c["params"]
                child_indicator_id = create_script_id(
                    script_type=child_indicator_type,
                    script_name=child_indicator_name,
                    script_params=child_indicator_params
                )
                if "indicators" not in schema[indicator_id]:
                    schema[indicator_id].update({"indicators": []})
                schema[indicator_id]["indicators"].append(child_indicator_id)

            for c in indicator_data_config["indicators"]:
                child_indicator_type = c["type"]
                child_indicator_name = c["name"]
                child_indicator_params = c["params"]
                s = self.get_schema_of_indicator(
                    indicator_type=child_indicator_type,
                    indicator_name=child_indicator_name,
                    indicator_params=child_indicator_params
                )
                schema.update(s)
        return schema

    def get(self):
        return self.schema


class QuerySchemaBuilder(object):
    def __init__(self, indicator_schema):
        self.indicator_schema = indicator_schema
        self.schema = []
        for indicator_id in self.indicator_schema:
            if "queries" in self.indicator_schema[indicator_id]:
                for q in self.indicator_schema[indicator_id]["queries"]:
                    self.schema.append(q)

    def get(self):
        return self.schema


class QueryDataMapBuilder(object):
    def __init__(self, query_data):
        self.query_data = query_data
        self.query_data_map = {}

    def build(self):
        # populate query_data_map:
        for query_id in self.query_data:
            self.query_data_map[query_id] = self.query_data[query_id]

    def get(self):
        return self.query_data_map


class IndicatorDataMapBuilder(object):
    def __init__(self, indicator_schema, query_data_map):
        self.indicator_schema = indicator_schema
        self.query_data_map = query_data_map
        self.indicator_data_map = {}

    def queries_of_indicator(self, i_id):
        if "queries" in self.indicator_schema[i_id]:
            query_ids = self.indicator_schema[i_id]["queries"]
        else:
            query_ids = []
        return query_ids

    def indicators_of_indicator(self, i_id):
        if "indicators" in self.indicator_schema[i_id]:
            indicator_ids = self.indicator_schema[i_id]["indicators"]
        else:
            indicator_ids = []
        return indicator_ids

    def is_full(self):
        for indicator_id in self.indicator_schema:
            if indicator_id not in self.indicator_data_map:
                return False
        return True

    def build(self):

        while True:

            if self.is_full():
                break

            for indicator_id in self.indicator_schema:
                indicator_query_ids = self.queries_of_indicator(indicator_id)
                indicator_indicator_ids = self.indicators_of_indicator(indicator_id)

                # create "data" object for (calculate function):
                calc_indicator = True
                data = {}

                # data has "queries" and "indicators" fields:
                for q_id in indicator_query_ids:
                    if "queries" not in data:
                        data["queries"] = {}
                    _, q_name, _ = parse_script_id(q_id)
                    if q_id in self.query_data_map:
                        data["queries"][q_name] = self.query_data_map[q_id]
                    else:
                        raise Exception(f"Error: Missing <q_id> = {q_id} from <query_data_map>")

                for i_id in indicator_indicator_ids:
                    if "indicators" not in data:
                        data["indicators"] = {}

                    if i_id in self.indicator_data_map:
                        _, i_name, _ = parse_script_id(i_id)
                        data["indicators"][i_name] = self.indicator_data_map[i_id]
                    else:
                        calc_indicator = False

                if calc_indicator:
                    indicator_type, indicator_name, indicator_params = parse_script_id(indicator_id)
                    indicator_module = importlib.import_module(f"scripts.indicators.{indicator_type}.script")
                    calculate_func = getattr(indicator_module, "calculate")
                    indicator_data = calculate_func(data, indicator_params)
                    self.indicator_data_map[indicator_id] = indicator_data

    def get(self):
        return self.indicator_data_map


def create_indicators_dataframe(indicator_data_map):
    df = pd.DataFrame({})
    for indicator_id in indicator_data_map:
        _, indicator_name, _ = parse_script_id(indicator_id)
        indicator_data = indicator_data_map[indicator_id]
        df_ind = pd.DataFrame(indicator_data)
        df_ind.rename(columns={"value": indicator_name}, inplace=True)
        if len(df) == 0:
            df = df_ind
        else:
            df = pd.merge(df, df_ind, how="outer", on="timestamp")
        df.sort_values(by="timestamp", ascending=True, inplace=True, ignore_index=True)
    return df


class QueryDataGenerator(object):
    def __init__(self, coin_ids, query_ids):
        self.coin_ids = coin_ids
        self.query_ids = query_ids

    def generate(self):
        for coin_id in self.coin_ids:
            responses, response_map = self.get_responses(coin_id)
            yield coin_id, responses, response_map

    def get_responses(self, coin_id):
        responses = []
        response_map = {}
        for res_idx, query_id in enumerate(self.query_ids):
            query_type, query_name, query_params = parse_script_id(query_id)
            query_module = importlib.import_module(f"scripts.queries.{query_type}.script")
            get_data_func = partial(getattr(query_module, "get_data"), coin_id, query_params)
            res = get_data_func()
            responses.append(res)
            response_map[query_id] = res_idx
        return responses, response_map


def get_indicators(coin_id, config_list):
    indicator_schema_builder = IndicatorSchemaBuilder(config_list=config_list)
    indicator_schema = indicator_schema_builder.get()
    query_schema_builder = QuerySchemaBuilder(indicator_schema=indicator_schema)
    query_schema = query_schema_builder.get()  # = [query_1_id, ..., query_n_id]
    query_data_generator = QueryDataGenerator([coin_id], query_schema)

    coin_id, msearch_responses, response_map = next(query_data_generator.generate())

    query_data = {}
    for res_idx, query_id in enumerate(response_map):
        query_data[query_id] = msearch_responses[int(res_idx)]

    query_data_map_builder = QueryDataMapBuilder(query_data)
    query_data_map_builder.build()
    query_data_map = query_data_map_builder.get()

    indicator_data_map_builder = IndicatorDataMapBuilder(indicator_schema, query_data_map)

    indicator_data_map_builder.build()
    indicator_data_map = indicator_data_map_builder.get()

    df_indicators = create_indicators_dataframe(indicator_data_map)
    output = df_indicators.to_dict("records")

    return output


def get_signal_func(pattern_name):
    pattern_module = importlib.import_module(f"scripts.patterns.{pattern_name}.script")
    signal_func = getattr(pattern_module, "signal")
    return signal_func


def get_process_chart_data_func(pattern_name):
    pattern_module = importlib.import_module(f"scripts.patterns.{pattern_name}.script")
    try:
        process_chart_data_func = getattr(pattern_module, "process_chart_data")
        return process_chart_data_func
    except:
        return None


def get_patterns(coin_id, pattern_name, pattern_params, chart_window_size):
    data_config = create_script_data_config(pattern_name, pattern_params)
    indicators_records = get_indicators(coin_id, data_config["indicators"])

    signal_func = get_signal_func(pattern_name)
    process_chart_data_func = get_process_chart_data_func(pattern_name)

    for t in reversed(range(len(indicators_records))):  # note: most recent pattern first

        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            try:
                is_signal, signal_meta = signal_func(t, indicators_records, pattern_params)
            except Exception as e:
                print(f"[ERROR] Error calling signal function. Got {str(e)} => return is_signal = False")
                is_signal = False
                signal_meta = None

        if is_signal:
            lb_window = max(0, t - chart_window_size)
            ub_window = min(t + chart_window_size + 1, len(indicators_records))
            chart_data = indicators_records[lb_window: ub_window]
            if process_chart_data_func is not None:
                chart_data = process_chart_data_func(chart_data, signal_meta)

            signal_period = t
            signal_timestamp = indicators_records[t]["timestamp"]
            signal_data = {
                "coin_id": coin_id,
                "timestamp": signal_timestamp,
                "signal_period": signal_period,
                "signal_indicators": indicators_records[t],
                "signal_meta": signal_meta,
                "date": datetime.utcfromtimestamp(signal_timestamp).strftime("%Y-%m-%d %H:%M:%S UTC"),
            }

            yield signal_data, chart_data
