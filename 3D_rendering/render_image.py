# render_image.py
#
# This script uses Panda3D to generate a variable number of images containing a variable number of rendered 3D models.
# These models are randomly placed around a backdrop, and have their scale randomly adjusted within a set of limits.
# Generated images are saved in an output directory supplied by the user. If no directory is given, a default is used.
#
# See the README on Github for more details.
#
# Limitations:
# -Some aspects of this program are hard-coded, such as the background model that is used and its size and scale.
#  Additionally, all images are hard-coded to be saved as .bmp files, but Panda3D can output other formats as well.
# -Currently there is nothing stopping models from being generated on top of/inside of previously placed models.
# -Please note that only certain 3D model filetypes are supported by Panda3D. If a model path is not specified by
#  the user, the default panda model will be used.
#
########################################################################################################################
from panda3d.core import WindowProperties, GraphicsOutput, Texture, NodePath
from panda3d.core import Filename, PNMImage, Camera, Shader
from panda3d.core import DirectionalLight, AmbientLight

from math import log10, ceil
from time import sleep
import random, sys, os, argparse

# Note: any programmatic changes to Panda3D config file
# need to be done before ShowBase is imported
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.filter.FilterManager import FilterManager

''' Panda3D application class '''
class ImageGenerator(ShowBase):
    def __init__(self, num_imgs, models_per_img, img_wid, img_hgt, model_path, out_dir_path, stereo, eye_sep, depth, verbose):
        ShowBase.__init__(self)  #Initialize the application window
        self.num_imgs = num_imgs #Number of images to generate
        self.width = img_wid     #Picture dimensions
        self.height = img_hgt
        self.num_models = models_per_img  #Number of models to generate in scene for each image
        self.model_path = model_path      #Path to model to render in the scene
        self.models = []                  #List of models currently being rendered
        self.out_dir = out_dir_path       #Path to directory where generated images are saved
        self.stereo = stereo              #Boolean indicator of whether stereo images are being generated
        self.eye_separation = eye_sep     #Eye separation used for stereo images
        self.depth = depth                #Boolean indicator of whether depth maps are being generated
        self.verbose = verbose            #Boolean indicator of verbosity
        if(self.depth):
            if self.verbose: print("Depth buffer generation enabled")
            self.depth_manager = FilterManager(base.win, base.cam)  #Filter manager object used for depth visualization
        
        ''' Set limits for random adjustments that are made when placing models in the scene '''
        self.x_lower_lim = -7     #Limits for object position on the x axis
        self.x_upper_lim = 7
        self.y_lower_lim = -17    #Limits for object position on the y axis (smaller value = closer to camera)
        self.y_upper_lim = 5
        self.scale_lower_lim = -2 #Limits for object scale
        self.scale_upper_lim = 2
        
        self.object_height = 2    #Hard-coded height of object in scene 
    
        leading_zeros = str(ceil(log10(self.num_imgs)))   #Number of leading zeros to use in output image filenames                
        
        ''' Create a directory for generated images '''       
        if (self.out_dir in os.listdir()) == False:  #Check if directory already exists
            if self.verbose: print("Creating output directory: {}".format(self.out_dir))
            os.mkdir(self.out_dir)
        else:
            if self.verbose: print("Warning: output directory {} already exists".format(self.out_dir))
            
        ''' Resize image '''
        props = WindowProperties()
        props.setSize(self.width, self.height)
        base.win.requestProperties(props)
        base.graphicsEngine.renderFrame() #render next frame to resize window

        base.disableMouse() #IMPORTANT: must do this to enable custom camera positioning (otherwise camera is controlled by mouse)

        self.placeBackground("models/environment")  #Default background model is 'environment'              
        
        for i in range(self.num_imgs):    #Loop for generating each image
            if(self.verbose):
                print("Iteration {}".format(i))
                
            for j in range(self.num_models): #Load specified number of models            
                self.placeModel(model_path, model_num=j, verbose=self.verbose)                      

            ''' Set camera and generate filenames appropriately based on what type of images are being generated (regular, stereo, or depth) '''
            if(self.stereo):
                file_name1 = Filename((self.out_dir + "/out_{:0" + leading_zeros + "d}_left.bmp").format(i)) #Specify output filenames
                file_name2 = Filename((self.out_dir + "/out_{:0" + leading_zeros + "d}_right.bmp").format(i))

                ''' Render left-eye image '''
                base.camera.setPos(-1*(self.eye_separation/2),-20,5) #Set camera position to the left
                self.renderToPNM(filename=file_name1, verbose=self.verbose) #Produce a rendered image        

                ''' Render right-eye image '''
                base.camera.setPos(self.eye_separation/2,-20,5)      #Set camera position to the right
                self.renderToPNM(filename=file_name2, verbose=self.verbose) #Produce a rendered image       

            else:
                file_name1 = Filename((self.out_dir + "/out_{:0" + leading_zeros + "d}.bmp").format(i)) #Specify output filename
                base.camera.setPos(0, -20, 5) #A non-stereo image is being generated, so center the camera
                self.renderToPNM(filename=file_name1, verbose=self.verbose) #Produce a rendered image        
                
            if self.depth:
                file_name3 = Filename((self.out_dir + "/out_{:0" + leading_zeros + "d}_depth.bmp").format(i)) #Specify output filename
                
                ''' Render depth map '''
                base.camera.setPos(0, -20, 5) #Recenter camera
                self.displayZBuffer(self.depth_manager)  #Apply shader to scene to visualize the depth buffer                      
                self.renderToPNM(filename=file_name3, verbose=self.verbose) #Produce a rendered image
                self.displayCBuffer(self.depth_manager)  #Remove depth shader
                
            ''' Remove all rendered models from the scene '''
            for model in self.models:
                model.removeNode()
                
        self.taskMgr.add(self.stopApplicationTask, 'ExitApp') #exit the app when renders are done

    ''' Place a background model in the scene '''
    def placeBackground(self, model_name):
        self.scene = self.loader.loadModel(model_name) #Load environment backdrop            
        self.scene.reparentTo(self.render) #Add models to the scene
        self.scene.setScale(0.25, 0.25, 0.25) #Adjust scaling of background model
        self.scene.setPos(-8, 42, 2) #Adjust position of background model in scene
        
    ''' Place a model in the scene at a random location. Can be passed a model number if creating multiple models '''    
    def placeModel(self, model_name, model_num=None, verbose=None):        
        model = self.loader.loadModel(model_name)     #Load model from path indicated by model_name
        if model_num is not None:                     #Optionally append a number to the name of the model
            model.name = model_name + "_{:02d}".format(model_num)
            if verbose: print("\tPlacing model {:s}".format(model.name))
        model.reparentTo(self.render)                 #Allow this model to show up in the scene when the scene is rendered
        
        ''' Adjust scale of model to fit within background scene '''
        bg_min, bg_max = self.scene.getTightBounds()  #Get bounds of background model
        bg_height = bg_max[2] - bg_min[2]             #Calculate height of background based on bounds
        bg_height = bg_height / 24                    #Say height of model in background should be about 1/24th of the total background height
        
        model_min, model_max = model.getTightBounds() #Get bounds of model being place
        model_height = model_max[2] - model_min[2]    #Calculate height
                
        scale_origin = bg_height / model_height       #Set baseline scale factor as a proportion of the model height vs the background height
        scale_num = random.uniform(self.scale_lower_lim, self.scale_upper_lim)/1000   #Get a random number within a set of limits by which to alter the scale factor
        model.setScale(scale_origin + scale_num, scale_origin + scale_num, scale_origin + scale_num)  #Scale the model in all dimensions by scale baseline + random scale factor
        
        pos_origin = 0        #Baseline position is the origin
        pos_x = random.uniform(self.x_lower_lim, self.x_upper_lim) #Get random number to adjust "left to right" placement of model
        pos_y = random.uniform(self.y_lower_lim, self.y_upper_lim) #Get random number to adjust depth of model in the image (lower -> closer to camera)
        model.setPos(pos_origin + pos_x, pos_origin + pos_y, self.object_height)    #Set the position of the model in the scene
        
        self.models.append(model)   #Add this model to the list of models in the scene
    
    ''' Visualize the z buffer by applying a shader to the scene '''    
    def displayZBuffer(self, manager):  
        tex = Texture()   #Color texture
        dtex = Texture()  #Depth texture
        quad = manager.renderSceneInto(colortex=tex, depthtex=dtex) #Produce filter of window
        quad.setShader(Shader.load("z_buf.sha"))  #Apply shader to scene
        quad.setShaderInput("dtex", dtex)
        quad.setTexture(dtex)                     #Apply shaded depth texture to filter

    ''' Restore the regular color buffer of the image after displaying the z buffer '''
    def displayCBuffer(self, manager):
        tex = Texture()   #Color texture
        dtex = Texture()  #Depth texture
        quad = manager.renderSceneInto(colortex=tex, depthtex=dtex) #Produce filter of window
        quad.setShader(Shader.load("z_buf.sha"))  #Apply shader to scene
        quad.setShaderInput("dtex", dtex)        
        quad.setTexture(tex)                      #Apply regular color texture to filter
        
    ''' Renders a single frame as an image writable to a file '''
    def renderToPNM(self, filename=None, verbose=None):
        base.graphicsEngine.renderFrame() #Render next frame
        
        image = PNMImage()
        if verbose: print("\t\tWriting image {}".format(filename))
        if filename is not None:
            base.win.saveScreenshot(filename)   #Save image to disk
        base.win.getScreenshot(image)  #Get the screenshot in an object
        
        return image  #Return screenshot object
 
    ''' End the application automatically (normally requires user input) '''
    def stopApplicationTask(self, task):        
        taskMgr.stop() # Exit the application loop
        return Task.done

if __name__ == "__main__":        
    
    parser = argparse.ArgumentParser(description="generate images containing randomly placed 3d models")

    parser.add_argument("-v", "--verbose", help="print full console output", action="store_true")
    parser.add_argument("-d", "--depth_map", help="output a depth map of the generated image(s)", action="store_true")
    parser.add_argument("-s", "--stereo", help="generate two stereo images based on a given eye separation", action="store_true")    
    parser.add_argument("--eye_sep", help="distance of separation between two stereo images", metavar="EYE_SEPARATION", type=int, default=2)
    parser.add_argument("images_to_generate", help="number of images to generate", type=int)
    parser.add_argument("models_per_image", help="number of 3d models to render per generated image", type=int)
    parser.add_argument("--image_width", help="width in pixels of generated image (default 800)", type=int, default=800)
    parser.add_argument("--image_height", help="height in pixels of generated image(default 600)", type=int, default=600)
    parser.add_argument("--model_path", help="path to the 3d model to be rendered", default="models/panda-model")    
    parser.add_argument("--out_dir", help="path to a directory which output images will be generated in", default ="img_gen_out", metavar="OUTPUT_DIRECTORY_PATH")
    
    args = parser.parse_args()

    verbose = args.verbose    
    stereo = args.stereo
    depth = args.depth_map
    
    try:
        if stereo:
            print("\nGenerating stereo images with eye separation = {} units...".format(args.eye_sep))
        else:
            print("\nGenerating images...")
            
        seed = random.randrange(sys.maxsize) #Get seed for randomly adjusting position and scale of models that are rendered
        print("Current randomization seed: {:d}".format(seed))
        random.seed(seed)

        ''' Initialize Panda3D app '''
        app = ImageGenerator(args.images_to_generate, args.models_per_image, args.image_width, args.image_height, args.model_path, args.out_dir, stereo, args.eye_sep, depth, verbose)
        
        ''' Apply light source '''
        alight = AmbientLight('alight') #Create ambient light source
        alnp = app.render.attachNewNode(alight) #Attach to scene
        app.render.setLight(alnp) #Apply lighting to renderer

        app.run()  #Run the app
            
    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit()   #Exit the program cleanly        
