# used the following: https://medium.com/@6berardi/how-to-create-a-smooth-bar-chart-race-with-python-ad2daf6510dc
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.animation as animation
import matplotlib.colors as mc
import colorsys
from random import randint
import re

df = pd.read_csv("corona_panel.csv")
#df = df.loc[df['Variable'] == 'confirmed']
#df = df[((df.countryregion != 'OECD - Total') & (df.countryregion != 'Non-OECD Economies') & (df.countryregion != 'World') & (
#            df.countryregion != 'Euro area (15 countries)'))]
df = df[['countryregion', 'days', 'confirmed']]

df = df.pivot(index='countryregion', columns='days', values='confirmed')
df = df.reset_index()

for p in range(3):
    i = 0
    while i < len(df.columns):
        try:
            a = np.array(df.iloc[:, i + 1])
            b = np.array(df.iloc[:, i + 2])
            c = (a + b) / 2
            df.insert(i + 2, str(df.iloc[:, i + 1].name) + '^' + str(len(df.columns)), c)
        except:
            print(f"\n  Interpolation No. {p + 1} done...")
        i += 2

df = pd.melt(df, id_vars='countryregion', var_name='days')

frames_list = df["days"].unique().tolist()
for i in range(10):
    frames_list.append(df['days'].iloc[-1])


def transform_color(color, amount=0.5):
    try:
        c = mc.cnames[color]
    except:
        c = color
        c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])


all_names = df['countryregion'].unique().tolist()
random_hex_colors = []
for i in range(len(all_names)):
    random_hex_colors.append('#' + '%06X' % randint(0, 0xFFFFFF))

rgb_colors = [transform_color(i, 1) for i in random_hex_colors]
rgb_colors_opacity = [rgb_colors[x] + (0.825,) for x in range(len(rgb_colors))]
rgb_colors_dark = [transform_color(i, 1.12) for i in random_hex_colors]

fig, ax = plt.subplots(figsize=(36, 20))

num_of_elements = 8


def draw_barchart(days):
    df_frame = df[df['days'].eq(days)].sort_values(by='value', ascending=True).tail(num_of_elements)
    ax.clear()

    normal_colors = dict(zip(df['countryregion'].unique(), rgb_colors_opacity))
    dark_colors = dict(zip(df['countryregion'].unique(), rgb_colors_dark))

    ax.barh(df_frame['countryregion'], df_frame['value'], color=[normal_colors[x] for x in df_frame['countryregion']], height=0.8,
            edgecolor=([dark_colors[x] for x in df_frame['countryregion']]), linewidth='6')

    dx = float(df_frame['value'].max()) / 200

    for i, (value, name) in enumerate(zip(df_frame['value'], df_frame['countryregion'])):
        ax.text(value + dx, i + (num_of_elements / 50), '    ' + name,
                size=36, weight='bold', ha='left', va='center', fontdict={'fontname': 'Trebuchet MS'})
        ax.text(value + dx, i - (num_of_elements / 50), f'    {value:,.0f}', size=36, ha='left', va='center')

    days_unit_displayed = re.sub(r'\^(.*)', r'', str(days))
    ax.text(1.0, 1.14, days_unit_displayed, transform=ax.transAxes, color='#666666',
            size=62, ha='right', weight='bold', fontdict={'fontname': 'Trebuchet MS'})
    ax.text(-0.005, 1.06, 'Confirmed Cases', transform=ax.transAxes, size=30, color='#666666')
    ax.text(-0.005, 1.14, 'COVID-19 Confirmed Cases by Country', transform=ax.transAxes,
            size=62, weight='bold', ha='left', fontdict={'fontname': 'Trebuchet MS'})

    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax.xaxis.set_ticks_position('top')
    ax.tick_params(axis='x', colors='#666666', labelsize=28)
    ax.set_yticks([])
    ax.set_axisbelow(True)
    ax.margins(0, 0.01)
    ax.grid(which='major', axis='x', linestyle='-')

    plt.locator_params(axis='x', tight=True, nbins=4)
    plt.box(False)
    plt.subplots_adjust(left=0.075, right=0.75, top=0.825, bottom=0.05, wspace=0.2, hspace=0.2)


animator = animation.FuncAnimation(fig, draw_barchart, frames=frames_list)
animator.save("COVID-19 Confirmed Cases.mp4", fps=20, bitrate=1800)
