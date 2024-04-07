import datetime

import matplotlib.pyplot as plt
import io

def get_plot(data, period):
    # period = ['12-3', '3-6', '6-9', '9-00', '00-03', '03-06', '06-09', '09-12']
    # usage = [44, 53, 123, 4, 42, 64, 13, 4]
    period = data.keys()
    usage = data.values() or [0 for _ in range(0, len(period))]

    list_of_period_name = {
        'day': 'Hours',
        'week': 'Days',
        'month': 'Weeks',
        'year': 'Months'
    }

    fig, ax = plt.subplots(figsize=(9, 6))

    bars = ax.bar(period, usage, color='#3449eb', edgecolor='black', linewidth=0.5, alpha=0.8)

    for bar in bars:
        height = bar.get_height()
        ax.annotate('{}'.format(height),
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', color='black')

    background_color = '#F0F0F0'
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)

    font_dict = {'fontsize': 14, 'color': 'black'}
    plt.xlabel(list_of_period_name[period], **font_dict)
    plt.ylabel('Usage (MB)', **font_dict)

    # plt.title('Usage in the Last 24 Horse', fontsize=16, color='black')

    ax.tick_params(axis='y', labelsize=12, colors='black')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    # ax.spines['left'].set_visible(False)

    x_position = len(period) - 0.5
    y_position = max(usage)

    ax.text(x_position, y_position, 'Now', fontsize=12, color='black', ha='center')

    image_bytes = io.BytesIO()
    plt.savefig(image_bytes, format='png')
    image_bytes.seek(0)

    plt.close()
    return image_bytes


# get_plot(5)