import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

def generate_stylish_pie_chart_and_save():
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#f7f7f7')  # Background color for the entire figure

    data = [20, 30, 30]  # Values in percentage
    labels = ["Upload", "Download", "Remaining"]
    colors = ['#FF5E78', '#5E7F5E', '#758AA2']  # Custom color palette

    wedges, texts = ax.pie(data, labels=None, autopct=None,
                           textprops=dict(color="w", fontsize=12, fontweight='bold'),
                           colors=colors, wedgeprops=dict(width=0.4, edgecolor='#c4c4c4'))

    # Adding a circular border for a stylish look
    centre_circle = plt.Circle((0, 0), 0.6, color='white', fc='white', linewidth=0.1)
    ax.add_artist(centre_circle)

    # Placing consumption type and percentage within each section
    for wedge, label, percentage in zip(wedges, labels, data):
        angle = (wedge.theta2 - wedge.theta1) / 2.0 + wedge.theta1
        x = 0.68 * np.cos(np.radians(angle))
        y = 0.68 * np.sin(np.radians(angle))
        ax.text(x, y, f'{label}\n{percentage:.1f}%', ha='center', va='center', fontsize=15, color='#2b2b2b')

    # Additional information in the center
    total_volume = sum(data)
    info_text = f'Total Traffic:\n{total_volume}%\n100GB/200GB'
    ax.text(0, 0, info_text, ha='center', va='center', fontsize=15, color='#414141',
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='white'))

    title_font = {'fontsize': 20, 'fontweight': 'bold', 'fontfamily': 'Arial'}
    ax.set_title("Traffic Chart of This Service", fontdict=title_font, y=.99, color='#414141')

    plt.savefig('stylish_pie_chart.png', dpi=100, bbox_inches='tight', facecolor=fig.get_facecolor())

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor=fig.get_facecolor())
    binary_data = buffer.getvalue()
    buffer.close()

    return binary_data

# Call the function to generate the stylish pie chart and save it
generate_stylish_pie_chart_and_save()
