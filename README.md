# Matplotlib plugin for H2O Nitro

This plugin lets you use [Matplotlib](https://matplotlib.org/stable/index.html)
and [Seaborn](https://seaborn.pydata.org/) visualizations in [Nitro](https://github.com/h2oai/nitro) apps.

**Warning: Try to avoid pyplot in web apps!** pyplot maintains references to the opened figures to make show() work, but
this will cause memory leaks unless the figures are properly closed[^1].

[^1]: See [Matplotlib docs on embedding](https://matplotlib.org/3.5.0/gallery/user_interfaces/web_application_server_sgskip.html)

## Demo

### Matplotlib

![Matplotlib](demo_matplotlib.gif)

[View source](examples/matplotlib_basic.py).

### Seaborn

![Seaborn](demo_seaborn.gif)

[View source](examples/seaborn_basic.py).


## Install

```
pip install h2o-nitro-matplotlib
```

## Usage

1. Import the plugin:


```py
from h2o_nitro_matplotlib import matplotlib_plugin, matplotlib_box
```


2. Register the plugin:

```py
nitro = View(main, title='My App', caption='v1.0', plugins=[matplotlib_plugin()])
```

3. Use the plugin:

```py 
# Make a figure:
x = np.linspace(0, 2, 100)  # Sample data.
fig = Figure()
ax = fig.subplots()
ax.plot(x, x, label='linear')  # Plot some data on the axes.
ax.plot(x, x ** 2, label='quadratic')  # Plot more data on the axes...
ax.plot(x, x ** 3, label='cubic')  # ... and some more.
ax.set_xlabel('x label')  # Add an x-label to the axes.
ax.set_ylabel('y label')  # Add a y-label to the axes.
ax.legend()  # Add a legend.

# Display the figure:
view(matplotlib_box(fig))
```
