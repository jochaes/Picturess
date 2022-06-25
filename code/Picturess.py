#PIL
from webbrowser import MacOSX
import PIL
from PIL import Image

#plyer
import plyer.platforms.win.filechooser
from plyer import filechooser



#TinyPng
from tinify import tinify

#Kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp
from kivy.uix.button import Button

#os
import os 
import sys
import glob
import concurrent.futures

def override_where():
    """ overrides certifi.core.where to return actual location of cacert.pem"""
    # change this to match the location of cacert.pem
    cert_path = "certifi/cacert.pem"
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, cert_path)
    


# is the program compiled?
if hasattr(sys, "frozen"):
    import certifi.core

    os.environ["REQUESTS_CA_BUNDLE"] = override_where()
    certifi.core.where = override_where

    # delay importing until after where() has been replaced
    import requests.utils
    import requests.adapters
    # replace these variables in case these modules were
    # imported before we replaced certifi.core.where
    requests.utils.DEFAULT_CA_BUNDLE_PATH = override_where()
    requests.adapters.DEFAULT_CA_BUNDLE_PATH = override_where()



class MyWatermark:

    def __init__(self, pFolderPath, pSaveFolderPath, pWatermarkPath):
        self.folder_path = pFolderPath
        self.watermark_path = pWatermarkPath
        self.folder_save_path = pSaveFolderPath
    
    def watermark(self, pImageTitle):

        #Image
        image_file_path = self.folder_path + '/' + pImageTitle
        img = PIL.Image.open(image_file_path)
        my_height, my_width = img.size
        
        print("Imagen a Watermark: ", image_file_path)
        print("Logo Path", self.watermark_path)


        #Logo
        #logo_path = '../watermark/logo_w_letters.png'   #Path del Logo 
        logo_path = self.watermark_path
        logo_size = (300,300)                           #Logo Size
        logo_img = PIL.Image.open(logo_path)            #Logo 
        logo_img.thumbnail(logo_size)                   #Logo resize

        #Logo Position
        pos_y = my_height -  logo_size[0] - 15
        pos_x = my_width  - logo_size[1] - 15

        # if img.mode != 'RGB':
        #     img = img.convert('RGB')
        
        #Paste logo onto image
        img.paste(logo_img, (pos_y, pos_x), logo_img.convert('RGBA'))

        #save_path = asksaveasfilename()

        save_path = self.folder_save_path + '/' + pImageTitle

        img.save(save_path)
    
    def bulkWatermark(self):
        dirArray = [ os.path.basename(f) for f in glob.glob(self.folder_path+"/*.*")]
        for i,image in enumerate(dirArray):
            print( "Watermarking %d out of %d"%((i+1), len(dirArray)) )
            self.watermark(image)
            

class MyCompressor:
    tinify.key = "hlH2Tr7d0p0gpnPsypV53Klp5kR3pbPv"
    PLAN_TOTAL_USAGE = 500
    CMPCODE ="cmp-" 

    def __init__(self, pFolderPath, pSaveFolderPath):
        self.folder_path = pFolderPath
        self.folder_save_path = pSaveFolderPath

        try:
            tinify.key = "hlH2Tr7d0p0gpnPsypV53Klp5kR3pbPv"
            tinify.validate()
        except tinify.Error:
        # Validation of API key failed.
            print ("Validation Error")
            pass


    #input_path = Path of the image to compress 
    #output_path = To store the compressed image 
    def compressImage(self, input_path, output_path ):
        try:
            source = tinify.from_file(input_path)

            # resize = source.resize(
            #     method="fit",
            #     width=980,
            #     height=700
            # )
            #source.preserve("creation")

            source.to_file(output_path)

            compressions_this_month = 500 - tinify.compression_count
            print("%d compressions left"%(compressions_this_month))
            return True
        except tinify.AccountError:
            # Verify your API key and account limit.
            print ("Invalid KEY")
            return False
        except tinify.ClientError:
            print("File type not supported")
            return False
        except tinify.ServerError:
            print("Temporary issue with the Tinify API.")
            return False
        except tinify.ConnectionError as e:
            print("A network connection error occurred.\n", e)
            return False
        except Exception  as e:
            print("Something else went wrong, unrelated to the Tinify API.\n",e)
            return False

    #Returns the number of compressions left using the api
    def planUsageLeft(self, planTotalUsage):
        try:
            compressions_this_month = planTotalUsage - tinify.compression_count
            print("%d compressions left"%(compressions_this_month))
            return True 
        except tinify.AccountError:
            # Verify your API key and account limit.
            print ("Verify your API key and account limit.")
            return False
        except tinify.ClientError:
            print("Check your source image and request options.")
            return False
        except tinify.ServerError:
            print("Temporary issue with the Tinify API.")
            return False     
        except tinify.ConnectionError:
            print("A network connection error occurred.")
            return False 
        except Exception:
            print("Something else went wrong, unrelated to the Tinify API.")
            return False

    #Gets a path array of images and calls "compressImage" to compress every image
    #dirPath: Directory path 
    #dirArr: Path Array for images in the directory
    def bulkCompressing(self):
        dirArr = [ os.path.basename(f) for f in glob.glob(self.folder_path+"/*.*")]

        for i,image in enumerate(dirArr):
            print( "Compressing %d out of %d"%((i+1), len(dirArr)) )
            
            input_Path = self.folder_path +'/'+image   
            output_Path = self.folder_save_path + '/' + self.CMPCODE + image

            print(input_Path)
            print(output_Path)

            x = self.compressImage(input_Path, output_Path)

            #Compress every image and stores it in the same directory
            if( not x):
                print( "An unexpected error was found. Compression Cancelled" )
                return 

#https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file

# def resource_path(relative_path):
#     try:
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")
#     return os.path.join(base_path, relative_path)


# # wtmarkPath = resource_path("logo_w_letters.png")
# wtmarkPath = "../watermark/logo_w_letters.png"

# #messagebox.showerror('Python Error', wtmarkPath)
# wtmrk = MyWatermark("","", wtmarkPath)
# cmprssr = MyCompressor("", "")

class MyFileHandler:
    _file_selection_dialog = "Select Folder"

    def openFolder(self):

        #Get Image Folder Path
        # image_folder_Path = self.get_path()
        
        image_folder_Path = filechooser.choose_dir(title="Select a Folder")

        if image_folder_Path is None:
            return (0,0)

        #Save Folder Path
        save_directory =  os.path.dirname(image_folder_Path[0]) + "/ready_to_upload"

        #Check if path exists
        return (image_folder_Path[0], save_directory)

    

    def newFolder(self, dir_path):
        if not os.path.exists( dir_path ):
            os.makedirs(dir_path, exist_ok=False)


#This Class controls the main page of the app 
class PicturessMainPage(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.watermark_path = self.resource_path("logo_w_letters.png", False)
        self.watermark_instance = MyWatermark("","", self.watermark_path)
        self.comprssor_instance = MyCompressor("", "")

        self.file_handler_instance = MyFileHandler()
        self.executor = concurrent.futures.ThreadPoolExecutor()

    file_handler_instance = None
    watermark_instance = None
    comprssor_instance = None
    watermark_path     =""
    executor = None

    lab_left_images = StringProperty("Images")
    lab_left_waterm = StringProperty("Watermark Images?")

    lab_right_compr_eta = StringProperty("Waiting")
    lab_right_compr_inf = StringProperty("Images will be stored at:")

    lab_right_save_fldr = StringProperty("Images are taken from:")
    

    btns_enable_compression = BooleanProperty(True)
    compress_with_watermark = True 

    def resource_path(self, relative_path, testPath):
        if testPath:
            py_file_path = os.path.dirname(os.path.abspath(__file__))
            watermark_path =  os.path.dirname(py_file_path) + "/watermark/logo_w_letters.png"
            return watermark_path
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def on_switch_active(self, widget):
        self.compress_with_watermark = widget.active
        print("Watermark? ", widget.active)

    def on_button_click(self, widget):
        btn_id = widget.ids["btn_id"]
        

        if btn_id == "open_folder_btn":
            print("Open Folder")
            self.find_Image_folder()

        if btn_id == "start_image_compression":
            print("Start Compression")
            self.start()
    
    def find_Image_folder(self):
        open_folder, save_folder = self.file_handler_instance.openFolder() 
        #open_folder, save_folder = ('/Users/d4n11083/Desktop/testImages','/Users/d4n11083/Desktop/ready_to_upload')

        if open_folder != 0 :

            self.watermark_instance.folder_path = save_folder
            self.watermark_instance.folder_save_path = save_folder
            self.comprssor_instance.folder_path = open_folder
            self.comprssor_instance.folder_save_path = save_folder

            self.lab_right_compr_inf = "Images will be stored at: \n " + save_folder
            self.lab_right_save_fldr = "Images are taken from: \n "+ open_folder

            # print(open_folder, "OMG", save_folder)
        else:
            print("No eligió ningún folder")

    
    @mainthread
    def find_image_folder_aux(self, x):
        print(x)

    def start(self):
        print("Starting")
        self.btns_enable_compression = False
        save_path = self.watermark_instance.folder_save_path
        if( save_path != "" ):
            #Create new directory to save images
            self.file_handler_instance.newFolder(save_path)
            
            #Starts Thread 
            self.lab_right_compr_eta = "Processing Images"
            future = self.executor.submit(self.start_aux)
            future.add_done_callback( self.finish_aux)
            # self.start_aux()

        else:
            print("You must pick the folder")
            self.btns_enable_compression = True
            self.delete_path()
            self.call_pops("Wait! :D", "You need to select a folder with images first.")
    
    
    def start_aux(self):
        self.comprssor_instance.planUsageLeft(500)
        print("Compressing Images")

        self.comprssor_instance.bulkCompressing()

        if( self.compress_with_watermark ):
            print("Watermarking Images")
            self.watermark_instance.bulkWatermark()

    @mainthread
    def finish_aux(self, x):
        print(x)
        self.lab_right_compr_eta = "Waiting"
        self.btns_enable_compression = True
        self.lab_right_compr_inf = "Images will be stored at:" 
        self.lab_right_save_fldr = "Images are taken from:"
        self.delete_path()
        self.call_pops("Done", "Your Images are ready")



    def delete_path(self):
        
        self.watermark_instance.folder_path = ""
        self.watermark_instance.folder_save_path = ""

        self.comprssor_instance.folder_path = ""
        self.comprssor_instance.folder_save_path = ""


    def call_pops(self,tit,conten):
        cont=Button(text=conten)
        pop=Popup(title=tit,content=cont,size_hint=(.5, .3),auto_dismiss=True)
        pop.open()
        cont.bind(on_press=pop.dismiss)




    
#App Class
class PicturessApp(App):
    icon = '../images/logo.ico'
    pass

#Runs the app 
PicturessApp().run()
