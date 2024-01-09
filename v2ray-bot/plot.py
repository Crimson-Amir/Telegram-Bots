import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

def generate_chart(data):
    total_volume = sum(data)
    percentages = [(value / total_volume) * 100 for value in data]

    labels = ["Upload", "Download", "Remaining"]
    colors = ['#FF5E78', '#488bf7', '#758AA2']  # Custom color palette

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#f7f7f7')  # Background color for the entire figure

    wedges, texts = ax.pie(percentages, labels=None, autopct=None,
                           textprops=dict(color="w", fontsize=12, fontweight='bold'),
                           colors=colors, wedgeprops=dict(width=0.4, edgecolor='#c4c4c4'))

    centre_circle = plt.Circle((0, 0), 0.5, color='white', fc='white', linewidth=0.1)
    ax.add_artist(centre_circle)

    for wedge, label, percentage in zip(wedges, labels, percentages):
        angle = (wedge.theta2 - wedge.theta1) / 2.0 + wedge.theta1
        x = 0.68 * np.cos(np.radians(angle))
        y = 0.68 * np.sin(np.radians(angle))
        ax.text(x, y, f'{label}\n{percentage:.1f}%', ha='center', va='center', fontsize=15, color='#2b2b2b')

    remaining_percentage = (data[2] / total_volume) * 100
    info_text = f'Total Traffic:\n{100 - remaining_percentage:.2f}%\n{data[0] + data[1]}GB/{total_volume}GB'
    ax.text(0, 0, info_text, ha='center', va='center', fontsize=15, color='#414141',
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='white'))

    title_font = {'fontsize': 20, 'fontweight': 'bold', 'fontfamily': 'Arial'}
    ax.set_title("Traffic Chart of This Service", fontdict=title_font, y=.99, color='#414141')

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=80, bbox_inches='tight', facecolor=fig.get_facecolor())
    binary_data = buffer.getvalue()
    buffer.close()

    return binary_data

