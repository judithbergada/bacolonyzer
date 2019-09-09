# Usage

ReColonyzer has two main commands available for the users:

* `recolonyzer analyse`: This is the most important command and is needed
  to analyse timeseries of QFA images. It locates the bacterial cultures on
  the plate, identifies spots and agar, and generates output files for each
  image. The outputs contain the cell density estimates and the area of each
  spotted colony.

* `recolonyzer rename_images`: This is a useful command to rename the image
files accordig to the recommended date time format:
QFA_90000000001_YYYY-MM-DD_hh-mm-ss.jpeg.

A short description can be obtained as follows:

```text
$ recolonyzer --help
usage: recolonyzer [-h] [-v] {analyse,rename_images}
```


## Analyse

ReColonyzer has been designed with a very few number of input
parameters in order to guarantee its robustness and reliablility.
A brief description of the inputs can be found with the `help` flag:

```text
$ recolonyzer analyse --help
usage: recolonyzer analyse [-h] [-d DIRECTORY] [-c] [-r REFERENCE_IMAGE] [-q]
                           [-e] [-g GRID_FORMAT [GRID_FORMAT ...]]
                           [-f FRACTION]
```

**Directory**

Using `--directory` or `-d`, users specify the path to the folder that
contains the image files for analysis. If not specified, ReColonyzer
will search in the current directory.

!!! info "Please note"

    ReColonyzer analyses **all images** found in the given `directory`.
    These are the files with the extension .jpg, .jpeg, .tif, .tiff or .png.
    ReColonyzer always assumes that alphabetical ordering of the images
    matches temporal order. This is why we recommend to rename all the image
    files according to this format: QFA_90000000001_YYYY-MM-DD_hh-mm-ss.

ReColonyzer will only consider images found in the given directory, ignoring
the files existing in any of the subfolders.

Example:
```bash
recolonyzer analyse -d /Users/myname/Documents/2019-07-Saureus
```

**Grid format**

The `--grid_format` or `-g` is used by ReColonyzer to find the position of the
agar and the colonies. Thus it is of great importance to specify it properly.

The required format is: "n_rows n_columns" or "n_rowsxn_columns". By default,
ReColonyzer will consider 8x12, which is the format corresponding to a
96 well-plate of 8 rows and 12 columns.

Example:
```bash
recolonyzer analyse -g 8x12
```
Or alternatively:
```bash
recolonyzer analyse -g 8 12
```

**Fraction**

In order to find the position of the spots and the agar, and to ignore the
borders of the pictures if they are not part of the plate, ReColonyzer needs to
know the fraction of the image that corresponds to the agar plate.

Since this is very difficult to know, ReColonyzer tries different fractions,
starting from a minimum value which is set by the user: `--fraction` or `-f`.
By default, ReColonyzer will assume that the plate occupies at least 80% of the
image, and it will try any fraction from 0.8 to 1.

!!! info "Please note"

    If your plate occupies a small part of the image, it is safer to decrease
    the value of `fraction`. However, please consider that this will increase
    the computational time, and we do not recommend to use images where the
    agar plate is so small. You should also make sure that 0 < `fraction` < 1.

Example:
```bash
recolonyzer analyse -f 0.8
```

**Light correction**

By default, ReColonyzer normalises wach of the images and the colony areas by
subtracting the value of the agar. This is highly recommended, since it will
correct for differences in light intensities between and within images,
and results will be more accurate.

To disable the lighting correction, please use the flag `--light_correction_off`
or `-c`.

Example:
```bash
recolonyzer analyse -c
```
**Reference image**

In order to compare experiments in which the timelapse images were taken using different camera settings, ReColonyzer allows the users to provide a reference picture for the calibration. The path to this image can be specified using the parameter `-r` or `--reference_image`.

The reference must be an image showing a white and black paper next to each other, and must be taken using the same camera settings as the image series that are being analysed.

By default, ReColonyzer will not use any image for the calibration. However, it is highly recommended to provide one.

Example:
```bash
recolonyzer analyse -r ./reference/Ref_ISO400.png
```

!!! info "Please note"

    It is recommended not to have the reference image together with the rest of images that will be analysed. Instead, we recommend to create a subfolder or to place the reference image in another path.
    This is because during the analysis, **all images** in the directory will be analysed except the reference image. However, if the parameter `-r` is not specified and a reference image is found in the same directory, this reference picture will also be analysed and treated in the same way as the rest of the pictures.

**Other parameters**

* `--quiet` or `-q`: using this flag, users can suppress any information
  messages printed in the screen during analysis.

* `--endpoint` or `-e`: using this flag, users will analyse only the last
  image in the series, ignoring the rest. This is useful to test single
  images.

Examples:
```bash
recolonyzer analyse -q
```
```bash
recolonyzer analyse -e
```


## Rename images

ReColonyzer offers the possibility to rename the image files of a directory
according to a format which is highly recommended:
QFA_90000000001_YYYY-MM-DD_hh-mm-ss.jpeg.
A brief description of the inputs can be found using the `help` flag:

```text
$ recolonyzer rename_images --help
usage: recolonyzer rename_images [-h] [-d DIRECTORY] [-g GLOB] [-p PREFIX]
                                 [-m] [-s START_TIME] [-i INTERVAL]
                                 [--no_dry_run]
```

**Directory**

Using `--directory` or `-d`, users specify the path to the folder that
contains all files to rename. If not specified, ReColonyzer
will search in the current directory.

!!! info "Please note"

    ReColonyzer will rename **all files** in the given `directory`
    that match a given glob (see **glob**).

Example:
```bash
recolonyzer rename_images -d /Users/myname/Documents/2019-07-Saureus
```

**Glob**

The parameter `--glob` or `-g` allows the users to choose the glob to match.
Thus **all files** containing this glob will be renamed. By default,
ReColonyzer will rename files ending with .jpg.

Example (rename all files ending with .png):
```bash
recolonyzer rename_images -g *.png
```

Example 2 (rename all files starting with IMG_):
```bash
recolonyzer rename_images -g IMG_*
```

**Read metadata**

By default, ReColonyzer will rename all image files by using the date
and time information retrieved from the images metadata.

In order to avoid using images metadata for the renaming, the flag `-m` or
`--no_read_metadata` is needed. In this case, the renaming will take place
according to parameters `-s` and `-i`.

Example:
```bash
recolonyzer rename_images -m -s "2019-08-11 12:30" -i 30
```

**Start time**

Users can specify with `--start_time` or `s` the date and time of the
first image, which will be used as a reference to rename the whole image series.
By default, ReColonyzer will take the current date and time.

Required format: "YYYY-MM-DD hh:mm". Example:
```bash
recolonyzer rename_images -m -s "2019-08-11 12:30"
```

!!! info "Please note"

    This parameter will only be considered if users also require flag `-m`. The date time format must be given within quotes.

**Dry run**

By default, ReColonyzer will only show the renaming of the image files. However, to keep the users safe, it will not apply the modifications.

In order to definitely rename all files, the flag `--no_dry_run` is needed.

Example:
```bash
recolonyzer rename_images --no_dry_run
```

**Other parameters**

* `--interval` or `-i`: this parameter should be adjusted to define the time
  interval between images (in minutes), and will only be considered together
  with parameter `-m`. By default, ReColonyzer assumes 30min.

  Example:
  ```bash
  recolonyzer rename_images -m -i 30
  ```

* `--prefix` or `-p`: this parameter defines the prefix of the new names.
  It is recommended to use a barcode for the images, and by default, ReColonyzer
  will use QFA_90000000001_.

  Example:
  ```bash
  recolonyzer rename_images -p QFA_90000000001_
  ```

**Enjoy using ReColonyzer!**
