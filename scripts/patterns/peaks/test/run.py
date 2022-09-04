from scripts.utils import get_patterns
import os
import chart


def main():
    test_dir = os.path.dirname(__file__)
    plots_dir = f"{test_dir}/plots"
    os.makedirs(plots_dir, exist_ok=True)
    coin_id = "1"

    chart_config = [
        {
            "indicator": "price_close",
            "plot": 0,
            "axis": 0,
            "type": "line",
            "settings": {
                "color": "purple"
            }
        },
        {
            "indicator": "price_peaks",
            "plot": 0,
            "axis": 0,
            "type": "scatter",
            "settings": {
                "color": "red"
            }
        }
    ]

    for signal_data, chart_data in get_patterns(
        coin_id=coin_id,
        pattern_name="peaks",
        pattern_params={
            "interval": "4h",
            "peak_lookback": 4,
            "peak_lookahead": 4,
            "sdev_boundary": 1,
            "sdev_length": 30
        },
        chart_window_size=30
    ):
        signal_date = signal_data["date"]
        fig_path = f"{plots_dir}/coin_{coin_id}_date_{signal_date}.png"
        fig = chart.Figure(
            title=f"Coin: {coin_id} Date: {signal_data['date']}",
            chart_data=chart_data,
            chart_config=chart_config,
            save_path=fig_path
        )
        fig.create()
        print(f"Created {fig_path}.")


if __name__ == "__main__":
    main()
