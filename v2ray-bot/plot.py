import datetime

import matplotlib.pyplot as plt
import io

def get_plot(data, period_):
    period = data.keys()
    usage = data.values() or [0 for _ in range(0, len(period))]

    list_of_period_name = {
        'day': 'Hours',
        'week': 'Days',
        'month': 'Weeks',
        'year': 'Months'
    }

    fig, ax = plt.subplots(figsize=(9, 6))

    bars = ax.bar(period, usage, color=f'#3449eb', edgecolor='black', linewidth=0.5, alpha=0.8)

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
    plt.xlabel(list_of_period_name[period_], **font_dict)
    plt.ylabel('Usage (MB)', **font_dict)

    ax.tick_params(axis='y', labelsize=12, colors='black')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)


    image_bytes = io.BytesIO()
    plt.savefig(image_bytes, format='png')
    image_bytes.seek(0)

    plt.close()
    return image_bytes
