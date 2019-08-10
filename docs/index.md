# ReColonyzer

Description of the software.

## Installation

ReColonyzer is available in PyPI for Python3. To install it run the following command in your terminal:

```bash
pip3 install recolonyzer
```

Or if you want to play with the code and make some modifications you can download the code and install it in development mode:

```bash
git clone git@github.com:judithbergada/recolonyzer.git
cd recolonyzer
pip3 install -e .
```

Once you have run any of the previous options, you will have the command `recolonyzer` available.

## Usage
-----

To use the software, a command line tool is provided and after following the installation guide, you can start using the command `recolonyzer`.

To have an idea of the inputs required you can always run:

```text
$ recolonyzer --help
usage: recolonyzer [-h] [-d DIRECTORY] [-c] [-q] [-r] [-e]
                   [-g GRID_FORMAT [GRID_FORMAT ...]] [-f FRACTION]

Analyse timeseries of QFA images: locate cultures on plate, segment image into
agar and cells, apply lighting correction, write report including cell density
estimates for each location in each image.

optional arguments:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Directory in which to search for image files that need
                        to analysed. Default: current directory.
  -c, --light_correction
                        Enables lighting correction between images. Default:
                        False. Light correction is disabled.
  -q, --quiet           Suppresses messages printed during the analysis.
                        Default: show messages.
  -r, --remove          Removes any output files from the directory before
                        starting the analysis. It is useful to re-analyse a
                        set of images that have been analysed in advance.
                        Default: False. Keep previous output files.
  -e, --endpoint        Analyses only the final image in the series. It is
                        useful to test single images. Default: False. Analyse
                        all images in the directory.
  -g GRID_FORMAT [GRID_FORMAT ...], --grid_format GRID_FORMAT [GRID_FORMAT ...]
                        Specifies rectangular grid format. Important: specify
                        number of rows and number of columns, in this order
                        (e.g. -g 8x12 or -g 8 12). Default: 8x12.
  -f FRACTION, --fraction FRACTION
                        Specifies the minimum fraction of the image that
                        corresponds to the grid. Adjust it if grid occupies a
                        small part of the total image. Default: 0.8.
```

ReColonyzer analyses all images files found under the `directory` flag given. It assumes that alphabetical ordering of the files is the same as their temporal order. That is why the best approach is to have all the image files named with some `prefix` and then some date time signature (e.g. `my_prefix_YYYY_MM_DD_hh_mm.jpeg`)

and output description
