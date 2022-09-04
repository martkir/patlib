from scripts.indicators.get import get_indicators
import pandas as pd
import os
import chart


def main():
    test_dir = os.path.dirname(__file__)
    indicator_records_md_path = f"{test_dir}/indicator_records.md"
    indicator_plot_path = f"{test_dir}/indicator_plot.png"

    indicator_records = get_indicators(
        coin_id="1",
        config_list=[
            {
                "type": "price_close",
                "name": "price_close",
                "params": {
                    "interval": "1h"
                }
            },
            {
                "type": "price_close",
                "name": "price_close_4h",
                "params": {
                    "interval": "4h"
                }
            }
        ]
    )
    df = pd.DataFrame(indicator_records)
    df.to_markdown(open(indicator_records_md_path, "w+"), index=False)
    print(f"Created {indicator_records_md_path}.")

    fig = chart.Figure(
        title="Price Close",
        chart_data=indicator_records[len(indicator_records) - 100:len(indicator_records)],
        chart_config=[
            {
                "indicator": "price_close",
                "plot": 0,
                "axis": 0,
                "type": "line",
                "settings": {
                    "color": "red"
                }
            },
            {
                "indicator": "price_close_4h",
                "plot": 0,
                "axis": 0,
                "type": "line",
                "settings": {
                    "color": "blue"
                }
            }
        ],
        save_path=indicator_plot_path
    )
    fig.create()
    print(f"Created {indicator_plot_path}.")


if __name__ == "__main__":
    main()

