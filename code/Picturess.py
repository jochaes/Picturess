#KEY = hlH2Tr7d0p0gpnPsypV53Klp5kR3pbPv
#PIL

import PIL
from PIL import Image
import kivy

#plyer
import plyer.platforms.macosx.filechooser
#import plyer.platforms.win.filechooser

from plyer import filechooser

#TinyPng
from tinify import AccountError, tinify

#Kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.factory import Factory


#os
import os 
import sys
import glob
import concurrent.futures
import json

#--------------------------------- Overrrides the certificate location for the request library -----------------------
def overrideWhere():
    """ overrides certifi.core.where to return actual location of cacert.pem"""
    # change this to match the location of cacert.pem
    cert_path = "certifi/cacert.pem"
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, cert_path)
    

# is the program compiled?
if hasattr(sys, "frozen"):
    import certifi.core

    os.environ["REQUESTS_CA_BUNDLE"] = overrideWhere()
    certifi.core.where = overrideWhere

    # delay importing until after where() has been replaced
    import requests.utils
    import requests.adapters
    # replace these variables in case these modules were
    # imported before we replaced certifi.core.where
    requests.utils.DEFAULT_CA_BUNDLE_PATH = overrideWhere()
    requests.adapters.DEFAULT_CA_BUNDLE_PATH = overrideWhere()
#--------------------------------------------------------------------------------------------------------------------



class MyWatermark:

    def __init__(self, pFolderPath, pSaveFolderPath, pWatermarkPath):
        self.folder_path = pFolderPath
        self.watermark_path = pWatermarkPath
        self.folder_save_path = pSaveFolderPath
    
    def watermark(self, pImageTitle):
        logo_size_x_y = 0
    

        #Image
        image_file_path = self.folder_path + '/' + pImageTitle
        img = PIL.Image.open(image_file_path)
        my_height, my_width = img.size
        
        print("Imagen a Watermark: ", image_file_path)
        print("Logo Path", self.watermark_path)

        if(my_height < my_width):
            logo_size_x_y = int(my_height * 0.25) #Logo will be 20% of the  image's height 
        else:
            logo_size_x_y = int(my_width * 0.25)

        #Logo
        #logo_path = '../watermark/logo_w_letters.png'   #Path del Logo 
        logo_path = self.watermark_path
        logo_size = (logo_size_x_y,logo_size_x_y)                           #Logo Size
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
        dir_Array = [ os.path.basename(f) for f in glob.glob(self.folder_path+"/*.*")]
        for i,image in enumerate(dir_Array):
            print( "Watermarking %d out of %d"%((i+1), len(dir_Array)) )
            self.watermark(image)
            

class MyCompressor:

    def __init__(self, pFolderPath, pSaveFolderPath):
        self.folder_path = pFolderPath
        self.folder_save_path = pSaveFolderPath

    def validateKey(self, pKeyToValidate):
        try:
            tinify.key = pKeyToValidate
            tinify.validate()
        except tinify.Error as e:
        # Validation of API key failed.
            error_string  = "Validation Error: "+ e.message
            print (error_string)
            return (False, error_string, pKeyToValidate)
        return (True, "", pKeyToValidate)

    
    def setAPIKey(self, pAPIKEY):
        self.api_key = pAPIKEY

    api_key = ""
    PLAN_TOTAL_USAGE = 500
    CMPCODE ="cmp-" 

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
    #_file_selection_dialog = "Select Folder"

    def openFolder(self):

        #Get Image Folder Path
        # image_folder_path = self.get_path()
        
        image_folder_path = filechooser.choose_dir(title="Select a Folder")
        
        print('Response filechooser:')
        print(image_folder_path)

        if image_folder_path is None or image_folder_path == []:
            return (0,0)

        #Save Folder Path
        save_directory =  os.path.dirname(image_folder_path[0]) + "/ready_to_upload"

        #Check if path exists
        return (image_folder_path[0], save_directory)

    def newFolder(self, pDirectoryPath):
        if not os.path.exists( pDirectoryPath ):
            os.makedirs(pDirectoryPath, exist_ok=False)

    def openJsonFile(self, pOpenMode):
        json_path = os.path.dirname(os.path.abspath(__file__)) + "/data.json"
        file_pointer = open(json_path, pOpenMode)
        return file_pointer

    def closeJsonFile(self, pFilePointer):
        pFilePointer.close()


    #Opens a JSON file and returns the data 
    def loadJsonData(self):
        file_pointer = self.openJsonFile('r')
        data = json.load(file_pointer)
        self.closeJsonFile(file_pointer)
        return data    
    
    def changeJsonFileKey(self, pNewAPIKey):
        data = self.loadJsonData()
        data['tinify_api_key'] = pNewAPIKey

        file_pointer = self.openJsonFile('w')
        json.dump(data, file_pointer)
        self.closeJsonFile(file_pointer)


# class ChangeKeyPopup(Popup):

#     def changeApiKey(self, pInstance):
#         self.api_key = pInstance.text
#         print("ChangeKeyPopup: ", pInstance.text )
#         self.dismiss()

#     def deleteApiKey(self, instance):
#         self.api_key =  ""




#This Class controls the main page of the app 
class PicturessMainPage(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.FILE_HANDLER_INSTANCE = MyFileHandler()

        self.watermark_path = self.resourcePath("logo_w_letters.png", True)

        self.WATERMARK_INSTANCE = MyWatermark("","", self.watermark_path)
        self.COMPRESSOR_INSTANCE = MyCompressor("", "")
        self.EXECUTOR = concurrent.futures.ThreadPoolExecutor()

        #Starts Thread 
        self.lab_right_compr_eta = "Validatiing Key"
        future = self.EXECUTOR.submit(self.validateKey)
        future.add_done_callback( self.validateKeyAux)

    def validateKey(self):
        #Validate API KEY
        stored_api_key = self.loadAPIKey()
        validation = self.COMPRESSOR_INSTANCE.validateKey(stored_api_key)
        return validation

    @mainthread
    def validateKeyAux(self, pX):
        result = pX.result()

        if result[0]:
            self.COMPRESSOR_INSTANCE.setAPIKey(result[2])
            self.btns_enable_compression = True

        else:
            self.btns_enable_compression = False
            self.callPops("Error Validating API KEY", "Please set a correct API KEY First")
            print("validateKeyAux: ",pX.result())


    
    
    #Utilitary Objects 
    CHANGE_KEY_POPUP_INSTANCE = None
    FILE_HANDLER_INSTANCE = None
    WATERMARK_INSTANCE = None
    COMPRESSOR_INSTANCE = None
    EXECUTOR = None
    
    #Kivy Label Messages
    label_api_messages = StringProperty("API Messages") 
    label_app_alerts = StringProperty("APP Alerts") 

    lab_left_images = StringProperty("Images")
    lab_left_waterm = StringProperty("Watermark Images?")

    lab_right_compr_eta = StringProperty("Waiting")
    lab_right_compr_inf = StringProperty("Images will be stored at:")

    lab_right_save_fldr = StringProperty("Images are taken from:")
    
    #Variables 
    btns_enable_compression = BooleanProperty(False)
    compress_with_watermark = True 
    watermark_path     =""

    def loadAPIKey(self):
        data = self.FILE_HANDLER_INSTANCE.loadJsonData()
        return data['tinify_api_key']

    def resourcePath(self, pRelativePath, pTestPath):
        if pTestPath:
            py_file_path = os.path.dirname(os.path.abspath(__file__))
            watermark_path =  os.path.dirname(py_file_path) + "/watermark/logo_w_letters.png"
            return watermark_path
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, pRelativePath)

    def onSwitchActive(self, pWidget):
        self.compress_with_watermark = pWidget.active
        print("Watermark? ", pWidget.active)

    def onButtonClick(self, pWidget):
        btn_id = pWidget.ids["btn_id"]
        
        if btn_id == "open_folder_btn":
            print("Open Folder")
            self.findImageFolder()

        if btn_id == "start_image_compression":
            print("Start Compression")
            self.start()

        if btn_id == "btn_change_api_key":
            print("Change API KEY")
            self.popChangeAPIKey("Change API key")

    
    def findImageFolder(self):
        open_folder, save_folder = self.FILE_HANDLER_INSTANCE.openFolder() 

        if open_folder != 0 :

            self.WATERMARK_INSTANCE.folder_path = save_folder
            self.WATERMARK_INSTANCE.folder_save_path = save_folder
            self.COMPRESSOR_INSTANCE.folder_path = open_folder
            self.COMPRESSOR_INSTANCE.folder_save_path = save_folder

            self.lab_right_compr_inf = "Images will be stored at: \n " + save_folder
            self.lab_right_save_fldr = "Images are taken from: \n "+ open_folder

            # print(open_folder, "OMG", save_folder)
        else:
            print("No eligió ningún folder")

    
    @mainthread
    def findImageFolderAux(self, pX):
        print(pX)

    def start(self):
        print("Starting")
        self.btns_enable_compression = False

        save_path = self.WATERMARK_INSTANCE.folder_save_path
        if( save_path != "" ):
            #Create new directory to save images
            self.FILE_HANDLER_INSTANCE.newFolder(save_path)
            
            #Starts Thread 
            self.lab_right_compr_eta = "Processing Images"
            future = self.EXECUTOR.submit(self.startAux)
            future.add_done_callback( self.finishAux)
            # self.startAux()

        else:
            print("You must pick the folder")
            self.btns_enable_compression = True
            self.deletePath()
            self.callPops("Wait! :D", "You need to select a folder with images first.")
    
    
    def startAux(self):
        self.COMPRESSOR_INSTANCE.planUsageLeft(500)
        print("Compressing Images")

        self.COMPRESSOR_INSTANCE.bulkCompressing()

        if( self.compress_with_watermark ):
            print("Watermarking Images")
            self.WATERMARK_INSTANCE.bulkWatermark()

    @mainthread
    def finishAux(self, pX):
        print(pX)
        self.lab_right_compr_eta = "Waiting"
        self.btns_enable_compression = True
        self.lab_right_compr_inf = "Images will be stored at:" 
        self.lab_right_save_fldr = "Images are taken from:"
        self.deletePath()
        self.callPops("Done", "Your Images are ready")



    def deletePath(self):
        
        self.WATERMARK_INSTANCE.folder_path = ""
        self.WATERMARK_INSTANCE.folder_save_path = ""

        self.COMPRESSOR_INSTANCE.folder_path = ""
        self.COMPRESSOR_INSTANCE.folder_save_path = ""
    
    def onEnterChangeKey(self, pInstance):
        newKey = pInstance.text
        popup = pInstance.parent.parent.parent.parent
        popup.dismiss()
        print("PICTURESS_APP ON_ENTER VALUE:",newKey)
        self.FILE_HANDLER_INSTANCE.changeJsonFileKey(newKey)

        #Starts Thread 
        self.lab_right_compr_eta = "Validating Key"
        future = self.EXECUTOR.submit(self.validateKey)
        future.add_done_callback( self.validateKeyAux)


    def popChangeAPIKey(self,pTitle):
        textinput = TextInput( multiline=False)
        textinput.bind(on_text_validate=self.onEnterChangeKey)

        label   = Label(text="Write the new Key and hit enter to validate. \nOr click outside to dismiss",halign= 'left')

        box_layout = BoxLayout(orientation="vertical", size_hint= (1,0.9))
        box_layout.add_widget(textinput)
        box_layout.add_widget(label)

        pop=Popup(content=box_layout,title=pTitle,auto_dismiss=True,size_hint=(.5, .25))
        pop.open()

        #Factory.ChangeKeyPopup.open(self.CHANGE_KEY_POPUP_INSTANCE)
        #print("popChangeAPIKey: ",self.CHANGE_KEY_POPUP_INSTANCE.api_key)



    def callPops(self,pTitle,pConten):
        cont=Button(text=pConten)
        pop=Popup(title=pTitle,content=cont,size_hint=(.5, .3),auto_dismiss=True)
        pop.open()
        cont.bind(on_press=pop.dismiss)

    
#App Class
class PicturessApp(App):
    #uncomment on production 
    #icon = 'logo.ico'
    pass

#Runs the app 
PicturessApp().run()
