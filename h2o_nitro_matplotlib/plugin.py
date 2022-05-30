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

import base64
from io import BytesIO
from matplotlib.figure import Figure

from h2o_nitro import box, Box, Plugin, Script

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


def matplotlib_box(figure: Figure) -> Box:
    """
    Creates a Nitro box from a Matplotlib Figure.

    Warning: Do not use pyplot!
    pyplot maintains references to the opened figures to make show() work, but this will cause memory leaks
    unless the figures are properly closed

    :param figure: A Matplotlib Figure
    :return: A box
    """
    # Reference: https://matplotlib.org/3.5.0/gallery/user_interfaces/web_application_server_sgskip.html
    buf = BytesIO()
    figure.savefig(buf, format="png")
    png = base64.b64encode(buf.getbuffer()).decode("ascii")
    return box(mode='plugin:matplotlib.render', data=dict(png=png))
