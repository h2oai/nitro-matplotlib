import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import simple_websocket
from flask import Flask, request, send_from_directory

# ----- Nitro app -----

from h2o_nitro import View, web_directory
from h2o_nitro_matplotlib import matplotlib_plugin, matplotlib_box


# Entry point
def main(view: View):
    # Show each plot one by one
    view('## Hexbin with distributions', matplotlib_box(plot_hexbin()))
    view('## Conditional KDE', matplotlib_box(plot_kde()))
    view('## Ridge plots', matplotlib_box(plot_ridge()))
    view('## Cubehelix palettes', matplotlib_box(plot_cubehelix()))
    view('## Time Series Trellis', matplotlib_box(plot_trellis()))


# Nitro instance
nitro = View(
    main,
    title='Nitro + Seaborn',
    caption='A minimal example',
    plugins=[matplotlib_plugin()],  # Include the matplotlib plugin
)


# ----- Seaborn plotting routines -----

def plot_hexbin():
    # Source: https://seaborn.pydata.org/examples/hexbin_marginals.html

    sns.set_theme(style="ticks")

    rs = np.random.RandomState(11)
    x = rs.gamma(2, size=1000)
    y = -.5 * x + rs.normal(size=1000)

    sns.jointplot(x=x, y=y, kind="hex", color="#4CB391")
    return None


def plot_kde():
    # Source: https://seaborn.pydata.org/examples/multiple_conditional_kde.html

    sns.set_theme(style="whitegrid")

    # Load the diamonds dataset
    diamonds = sns.load_dataset("diamonds")

    # Plot the distribution of clarity ratings, conditional on carat
    sns.displot(
        data=diamonds,
        x="carat", hue="cut",
        kind="kde", height=6,
        multiple="fill", clip=(0, None),
        palette="ch:rot=-.25,hue=1,light=.75",
    )
    return None


def plot_ridge():
    # Source: https://seaborn.pydata.org/examples/kde_ridgeplot.html

    sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

    # Create the data
    rs = np.random.RandomState(1979)
    x = rs.randn(500)
    g = np.tile(list("ABCDEFGHIJ"), 50)
    df = pd.DataFrame(dict(x=x, g=g))
    m = df.g.map(ord)
    df["x"] += m

    # Initialize the FacetGrid object
    pal = sns.cubehelix_palette(10, rot=-.25, light=.7)
    g = sns.FacetGrid(df, row="g", hue="g", aspect=15, height=.5, palette=pal)

    # Draw the densities in a few steps
    g.map(sns.kdeplot, "x",
          bw_adjust=.5, clip_on=False,
          fill=True, alpha=1, linewidth=1.5)
    g.map(sns.kdeplot, "x", clip_on=False, color="w", lw=2, bw_adjust=.5)

    # passing color=None to refline() uses the hue mapping
    g.refline(y=0, linewidth=2, linestyle="-", color=None, clip_on=False)

    # Define and use a simple function to label the plot in axes coordinates
    def label(x, color, label, **kwargs):
        ax = plt.gca()
        ax.text(0, .2, label, fontweight="bold", color=color,
                ha="left", va="center", transform=ax.transAxes)

    g.map(label, "x")

    # Set the subplots to overlap
    g.figure.subplots_adjust(hspace=-.25)

    # Remove axes details that don't play well with overlap
    g.set_titles("")
    g.set(yticks=[], ylabel="")
    g.despine(bottom=True, left=True)
    return None


def plot_cubehelix():
    # Source: https://seaborn.pydata.org/examples/palette_generation.html

    sns.set_theme(style="white")
    rs = np.random.RandomState(50)

    # Set up the matplotlib figure
    f, axes = plt.subplots(3, 3, figsize=(9, 9), sharex=True, sharey=True)

    # Rotate the starting point around the cubehelix hue circle
    for ax, s in zip(axes.flat, np.linspace(0, 3, 10)):
        # Create a cubehelix colormap to use with kdeplot
        cmap = sns.cubehelix_palette(start=s, light=1, as_cmap=True)

        # Generate and plot a random bivariate dataset
        x, y = rs.normal(size=(2, 50))
        sns.kdeplot(
            x=x, y=y,
            cmap=cmap, fill=True,
            clip=(-5, 5), cut=10,
            thresh=0, levels=15,
            ax=ax,
        )
        ax.set_axis_off()

    ax.set(xlim=(-3.5, 3.5), ylim=(-3.5, 3.5))
    f.subplots_adjust(0, 0, 1, 1, .08, .08)
    return None


def plot_trellis():
    # Source: https://seaborn.pydata.org/examples/timeseries_facets.html

    sns.set_theme(style="dark")

    flights = sns.load_dataset("flights")

    # Plot each year's time series in its own facet
    g = sns.relplot(
        data=flights,
        x="month", y="passengers", col="year", hue="year",
        kind="line", palette="crest", linewidth=4, zorder=5,
        col_wrap=3, height=2, aspect=1.5, legend=False,
    )

    # Iterate over each subplot to customize further
    for year, ax in g.axes_dict.items():
        # Add the title as an annotation within the plot
        ax.text(.8, .85, year, transform=ax.transAxes, fontweight="bold")

        # Plot every year's time series in the background
        sns.lineplot(
            data=flights, x="month", y="passengers", units="year",
            estimator=None, color=".7", linewidth=1, ax=ax,
        )

    # Reduce the frequency of the x axis ticks
    ax.set_xticks(ax.get_xticks()[::2])

    # Tweak the supporting aspects of the plot
    g.set_titles("")
    g.set_axis_labels("", "Passengers")
    g.tight_layout()
    return None


# ----- Flask boilerplate -----

app = Flask(__name__, static_folder=web_directory, static_url_path='')


@app.route('/')
def home_page():
    return send_from_directory(web_directory, 'index.html')


@app.route('/nitro', websocket=True)
def socket():
    ws = simple_websocket.Server(request.environ)
    try:
        nitro.serve(ws.send, ws.receive)
    except simple_websocket.ConnectionClosed:
        pass
    return ''


if __name__ == '__main__':
    app.run()
