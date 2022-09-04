import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class Chart(object):
    def __init__(self, fig=None, ax=None):
        if fig is None:
            self.fig = plt.figure()
            _ = self.fig.add_subplot(1, 1, 1)
            fig_width = 1 * 8.5
            fig_height = 1 * 6.5
            self.fig.set_size_inches(fig_width, fig_height, forward=True)
        else:
            self.fig = fig
        if ax is None:
            self.ax = self.fig.axes[0]
        else:
            self.ax = ax

    def signal(self, x_vals, y_vals, color="magenta"):
        # ax = self.fig.axes[0]
        signal_timestamps = [x_vals[i] for i in range(len(x_vals)) if y_vals[i] == 1]
        self.ax.axvline(signal_timestamps, c=color, linewidth=4)

    def target(self, target_price, color="magenta"):
        # ax = self.fig.axes[0]
        self.ax.axhline([target_price], c=color, linewidth=4)

    def annotate(self, text, pos=0):
        # ax = self.fig.axes[0]
        xy = (0.75, 0.95 - pos * 0.05)
        self.ax.annotate(text, xy=xy, xycoords="axes fraction", color="magenta", fontsize=14)

    def bar(self, x_vals, y_vals, color="blue", alpha=1.0):
        # ax = self.fig.axes[0]
        # ax.clear()
        self.ax.bar(x_vals, y_vals, color=color, linewidth=0.2, alpha=alpha)
        self.ax.set_xticklabels([])
        self.ax.set_ylim(bottom=min(y_vals) - np.std(y_vals))

    def scatter(self, x_vals, y_vals, color="red", label=None):
        self.ax.scatter(x_vals, y_vals, color=color, marker="x", s=150, linewidth=0.8, label=label)
        self.ax.set_xticklabels([])
        self.ax.legend()

    def line(self, x_vals, y_vals, color="red", label=None):
        # ax = self.fig.axes[0]
        # ax.clear()
        self.ax.plot(x_vals, y_vals, color=color, marker=".", markersize=4, linewidth=0.2, label=label)
        self.ax.set_xticklabels([])
        self.ax.legend()
        # ax.set_ylim(bottom=min(y_vals))

    def hist(self, x_vals):
        # ax = self.fig.axes[0]
        self.ax.hist(x_vals, bins=100, alpha=0.5)
        self.ax.set_xticklabels([])

    @staticmethod
    def save_chart(save_path):
        plt.tight_layout()
        plt.subplots_adjust(hspace=0, wspace=0)
        plt.savefig(save_path)
        plt.close()


class Figure(object):
    def __init__(self, title, chart_data, chart_config, save_path):
        self.title = title
        self.chart_data = chart_data
        self.chart_config = chart_config
        self.num_plots = len(set([x["plot"] for x in chart_config]))
        self.save_path = save_path
        self.df_chart_data = pd.DataFrame(self.chart_data)

    def _get_color(self, indicator_config):
        try:
            color = indicator_config["settings"]["color"]
        except:
            color = "red"
        return color

    def create(self):
        num_cols = 1
        num_rows = self.num_plots
        fig, axs = plt.subplots(num_rows, num_cols)
        try:
            _ = len(axs)
        except:
            axs = [axs]
        fig_width = num_cols * 12.5
        fig_height = num_rows * 3.5
        fig.set_size_inches(fig_width, fig_height, forward=True)

        for c in self.chart_config:
            chart = Chart(fig=fig, ax=axs[c["plot"]])
            if c["type"] == "line":
                chart.line(
                    x_vals=self.df_chart_data.timestamp,
                    y_vals=self.df_chart_data[c["indicator"]],
                    color=self._get_color(c),
                    label=c["indicator"]
                )
            if c["type"] == "scatter":
                chart.scatter(
                    x_vals=self.df_chart_data.timestamp,
                    y_vals=self.df_chart_data[c["indicator"]],
                    color=self._get_color(c),
                    label=c["indicator"]
                )
            if c["type"] == "signal":
                chart.signal(x_vals=self.df_chart_data.timestamp, y_vals=self.df_chart_data[c["indicator"]], color=self._get_color(c))

        fig.suptitle(self.title, fontsize=11, y=0.94)
        plt.subplots_adjust(hspace=0.03, wspace=0.15)
        plt.savefig(self.save_path, bbox_inches='tight', pad_inches=0.25)
        plt.close()