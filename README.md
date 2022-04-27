# BaColonyzer

[![PyPI](https://img.shields.io/pypi/v/bacolonyzer?style=for-the-badge)](https://pypi.org/project/bacolonyzer/) [![PyPI - License](https://img.shields.io/pypi/l/bacolonyzer?style=for-the-badge)](https://github.com/judithbergada/bacolonyzer/blob/master/LICENSE)

by Judith Bergadà Pijuan.

BaColonyzer is a software to quantify the cell density of bacterial cultures
from timecourse pictures. It uses image analysis tools to determine the fitness
of spotted cultures of bacteria grown on solid agar.

## Installation

BaColonyzer can be installed under Linux, macOS and Microsoft Windows.
It is available in PyPI for Python3.

To install the tool, please run this command in your terminal:

```bash
pip3 install bacolonyzer
```

If you want to test if your installation has worked, type:

```bash
bacolonyzer -h
```

Further information on the installation can be found in the
[Installation Guide](https://judithbergada.github.io/bacolonyzer/installation/).

If (on Windows) you run into a warning like 

```bash
WARNING: The script f2py.exe is installed in 'C:\Program Files (x86)\Python\Scripts' which is not on PATH.
```

Then this is not a problem of Python or BaColonyzer, but rather your Windows paths. You can solve this by adding your script path (as referenced in the warning on your command prompt). For this, click start, search for "environment variables". Click "edit the system environment variables" -> "Environment Variables...".

If the top box (user variables) one entry is named "Path", click on it, click "Edit". A new window pops up. Click "New" and paste in your script path, e.g. `C:\Program Files (x86)\Python\Scripts`.

If the top box does not have a variable named "path" click New to create one, set the name to "Path", and the value to your desired path, e.g. `C:\Program Files (x86)\Python\Script`.

## Usage

Basic information on how to use BaColonyzer can be obtained using
the `help` flag:

```bash
bacolonyzer -h
```

BaColonyzer has two main commands available for the users. Try the following
if you want to get further information:

```bash
bacolonyzer analyse -h
bacolonyzer rename_images -h
```

Alternatively, you can visit the [BaColonyzer webpage](https://judithbergada.github.io/bacolonyzer/usage/), where you will find
detailed documentation and instructions to use the tool.
We highly recommend to visit it in order to understand the input parameters as well as the outputs provided.
