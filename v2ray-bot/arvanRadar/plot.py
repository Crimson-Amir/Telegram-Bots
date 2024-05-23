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
            self._start_time = datetime.now(tz=pytz.timezone('Asia/Tehran')) - relativedelta.relativedelta(minutes=30)

        self.datacenter_names = []
        self.site_values = []
        for site in data:
            self.datacenter_names.append(site[0])
            self.site_values.extend([list(site[1].values())[:63]])

        self.site_names = [[values for values in data[0][1].keys()]] * len(self.datacenter_names)

    def make_plot(self):
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
            return byte.getvalue()
            # plt.show()

