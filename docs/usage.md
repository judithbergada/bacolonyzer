# Usage

BaColonyzer has three main commands available for the users:

* `bacolonyzer analyse`: This is the most important command and is needed
  to analyse timeseries of QFA images. It locates the bacterial cultures on
  the plate, identifying spots and agar, and it generates output files for each
  image. The outputs contain the cell density estimates and the area of each
  spotted colony.

* `bacolonyzer stabilize_images`: This is a very useful command to stabilize
the images that may have been moved or rotated during the experiment. It is
very important to guarantee the precision and reliability of the results.

* `bacolonyzer rename_images`: This is a useful command to rename the image
files according to the recommended date-time format:
QFAxxxxxxxxxx_YYYY-MM-DD_hh-mm-ss.jpeg, where xxxxxxxxxx is a random number.

A short description can be obtained as follows:

```text
$ bacolonyzer --help
usage: bacolonyzer [-h] [-v] {analyse,rename_images,stabilize_images}
```


## Analyse

BaColonyzer has been designed with a very few number of input
parameters in order to guarantee its robustness and reliablility.
A brief description of the inputs can be found with the `help` flag:

```text
$ bacolonyzer analyse --help
usage: bacolonyzer analyse [-h] [-d DIRECTORY] [-c] [-r REFERENCE_IMAGE] [-q]
                           [-e] [-g GRID_FORMAT [GRID_FORMAT ...]]
                           [-f FRACTION] [-l]
```

**Directory**

Using `--directory` or `-d`, users specify the path to the folder that
contains the image files for analysis. If not specified, BaColonyzer
will search in the current directory.

!!! info "Please note"

    BaColonyzer analyses **all images** found in the given `directory`.
    These are the files with the extension .jpg, .jpeg, .tif, .tiff or .png.
    BaColonyzer always assumes that alphabetical ordering of the images
    matches temporal order. This is why we recommend to rename all the image
    files according to this format: QFA_90000000001_YYYY-MM-DD_hh-mm-ss.

BaColonyzer will only consider images found in the given directory, ignoring
the files existing in any of the subfolders.

Example:
```bash
bacolonyzer analyse -d /Users/myname/Documents/2019-07-Saureus
```

**Grid format**

The `--grid_format` or `-g` is used by BaColonyzer to find the position of the
agar and the colonies. Thus it is of great importance to specify it properly.

The required format is: "n_rows n_columns" or "n_rowsxn_columns". By default,
BaColonyzer will consider 8x12, which is the format corresponding to a
96 well-plate of 8 rows and 12 columns.

Example:
```bash
bacolonyzer analyse -g 8x12
```
Or alternatively:
```bash
bacolonyzer analyse -g 8 12
```

**Fraction**

In order to find the position of the spots and the agar, and to ignore the
borders of the pictures if they are not part of the plate, BaColonyzer needs to
know the fraction of the image that corresponds to the agar plate.

Since this is very difficult to know, BaColonyzer tries different fractions,
starting from a minimum value which is set by the user: `--fraction` or `-f`.
By default, BaColonyzer will assume that the plate occupies at least 80% of the
image, and it will try any fraction from 0.8 to 1.

!!! info "Please note"

    If your plate occupies a small part of the image, it is safer to decrease
    the value of `fraction`. However, please consider that this will increase
    the computational time, and we do not recommend to use images where the
    agar plate is so small. You should also make sure that 0 < `fraction` < 1.

Example:
```bash
bacolonyzer analyse -f 0.8
```

**grid_by_peaks**

The default method to find the position of the agar plate and the colonies
is by using the grid format. However, if the agar plate is well aligned (no rotation)
and the colonies are well distributed, BaColonyzer can also find the position
of the agar plate and the colonies by using the peaks of the image intensities
along the x and y axis of the image. This option is sensitive to the plate
edge being visible and you may need to provide a fake image as new last image
where you've drawn white filled circles on each position of the spots.


Example:
```bash
bacolonyzer analyse -p
```


**Light correction**

By default, BaColonyzer normalises all of the images and the colony areas by
subtracting the value of the agar. This is highly recommended, since it will
correct for differences in light intensities between and within images,
and results will be more accurate.

To disable the lighting correction, please use the flag `--light_correction_off`
or `-c`.

Example:
```bash
bacolonyzer analyse -c
```

**Adaptive segmentation**

In order to correct for images that show a very low contrast between colonies
and background, and to improve the detection of spots, Bacolonyzer can perform
an adaptive segmentation of the image. This option might also be useful
if the difference in intensity between individual colonies is large.

By default, BaColonyzer will not correct for that. However, you can enable
this option with the parameter `-l` or `--low_contrasts`.

Example:
```bash
bacolonyzer analyse -l
```

**Reference image**

In order to compare experiments in which the timelapse images were taken using
different camera settings, BaColonyzer allows the users to provide a reference
picture for the calibration. The path to this image can be specified using the
parameter `-r` or `--reference_image`.

The reference must be an image showing a white and black paper next to each
other, and must be taken using the same camera settings as the image series
that are being analysed.

By default, BaColonyzer will not use any image for the calibration. However,
it is highly recommended to provide one.

Example:
```bash
bacolonyzer analyse -r ./reference/Ref_ISO400.png
```

!!! info "Please note"

    It is recommended not to have the reference image together with the rest
    of images that will be analysed. Instead, we recommend to create a
    subfolder or to place the reference image in another path.
    This is because during the analysis, **all images** in the
    directory will be analysed except the reference image. However,
    if the parameter `-r` is not specified and a reference image is
    found in the same directory, this reference picture will also be
    analysed and treated in the same way as the rest of the pictures.

**Other parameters**

* `--quiet` or `-q`: using this flag, users can suppress any information
  messages printed in the screen during analysis.

* `--endpoint` or `-e`: using this flag, users will analyse only the last
  image in the series, ignoring the rest. This is useful to test single
  images.

Examples:
```bash
bacolonyzer analyse -q
```
```bash
bacolonyzer analyse -e
```

## Stabilize images

BaColonyzer offers the possibility to stabilize the image files of a directory
to ensure that undesired rotations of movements do not affect the final results.
A brief description of the inputs can be found using the `help` flag:

```text
$ bacolonyzer stabilize_images --help
usage: bacolonyzer rename_images [-h] [-d DIRECTORY] [-o OUTPUT_DIRECTORY] [-q]
```

**Directory**

Using `--directory` or `-d`, users specify the path to the folder that
contains all image files to stabilize. If not specified, BaColonyzer
will search in the current directory.

Example:
```bash
bacolonyzer stabilize_images -d /Users/myname/Documents/2019-07-Saureus
```

**Output directory**

Using `--output_directory` or `-o`, users specify the new directory where the
stabilized images will be stored. By default, BaColonyzer creates a new folder
inside the current directory, which is named "corrected_images".

!!! info "Please note"

    If the output directory does not exist, it will be created. If it exists,
    the images inside this directory will be overwritten.

Example:
```bash
bacolonyzer stabilize_images -o /Users/myname/Documents/2019-07-Saureus_correct
```

**Other parameters**

* `--quiet` or `-q`: using this flag, users can suppress any information
  messages printed in the screen during analysis.

Examples:
```bash
bacolonyzer stabilize_images -q
```


## Rename images

BaColonyzer offers the possibility to rename the image files of a directory
according to a format which is highly recommended:
QFAxxxxxxxxxx_YYYY-MM-DD_hh-mm-ss.jpeg, where xxxxxxxxxx is a random number.
A brief description of the inputs can be found using the `help` flag:

```text
$ bacolonyzer rename_images --help
usage: bacolonyzer rename_images [-h] [-d DIRECTORY] [-g GLOB] [-p PREFIX]
                                 [-m] [-s START_TIME] [-i INTERVAL]
                                 [--no_dry_run]
```

**Directory**

Using `--directory` or `-d`, users specify the path to the folder that
contains all files to rename. If not specified, BaColonyzer
will search in the current directory.

!!! info "Please note"

    BaColonyzer will rename **all files** in the given `directory`
    that match a given glob (see **glob**).

Example:
```bash
bacolonyzer rename_images -d /Users/myname/Documents/2019-07-Saureus
```

**Glob**

The parameter `--glob` or `-g` allows the users to choose the glob to match.
Thus **all files** containing this glob will be renamed. By default,
BaColonyzer will rename files ending with .jpg.

Example (rename all files ending with .png):
```bash
bacolonyzer rename_images -g *.png
```

Example 2 (rename all files starting with IMG_):
```bash
bacolonyzer rename_images -g IMG_*
```

**Read metadata**

By default, BaColonyzer will rename all image files by using the date
and time information retrieved from the images metadata.

In order to avoid using images metadata for the renaming, the flag `-m` or
`--no_read_metadata` is needed. In this case, the renaming will take place
according to parameters `-s` and `-i`.

Example:
```bash
bacolonyzer rename_images -m -s "2019-08-11 12:30" -i 30
```

**Start time**

Users can specify with `--start_time` or `s` the date and time of the
first image, which will be used as a reference to rename the whole image series.
By default, BaColonyzer will take the current date and time.

Required format: "YYYY-MM-DD hh:mm". Example:
```bash
bacolonyzer rename_images -m -s "2019-08-11 12:30"
```

!!! info "Please note"

    This parameter will only be considered if users also require flag `-m`.
    The date time format must be given within quotes.

**Dry run**

By default, BaColonyzer will only show the renaming of the image files.
However, to keep the users safe, it will not apply the modifications.

In order to definitely rename all files, the flag `--no_dry_run` is needed.

Example:
```bash
bacolonyzer rename_images --no_dry_run
```

**Other parameters**

* `--interval` or `-i`: this parameter should be adjusted to define the time
  interval between images (in minutes), and will only be considered together
  with parameter `-m`. By default, BaColonyzer assumes 30min.

  Example:
  ```bash
  bacolonyzer rename_images -m -i 30
  ```

* `--prefix` or `-p`: this parameter defines the prefix of the new names.
  It is recommended to use a barcode for the images, and by default, BaColonyzer
  will use QFAxxxxxxxxxx_, where xxxxxxxxxx is a random number.

  Example:
  ```bash
  bacolonyzer rename_images -p QFAxxxxxxxxxx_
  ```

**Enjoy using BaColonyzer!**
