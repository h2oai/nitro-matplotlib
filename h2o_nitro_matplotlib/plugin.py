# Copyright 2022 H2O.ai, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional
import base64
from io import BytesIO
import matplotlib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from h2o_nitro import box, Box, Plugin, Script

# Use the Anti-Grain Geometry backend, since we're only going to use non-interactive PNG images
# Ref: https://matplotlib.org/3.5.0/users/explain/backends.html#the-builtin-backends
matplotlib.use('AGG')

# Javascript function for embedding the Matplotlib plot.
# Here, we export one function called render(), which we can later invoke from our Python box().
_render_js = '''
exports.render = (context, element, data) => {
    const img = document.createElement('img');
    img.src = 'data:image/png;base64,' + data.png;
    element.replaceChildren(img);
};
'''


def matplotlib_plugin():
    """
    Creates a Nitro plugin for the currently installed version of Matplotlib.
    :return: A plugin
    """
    return Plugin(
        name='matplotlib',
        scripts=[
            # Install our custom rendering Javascript.
            Script(source=_render_js, type='inline'),
        ],
    )


def matplotlib_box(figure: Optional[Figure] = None) -> Box:
    """
    Creates a Nitro box from a Matplotlib Figure.

    If a figure is not provided, the global matplotlib.pyplot instance is used as the source.
    This is useful when you're using something like Seaborn, which relies on matplotlib.pyplot, but not optimal
    when used inside a web app.

    **Warning: Avoid pyplot if possible!**
    pyplot maintains references to the opened figures to make show() work, but this will cause memory leaks
    unless the figures are properly closed.

    :param figure: A Matplotlib Figure
    :return: A box
    """
    # Reference: https://matplotlib.org/3.5.0/gallery/user_interfaces/web_application_server_sgskip.html
    buf = BytesIO()
    if figure is None:
        plt.savefig(buf, format="png")
        plt.close("all")  # Attempt to avoid memory leaks
    else:
        figure.savefig(buf, format="png")

    png = base64.b64encode(buf.getbuffer()).decode("ascii")
    return box(mode='plugin:matplotlib.render', data=dict(png=png), ignore=True)
