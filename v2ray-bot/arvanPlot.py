import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from datetime import datetime
from dateutil import relativedelta
import pytz

sites_color = {
    'playstation': '#ffcc00',
    'wikipedia': '#ab00ff',
    'bing': '#ff27b8',
    'google': '#ff6964',
    'github': '#ce0000',
    'aparat': '#15fdef',
    'filimo': '#2785ff',
    'digikala': '#08cf29'
}


class RadarPlot:

    def __init__(self, data, start_time=None):
        self._start_time = start_time
        if not self._start_time:
            self._start_time = datetime.now(tz=pytz.timezone('Asia/Tehran')) - relativedelta.relativedelta(hours=6)

        self.datacenter_names = []
        self.site_values = []
        for site in data:
            self.datacenter_names.append(site[0].replace('_', ' '))
            self.site_values.extend([list(site[1].values())])

        self.site_names = [[values for values in data[0][1].keys()]] * len(self.datacenter_names)



    def make_plot_1(self):
        """
        heavy and detailful plot
        """
        num_plots = len(self.site_names)

        with plt.style.context('dark_background'):
            fig, axes = plt.subplots(num_plots, 1, figsize=(15, 2 * num_plots), squeeze=False)
            for i in range(num_plots):

                ax = axes[i, 0]
                ax.set_ylabel(self.datacenter_names[i])

                max_length = max(len(arr) for arr in self.site_values[i])

                bottom = np.zeros(max_length)
                colors = [sites_color[color] for color in self.site_names[0]]

                for j, dc in enumerate(self.site_names[i]):
                    current_arr = self.site_values[i][j]
                    current_arr += [0] * (max_length - len(current_arr))
                    ax.bar(range(max_length), current_arr, bottom=bottom, label=dc, color=colors[j])
                    bottom += current_arr

                if i == num_plots - 1:
                    np_range = np.arange(0, max_length, 20)
                    minute = int(30 / len(np_range))
                    column_date = [self._start_time]

                    for state in range(len(np_range) - 1):
                        column_date.append((column_date[-1] + relativedelta.relativedelta(minutes=minute)))

                    ax.set_xticks(np_range)
                    ax.set_xticklabels([column.strftime('%H:%M') for column in column_date])
                    ax.legend(loc='upper right', bbox_to_anchor=(1.05, 1))

                else:
                    ax.set_xticks([])

                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

            plt.tight_layout()
            byte = BytesIO()
            plt.savefig('o.png')
            fig.savefig(byte, format='png')
            plt.close(fig)
            byte.seek(0)
            # plt.show()
            return byte.getvalue()


    def make_plot_2(self):
        """light"""
        ziped_data = [list(zip(*values)) for values in self.site_values]
        avg_data = [[round(sum(group) / len(group), 2) for group in ziped] for ziped in ziped_data]

        max_length = max(len(data) for data in avg_data)
        padded_data = [np.pad(data, (0, max_length - len(data)), 'constant', constant_values=np.nan) for data in
                       avg_data]


        x_values = list(range(max_length))

        num_plots = len(padded_data)
        num_cols = 2
        num_rows = (num_plots + num_cols - 1) // num_cols

        fig, axs = plt.subplots(num_rows, num_cols, figsize=(12, 2 * num_rows))

        for i, y in enumerate(padded_data):
            row = i // num_cols
            col = i % num_cols
            ax = axs[row, col]
            ax.plot(x_values, y)
            ax.set_title(self.datacenter_names[i])
            ax.set_ylim([0, 1])

            if i == num_plots - 2 or i == num_plots - 1:
                np_range = np.arange(0, max_length, 20)
                minute = int(380 / len(np_range))
                column_date = [self._start_time]

                for state in range(len(np_range) - 1):
                    column_date.append((column_date[-1] + relativedelta.relativedelta(minutes=minute)))

                ax.set_xticks(np_range)
                ax.set_xticklabels([column.strftime('%H:%M') for column in column_date], rotation='vertical')

            else:
                ax.set_xticks([])

        plt.subplots_adjust(hspace=0.5)
        plt.tight_layout()
        byte = BytesIO()
        plt.savefig('o.png')
        fig.savefig(byte, format='png')
        plt.close(fig)
        byte.seek(0)
        # plt.show()
        return byte.getvalue()