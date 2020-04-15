# 3D Rendering
Tools for working with 3D models

## render_image.py
This program uses Panda3D to generate a variable number of images containing a variable number of rendered 3D models.
These models are randomly placed around a backdrop, and have their scale randomly adjusted within a set of limits.
Generated images are saved in an output directory supplied by the user. If no directory is given, a default is used.

### installation
To use the program, make sure you are using python 3. Also, make sure you have Panda3D installed. I recommend installing it with PIP:

```bash
pip install panda3d 
```

### usage

```bash
usage: render_image.py [-h] [-v] [-d] [-s] [--eye_sep EYE_SEPARATION]
                       [--image_width IMAGE_WIDTH]
                       [--image_height IMAGE_HEIGHT] [--model_path MODEL_PATH]
                       [--out_dir OUTPUT_DIRECTORY_PATH]
                       images_to_generate models_per_image
```

required arguments:
* images_to generate - number of images to generate
* models_per_image   - number of 3D models to render per generated image

optional arguments:
* -h, --help         - show help message and exit
* -v, --verbose      - print full console output
* -d, --depth_map    - output a depth map of the generated image(s)
* -s, --stereo       - generate two stereo images based on a given eye separation
* --image_width      - pixel width of generated image(s) (default: 800)
* --image_height     - pixel height of generated image(s) (default: 600)
* --model_path       - path to 3D model to be rendered in images
* --out_dir          - path to directory which images will be generated in

The -s flag triggers stereo image generation, in which 2 images are generated instead of 1, with the perspective 
of each image being offset to represent the left and right eye, based on a given eye separation. If no eye_separation
is specified when generating stereo images, a default is used.

The -d flag causes the program to output a depth map of the generated image(s). The depth map is visualized in grayscale
using a shader file z_buf.sha, which must be located in the same directory as this program for this feature to work.
When stereo images are being generated, a single depth map is produced that represents the view in-between the left
and right eyes.

### notes
1. Some aspects of this program are hard-coded, such as the background model that is used and its size and scale.
Additionally, all images are hard-coded to be saved as .bmp files, but Panda3D can output other formats as well.
2. Currently there is nothing stopping models from being generated on top of/inside of previously placed models.
3. Please note that only certain 3D model filetypes are supported by Panda3D. If a model path is not specified by the user, the default panda model is used.
