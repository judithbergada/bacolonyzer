# Outputs

ReColonyzer will create two new folders to save the outputs: "Output_Data" and
"Output_Images". These will be created in the given `directory`.

If folders exist in advance, they will not be overwritten. However, if there
are files inside these folders with the same name as ReColonyzer outputs,
those files will be overwritten.

## Output_Data

This folder will contain tab delimed text files with the image metrics
computed by ReColonyzer. Each file will contain information of one image,
and will be named exactly the same as the original image file, ending with
".out".

Here, users can find, for each image and each colony area:

* Row: row of the colony in the agar plate.
* Column: column of the colony in the agar plate.
* Intensity: total light intensity of the colony. This can be used as the
  cell density estimate for future calculations.
* Area: area of the colony.
* ColonyMean: mean intensity values of the colony.
* BackgroundMean: mean intensity values of the agar.
* Barcode: prefix used to name the image.
* Filename: full name of the image.


## Output_Images

This folder will contain binary images (black/white), which will be named
exactly the same as the original image files used for the anlysis.

The binary images can be used to visualy see the performance of ReColonyzer
to detect the position of the plate, the agar and the colonies on the solid
growth media. Thus, black pixels show the agar and white pixels correspond
to the spots. In addition, the borders of the pictures have been deleted in
order to take only the surface of the plate and ignore the rest.

The area of the colonies in each image, which is shown numerically in
"Output_Data", is inferred from these results.
However, the cell density does not depend on these areas.

**Enjoy using ReColonyzer!**
