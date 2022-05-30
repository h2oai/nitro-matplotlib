import numpy as np
import simple_websocket
from flask import Flask, request, send_from_directory

from matplotlib.figure import Figure
from matplotlib import cbook
from matplotlib import cm
from matplotlib.ticker import LinearLocator
from matplotlib.colors import LightSource

# ----- Nitro app -----

from h2o_nitro import View, web_directory
from h2o_nitro_matplotlib import matplotlib_plugin, matplotlib_box


# Entry point
def main(view: View):
    # Show each plot one by one
    view('## Line plots', matplotlib_box(plot_simple()))
    view('## Signal coherence', matplotlib_box(plot_line()))
    view('## Bars in polar coords', matplotlib_box(plot_polar()))
    view('## Color map', matplotlib_box(plot_colormap()))
    view('## Surface plot', matplotlib_box(plot_surface()))


# Nitro instance
nitro = View(
    main,
    title='Nitro + Matplotlib',
    caption='A minimal example',
    plugins=[matplotlib_plugin()],  # Include the Bokeh plugin
)


# ----- Matplotlib plotting routines -----

def plot_simple() -> Figure:
    # Source: https://matplotlib.org/stable/tutorials/introductory/usage.html#the-object-oriented-and-the-pyplot-interfaces
    x = np.linspace(0, 2, 100)  # Sample data.

    # Important: Generate the figure **without using pyplot**.
    fig = Figure()

    ax = fig.subplots()
    ax.plot(x, x, label='linear')  # Plot some data on the axes.
    ax.plot(x, x ** 2, label='quadratic')  # Plot more data on the axes...
    ax.plot(x, x ** 3, label='cubic')  # ... and some more.
    ax.set_xlabel('x label')  # Add an x-label to the axes.
    ax.set_ylabel('y label')  # Add a y-label to the axes.
    ax.legend()  # Add a legend.

    return fig


def plot_line() -> Figure:
    # Source: https://matplotlib.org/stable/gallery/lines_bars_and_markers/cohere.html#sphx-glr-gallery-lines-bars-and-markers-cohere-py

    # Fixing random state for reproducibility
    np.random.seed(19680801)

    dt = 0.01
    t = np.arange(0, 30, dt)
    nse1 = np.random.randn(len(t))  # white noise 1
    nse2 = np.random.randn(len(t))  # white noise 2

    # Two signals with a coherent part at 10Hz and a random part
    s1 = np.sin(2 * np.pi * 10 * t) + nse1
    s2 = np.sin(2 * np.pi * 10 * t) + nse2

    # Important: Generate the figure **without using pyplot**.
    fig = Figure()
    axs = fig.subplots(2, 1)
    axs[0].plot(t, s1, t, s2)
    axs[0].set_xlim(0, 2)
    axs[0].set_xlabel('time')
    axs[0].set_ylabel('s1 and s2')
    axs[0].grid(True)

    cxy, f = axs[1].cohere(s1, s2, 256, 1. / dt)
    axs[1].set_ylabel('coherence')
    fig.tight_layout()

    return fig


def plot_polar() -> Figure:
    # Source: https://matplotlib.org/stable/gallery/pie_and_polar_charts/polar_bar.html#sphx-glr-gallery-pie-and-polar-charts-polar-bar-py

    # Fixing random state for reproducibility
    np.random.seed(19680801)

    # Compute pie slices
    N = 20
    theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
    radii = 10 * np.random.rand(N)
    width = np.pi / 4 * np.random.rand(N)

    # Important: Generate the figure **without using pyplot**.
    fig = Figure()
    colors = cm.viridis(radii / 10.)
    ax = fig.subplots(subplot_kw=dict(projection='polar'))
    ax.bar(theta, radii, width=width, bottom=0.0, color=colors, alpha=0.5)

    return fig


def plot_colormap() -> Figure:
    # Source: https://matplotlib.org/stable/gallery/mplot3d/surface3d.html#sphx-glr-gallery-mplot3d-surface3d-py

    # Important: Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots(subplot_kw=dict(projection='3d'))

    # Make data.
    X = np.arange(-5, 5, 0.25)
    Y = np.arange(-5, 5, 0.25)
    X, Y = np.meshgrid(X, Y)
    R = np.sqrt(X ** 2 + Y ** 2)
    Z = np.sin(R)

    # Plot the surface.
    surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)

    # Customize the z axis.
    ax.set_zlim(-1.01, 1.01)
    ax.zaxis.set_major_locator(LinearLocator(10))
    # A StrMethodFormatter is used automatically
    ax.zaxis.set_major_formatter('{x:.02f}')

    # Add a color bar which maps values to colors.
    fig.colorbar(surf, shrink=0.5, aspect=5)

    return fig


def plot_surface() -> Figure:
    # Source: https://matplotlib.org/stable/gallery/mplot3d/custom_shaded_3d_surface.html#sphx-glr-gallery-mplot3d-custom-shaded-3d-surface-py

    # Load and format data
    dem = cbook.get_sample_data('jacksboro_fault_dem.npz', np_load=True)
    z = dem['elevation']
    nrows, ncols = z.shape
    x = np.linspace(dem['xmin'], dem['xmax'], ncols)
    y = np.linspace(dem['ymin'], dem['ymax'], nrows)
    x, y = np.meshgrid(x, y)

    region = np.s_[5:50, 5:50]
    x, y, z = x[region], y[region], z[region]

    # Important: Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots(subplot_kw=dict(projection='3d'))

    ls = LightSource(270, 45)
    # To use a custom hillshading mode, override the built-in shading and pass
    # in the rgb colors of the shaded surface calculated from "shade".
    rgb = ls.shade(z, cmap=cm.gist_earth, vert_exag=0.1, blend_mode='soft')
    surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, facecolors=rgb,
                           linewidth=0, antialiased=False, shade=False)

    return fig


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
