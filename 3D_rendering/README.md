# 3D Rendering
Tools for working with 3D models

## render_image.py
This script uses Panda3D to generate a variable number of images containing a variable number of rendered 3D models.
These models are randomly placed around a backdrop, and have their scale randomly adjusted within a set of limits.
Generated images are saved in an output directory supplied by the user. If no directory is given, a default is used.

### Installation
To use the program, make sure you are using Python 3. Also, make sure you have Panda3D installed. I recommend installing it with PIP:

```bash
pip install panda3d 
```

If you're on Linux and you don't have sudo permission, I recommend creating a Python virtual environment with the command:

```bash
python3 -m venv <your virtual environment name>
```

Once created, you can activate the virtual environment with `source ./<your virtual enviornment name>/bin/activate`, assuming you didn't create the virtual environment in a different directory. The virtual enviornment essentially serves as a fresh, temporary install of Python, where you can mess around with things without worrying about messing up your actual Python installation. Once you activate the environment, you should be able to install Panda3D using PIP without issue.

To deactivate the environment, simply use `deactivate`.

### Usage

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

### Troubleshooting
When attempting to run the program, you may get an error like this: 

```bash
Xlib:  extension "XFree86-DGA" missing on display ":27".
:display(error): The application requested harware acceleration, but your OpenGL
:display(error): driver, Mesa GLX Indirect, only supports software rendering.
:display(error): You need to install a hardware-accelerated OpenGL driver, or,
:display(error): if you actually *want* to use a software renderer, then
:display(error): alter the hardware/software configuration in your Config.prc file.
:ShowBase(warning): Unable to open 'onscreen' window.
Traceback (most recent call last):
   ... (traceback listed here) ...
Exception: Could not open window.
```
In this case, Panda3D cannot generate its graphics window on your system. The above error occurred for me on Linux.

* The `Xlib` message relates to the X11 system for displaying graphical windows on your screen, with X11 being widely used on Linux distributions. This is not really an error, and more of a warning. To fix the problem listed above, [this NVIDIA page](https://download.nvidia.com/XFree86/Linux-x86/177.68/README/chapter-07.html) suggests adding `Load "extmod"` to your `xorg.conf` file. [This guide from IBM](https://developer.ibm.com/technologies/linux/tutorials/l-lpic1-106-1/) is a good resource for learning how to do that. However, even if you see an Xlib warning like that, the program may still be able to run correctly.

* The other message indicated by `:display(error):` is an error related to your system's graphics driver. To fix the issue, your options are to install a different OpenGL driver, or to edit the Panda3D config file, `Config.prc`, which is located at the install location of Panda3D on your system under the `etc/` directory. If your graphics driver doesn't support OpenGL and you don't want to update it, you can set the software renderer "tinydisplay" as a fallback renderer in `Config.prc`. Try doing the following:

   1. Find the install location of Panda3D on your machine. If you installed with PIP, it should be located with your python install at the path `site-packages/panda3d/.
   2. Open `etc/Config.prc` with a text editor
   3. Locate the following section:
   ```bash
   ###########################################################
   ###                                                     ###
   ### Panda3D Configuration File -  User-Editable Portion ###
   ###                                                     ###
   ###########################################################

   # Uncomment one of the following lines to choose whether you should
   # run using OpenGL, DirectX or TinyPanda (software) rendering.
   # There can only be one load-display line, but you can use
   # multiple aux-display lines to specify fallback modules.
   # When the module indicated by load-display fails, it will fall
   # back to the next display module indicated by aux-display,
   # when that fails, the next aux-display line, and so on.

   load-display pandagl

   ```
   4. Add `aux-display p3tinydisplay` on the line below `load-display pandagl`. This will cause the renderer to revert to software rendering if OpenGL cannot be used.

   Note: the config file can actually be set programatically using the ConfigVariableString class. Check out the documentation on how to do that [here](https://docs.panda3d.org/1.10/python/programming/configuration/accessing-config-vars-in-a-program). You can also learn more about editing the config file with [the official Panda3D documentation](https://docs.panda3d.org/1.10/python/programming/configuration/configuring-panda3d).

* Lastly, if all else fails and you can't get Panda3D running on your Linux system, try running it on Windows instead.

### Limitations
1. Some aspects of this program are hard-coded, such as the background model that is used and its size and scale.
Additionally, all images are hard-coded to be saved as .bmp files, but Panda3D can output other formats as well.
2. Currently there is nothing stopping models from being generated on top of/inside of previously placed models.
3. Please note that only certain 3D model filetypes are supported by Panda3D. If a model path is not specified by the user, the default panda model is used.
4. On Linux, it appears that when a non-default image width and height are used, the first image generated by the program is always entirely black. This does not happen on Windows.
5. On Linux, depth maps are not currently outputting correctly when using software rendering with p3tinydisplay.
