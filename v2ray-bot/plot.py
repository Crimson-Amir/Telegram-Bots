import matplotlib.pyplot as plt
import io

def get_plot(data, period_):
    period = list(data.keys())
    usage = list(data.values()) or [0 for _ in range(0, len(period))]

    usage_type, date_format = 'MB', '{}'
    list_of_period_name = {
        'day': 'Hours',
        'week': 'Days',
        'month': 'Weeks',
        'year': 'Months'
    }

    if period_ in ('month', 'year'):
        usage_type, date_format = 'GB', '{:.2f}'
        usage = [u / 1024 for u in usage]

    fig, ax = plt.subplots(figsize=(9, 6))

    bars = ax.bar(period, usage, color='#3449eb', edgecolor='black', linewidth=0.5, alpha=0.8)

    for bar in bars:
        height = bar.get_height()
        if period_ == 'month':
            ax.annotate(date_format.format(height),
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', color='black', rotation=90)
        else:
            ax.annotate(date_format.format(height),
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', color='black')

    background_color = '#F0F0F0'
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)

    font_dict = {'fontsize': 14, 'color': 'black'}
    plt.xlabel(list_of_period_name[period_], **font_dict)
    ylabel_text = f'Usage ({usage_type})'
    plt.ylabel(ylabel_text, **font_dict)

    ax.tick_params(axis='y', labelsize=12, colors='black')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    if period_ == 'month':
        ax.set_xticks([i for i in range(len(period)) if i % 7 == 0])
        ax.set_xticklabels([period[i] for i in range(len(period)) if i % 7 == 0], ha='center', fontsize=10)

    image_bytes = io.BytesIO()
    plt.savefig(image_bytes, format='png')
    image_bytes.seek(0)
    plt.close()
    return image_bytes

