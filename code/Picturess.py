#PIL
import PIL
from PIL import Image

#import kivy

#plyer
import plyer.platforms.macosx.filechooser
#import plyer.platforms.win.filechooser
from plyer import filechooser


#TinyPng
from tinify import tinify


#Kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label


#os
import os 
import sys
import glob
import concurrent.futures
import json

#Global
#Set to True when creating the distribution app with pyinstaller 
#All contents of the folder resources must be in the code folder before using pyinstaller
PRODUCTION = False

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
    """
    A class that is resposible for adding a wtaermark to an image.

    Attributes
    ----------
    folder_path : str
        The folder that contains the image 
    watermark_path: str 
        The location of the watermark image
    folder_save_path: str
        The folder where the watermarked image will be stored

    Methods
    -------
    watermark(pImageFileName)
        Adds a watermark to the image and stores the new image in the specified folder
    
    bulkWatermark()
        Given a folder, the function cretaes a list of file_names or images
        and goes through every image and add the watermark using the watermark
        function

    """

    def __init__(self, pFolderPath, pSaveFolderPath, pWatermarkPath):
        self.folder_path = pFolderPath
        self.watermark_path = pWatermarkPath
        self.folder_save_path = pSaveFolderPath
    
    def watermark(self, pImageFileName):
        """
        A method that adds a watermark to an image 

        Parameters
        ----------
        pImageFileName : str 
            The full adress and filename of the image 

        Output
        ------
            The Watermarked image
        """

        logo_size_x_y = 0
    
        #Image
        image_file_path = self.folder_path + '/' + pImageFileName
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

        save_path = self.folder_save_path + '/' + pImageFileName
        img.save(save_path)

    def bulkWatermark(self):
        """
        Watermarks a set of images inside a folder 

        The methos goes through every file, and creates a list of files 
        the folder must only contain images. With the list of files, 
        the method watermarks every file, or image of the list. 
        """

        dir_Array = [ os.path.basename(f) for f in glob.glob(self.folder_path+"/*.*")]
        for i,image in enumerate(dir_Array):
            print( "Watermarking %d out of %d"%((i+1), len(dir_Array)) )
            self.watermark(image)
            

class MyCompressor:
    """
    This class compress images using the tinify.com API. 

    Attributes
    ----------
    folder_path : str
        The folder path of the images that are ready to compress are 
    
    folder_save_path : str 
        The folder where the images will be stored after being compressed
    
    api_key : str 
        This api key is generated in the tinify website in the developer section
    
    PLAN_TOTAL_USAGE : int 
        The Total number of compressions for the month, by default is set to 500 
    
    CMPCODE : str 
        This is a prefix added to the compressed image's filename 

    Methods
    -------
    validateKey(pKeyToValidate)
        Validates if the API KEY is correct 
    
    setAPIKey(pAPIKEY)
        Sets the API KEY of the class that the API needs
    
    compressImage(pInputFilePath, pOutputFilePath ):
        Compress a fiven images and stores it in a folder 
    
    planUsageLeft(planTotalUsage)
        REturns the number of compression left usign the api 
    
    bulkCompressing()
        Compress all the images inside a given folder 

    """
    api_key = ""
    PLAN_TOTAL_USAGE = 500
    CMPCODE ="cmp-" 

    def __init__(self, pFolderPath, pSaveFolderPath):
        self.folder_path = pFolderPath
        self.folder_save_path = pSaveFolderPath

    def validateKey(self, pKeyToValidate):
        """
        Validates a given API key 

        Using the API, the key is send with a dummy request 
        to the service, and returns True if the key is valid 

        Parameters
        ----------
            pKeyToValidate : str
                A key to validate 

        Raises / Output 
        ------ 

            tinify.Error 
                API error, depends of the error a message is displayed

        """
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
        tinify.key = pAPIKEY


    def compressImage(self, pInputFilePath, pOutputFilePath ):
        """
        Compress an image using the tinify API

        Compress an image and stores it, in a given folder path 

        Parameters
        ----------
            pInputFilePath : str 
                The image's file path 
            
            pOutputFilePath : str
                The new compressed images's file path 


        Raises
        ------ 
            tinify.Error 
                API error, depends of the error a message is displayed

        """
        try:
            source = tinify.from_file(pInputFilePath)

            # resize = source.resize(
            #     method="fit",
            #     width=980,
            #     height=700
            # )
            #source.preserve("creation")

            source.to_file(pOutputFilePath)

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


    def planUsageLeft(self, pPlanTotalUsage):
        """
        Returns the number of compressions left using the API  

        Parameters
        ----------
            pPlanTotalUsage : int  
                Monthly normal plan usage, normally is set to 500 

        Raises
        ------ 
            tinify.Error 
                API error, depends of the error a message is displayed

        """
        try:
            compressions_this_month = pPlanTotalUsage - tinify.compression_count
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
        """
        Compress a list of images inside a given folder  

        Parameters
        ----------
            folder_path : str 
                Path of the folder that has the images 
            folder_save_path : str
                Path of the folder to store the images 
        """
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


class MyFileHandler:
    """
    A class responible to handle files and file choosers 

    Methods
    -------
        openFile()
            Opens a file chooser, and returns the file that the user choose. 

        openFolder(parameter)
            Opens the plyer filechooser and returns the path of the folder that 
            the user choose. 
        
        newFolder(pDirectoryPath)
            Creates the new folder where the images are going to be saved 
        
        openJsonFile(pOpenMode)
            Returns the pointer of the json file containing the API Key 
        
        closeJsonFile(pFilePointer)
            Closes a Json File
        
        loadJsonData()
            Returns the date inside the json file
        
        changeJsonFileKey()
            Modifies the key inside the json file 
        
        loadResourcePath(pResourceName)
            Returns the path of the watermak image 
    """
    def openFile(self):
        """Opens a file chooser, and returns the file that the user choose. """
        image_file_path = filechooser.open_file(title="Select a new Watermark Image")

        if image_file_path is None or image_file_path == []:
            return False
        return image_file_path[0] 
    
    def changeWatermark(self, pNewWatermarkPath):
        old_watermark_path = self.loadResourcePath("watermark.png")

        try:
            new_watermark_image = PIL.Image.open(pNewWatermarkPath, formats=['png','jpeg'])
            new_watermark_image.save(old_watermark_path)
        except TypeError as e:
            print(e)
            return False
        except PIL.UnidentifiedImageError as e:
            print(e)
            return False
        return True


    def openFolder(self):
        """Opens a file chooser, and returns the folder that the user choose. """

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
        """
        Create the save folder for the new images 

        Parameters
        ----------
            pDirectoryPath : str 
                The path where the new folder will be created

        """
        if not os.path.exists( pDirectoryPath ):
            os.makedirs(pDirectoryPath, exist_ok=False)

    def loadResourcePath(self, pResourceName):
        """
        Returns the path of the watermak image 

        Long Description 

        Parameters
        ----------
            pIsProduction : bool 
                True for production path 
                False for develepment path 
            pResourceName : str
                Name of the resource to load
        """
        py_file_path = os.path.dirname(os.path.abspath(__file__))
        resource_path = os.path.dirname(py_file_path)

        if PRODUCTION:
            resource_path += "/" + pResourceName
        else:
            resource_path += "/resources/" + pResourceName
        return resource_path

    def openJsonFile(self, pOpenMode):
        """
        Opens a json file and returns the file poiter

        Long Description 

        Parameters
        ----------
            pOpenMode : str 
                Open mode of the file 
                r : Read 
                w : Write 

        """
        json_path = self.loadResourcePath("data.json")
        file_pointer = open(json_path, pOpenMode)
        return file_pointer

    def closeJsonFile(self, pFilePointer):
        """
        Closes a file 

        

        Parameters
        ----------
            pFilePointer : file 
                File pointer
        """
        pFilePointer.close()

    def loadJsonData(self):
        """Opens a json file and returns it's contents"""
        file_pointer = self.openJsonFile('r')
        data = json.load(file_pointer)
        self.closeJsonFile(file_pointer)
        return data    
    
    def changeJsonFileKey(self, pNewAPIKey):
        """
        Changes the key inside the json file 

        Parameters
        ----------
            pNewAPIKey : str 
                The New Key 
        """
        data = self.loadJsonData()
        data['tinify_api_key'] = pNewAPIKey

        file_pointer = self.openJsonFile('w')
        json.dump(data, file_pointer)
        self.closeJsonFile(file_pointer)


#This Class controls the main page of the app 
class PicturessMainPage(BoxLayout):
    """
    This class handles the interaction between the GUI and the models

    You can say that this class serves a a controller 
    between the view(GUI) and the model(MyFileHandler, MyCompressor..)

    Attributes
    ----------
        FILE_HANDLER_INSTANCE : MyFileHandler
            Object resposible for hanlding files and find folder paths 
        
        WATERMARK_INSTANCE : MyWatermark
            Object resposible for watermarking images 
        
        COMPRESSOR_INSTANCE : MyCompressor 
            Object resposible wor compressing images 
        
        EXECUTOR : ThreadPoolExecutor
            Resposible for creating threads for the file chooser and other 
            functions that can't run with the kivy main thread.
        
        btns_enable_compression : Boolean
            Resposible to lock or unlock the buttons on the GUI when compressing 
            or validating the key. 
        
        compress_with_watermark : Boolean 
            Option to watermark the images at the same time when compressing the images
        
        watermark_path : str
            The path of the image or ican that is going to be used as the watermark 


    Methods
    -------
        validateKey()
            Validates the key when the app starts 

        loadAPIKey()
            Returns the key inside the Json file 
        
        onSwitchActive(pWidget)
            Changes the option to watermark or not the compressed images
        
        onButtonClick(pWidget)
            Button click handler
        
        setAllDirectoryPaths() 
            Opens the filechooser and sets the images folder and the save folder
            for Mycompressor and MyWatermark
        
        start()
            Start the process to compress and watermark the images 

        onEnterChangeKey(pInstance)
            Resposible for changing the API key with the new input
        
        popChangeAPIKey(pTitle)
            Resposbile for showing the PopUp to input the new key
        
        callPops(pTitle, pContent)
            Shows popups to the user, with information or alerts from the app 

    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.FILE_HANDLER_INSTANCE = MyFileHandler()

        self.watermark_path = self.FILE_HANDLER_INSTANCE.loadResourcePath("watermark.png")

        self.WATERMARK_INSTANCE = MyWatermark("","", self.watermark_path)
        self.COMPRESSOR_INSTANCE = MyCompressor("", "")
        self.EXECUTOR = concurrent.futures.ThreadPoolExecutor()

        #Starts Thread 
        api_key = self.loadAPIKey()
        future = self.EXECUTOR.submit(self.validateKey,api_key)
        future.add_done_callback( self.validateKeyAux)

    #Kivy Label Messages
    label_api_messages = StringProperty("API Messages") 
    label_app_alerts = StringProperty("APP Alerts") 

    lab_left_images = StringProperty("Images")
    lab_left_waterm = StringProperty("Watermark Images?")

    lab_right_compr_eta = StringProperty("Waiting")
    lab_right_compr_inf = StringProperty("Images will be stored at:")

    lab_right_save_fldr = StringProperty("Images are taken from:")
    
    #Variables 
    startup_key_valid  = False
    btns_enable_compression = BooleanProperty(False)
    compress_with_watermark = True 
    watermark_path     =""



    def validateKey(self, pKey):
        """
        Validates the key when the app starts and when the user changes it 

        Creates a thread that is in charge to 
        display a message if the key is invalid. 
        And also the thread  validates the key with the api 

        """
        validation = self.COMPRESSOR_INSTANCE.validateKey(pKey)
        return validation

    @mainthread
    def validateKeyAux(self, pX):
        """
        This class is the callback for the process of validating the Key 

        After the key is validated, the method unlocks the buttons,
        if the key is invalid the method displays a message to the user 
        indicating that the key is wrong. 

        Parameters
        ----------
            pX : Function thread response 
                Holds the response for the method that was on the created thread.   
        """
    
        result = pX.result()
        print("validate key aux: result :", result)

        if result[0]:
            self.COMPRESSOR_INSTANCE.setAPIKey(result[2])
            self.FILE_HANDLER_INSTANCE.changeJsonFileKey(result[2])
            self.btns_enable_compression = True
            self.startup_key_valid = True
        else:
            if self.startup_key_valid:
                self.callPops("Error Validating API KEY", "The key is invalid,\nthe app will still use the last working key")
            else:
                self.btns_enable_compression = False
                self.callPops("Error Validating API KEY", "Please set a correct API KEY First")
                print("ValidateKeyAux: ",pX.result())
        self.btns_enable_compression = True


    def loadAPIKey(self):
        """ Returns the key inside the Json file """
        data = self.FILE_HANDLER_INSTANCE.loadJsonData()
        return data['tinify_api_key']

    def onSwitchActive(self, pWidget):
        """
        Changes the option to watermark or not the compressed images 

        Parameters
        ----------
            pWidget : Widget 
               The instance of the switch widget in the gui 

        """
        self.compress_with_watermark = pWidget.active
        print("Watermark? ", pWidget.active)

    def onButtonClick(self, pWidget):
        """
        Button click handler

        All buttons use this Method, every button has a different id, 
        so depending of the ID different methods are called. 

        Parameters
        ----------
            pWidget : Widget 
                Button pressed so we can get the Id 
        """
        btn_id = pWidget.ids["btn_id"]
        
        if btn_id == "open_folder_btn":
            print("Open Folder")
            self.setAllDirectoryPaths()

        if btn_id == "start_image_compression":
            print("Start Compression")
            self.start()

        if btn_id == "btn_change_api_key":
            print("Change API KEY")
            self.btns_enable_compression = False
            self.popChangeAPIKey("Change API key")

        if btn_id == "btn_change_watermark":
            print("Change Watermark")
            self.btns_enable_compression = False
            self.changeWatermarkLogo()

    def changeWatermarkLogo(self):
        print("changeWatermarkLogo: changing  watermark logo ")
        new_watermark_path = self.FILE_HANDLER_INSTANCE.openFile() 
        if new_watermark_path:
            print(new_watermark_path)
            result = self.FILE_HANDLER_INSTANCE.changeWatermark(new_watermark_path)

            if not result:
                self.callPops("File Format Error", "Image format not supported \nOnly PNG or JPEG")

            print("changeWatermarkLogo: result",result)
            self.btns_enable_compression = True
            self.watermark_path = self.FILE_HANDLER_INSTANCE.loadResourcePath("watermark.png")
            self.ids.image_viewer.reload()

        else:
            print("No changes to watermark")

            self.btns_enable_compression = True

        #Open File Chooser


    def setAllDirectoryPaths(self):
        """
        Opens the filechooser and sets the images folder and the save folder
        for Mycompressor and MyWatermark
        """

        open_folder, save_folder = self.FILE_HANDLER_INSTANCE.openFolder() 

        if open_folder != 0 :

            self.WATERMARK_INSTANCE.folder_path = save_folder
            self.WATERMARK_INSTANCE.folder_save_path = save_folder
            self.COMPRESSOR_INSTANCE.folder_path = open_folder
            self.COMPRESSOR_INSTANCE.folder_save_path = save_folder

            self.lab_right_compr_inf = "Images will be stored at: \n " + save_folder
            self.lab_right_save_fldr = "Images are taken from: \n "+ open_folder

        else:
            print("No eligió ningún folder")

    
    @mainthread
    def setAllDirectoryPathsAux(self, pX):
        """
        This is the callback function for the find Image method

        This just displays the message of the function that 
        was created on a different thread. 
        """
        print(pX)

    def start(self):
        """
        Start the process to compress and watermark the images 

        Creates a Thread that is in charge to 
        display the filechooser so the user can
        choose the folder with the images. 

        """
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
        """
        Runs the methods to bulk compress and watermark images on a different thread 

        """
        self.COMPRESSOR_INSTANCE.planUsageLeft(500)
        print("Compressing Images")

        self.COMPRESSOR_INSTANCE.bulkCompressing()

        if( self.compress_with_watermark ):
            print("Watermarking Images")
            self.WATERMARK_INSTANCE.bulkWatermark()

    @mainthread
    def finishAux(self, pX):
        """
        The callback function for the Start method 
        
        Displays a message to the user commuicating that all 
        processes are complete. 

        And unlocks the buttons of the gui 

        Parameters
        ----------
            px : Thread response 
                Holds the message from the method that was 
                running in the other thread
        """
        print(pX)
        self.lab_right_compr_eta = "Waiting"
        self.btns_enable_compression = True
        self.lab_right_compr_inf = "Images will be stored at:" 
        self.lab_right_save_fldr = "Images are taken from:"
        self.deletePath()
        self.callPops("Done", "Your Images are ready")


    def deletePath(self):
        """
        Resets the folders for the different objects 

        Resets the images folder and the save folder 
        for the objects in charge of compressing and        
        watermarkng the images. And also changes the labels 
        of the GUI. 

        """
        
        self.WATERMARK_INSTANCE.folder_path = ""
        self.WATERMARK_INSTANCE.folder_save_path = ""

        self.COMPRESSOR_INSTANCE.folder_path = ""
        self.COMPRESSOR_INSTANCE.folder_save_path = ""
    
    #Todo
    #Validating if the user changed the KEY
    #IF there was no change then do nothing 
    #If the key is invalid then do nothing 
    def onEnterChangeKey(self, pInstance):
        """
        Resposible for changing the API key with the new input

        When the user inputs the new key and hit enter, this method validates 
        the key and changes it. 

        Parameters
        ----------
            pInstance : TextInput 
                TextInput that hold the text of the key 

        """
        newKey = pInstance.text
        popup = pInstance.parent.parent.parent.parent

        if newKey.strip() != "" :
            popup.dismiss()
            print("PICTURESS_APP ON_ENTER VALUE:",newKey)
            #self.FILE_HANDLER_INSTANCE.changeJsonFileKey(newKey)

            #Starts Thread 
            self.lab_right_compr_eta = "Validating Key"
            future = self.EXECUTOR.submit(self.validateKey,newKey)
            future.add_done_callback( self.validateKeyAux)
        else:
            pInstance.text = ""
            self.btns_enable_compression = False



    def popChangeAPIKey(self,pTitle):
        """
        Resposbile for showing the PopUp to input the new key

        Long Description 

        Parameters
        ----------
            pTitle : string 
                Title of the popup
        """

        textinput = TextInput( multiline=False)
        textinput.bind(on_text_validate=self.onEnterChangeKey)

        label   = Label(text="Write the new Key and hit enter to validate. \nOr click outside to dismiss",halign= 'left')

        box_layout = BoxLayout(orientation="vertical", size_hint= (1,0.9))
        box_layout.add_widget(textinput)
        box_layout.add_widget(label)

        pop=Popup(content=box_layout,title=pTitle,auto_dismiss=True,size_hint=(.5, .25))
        pop.open()


    #Todo
    #Create a better PopUp
    #With a layout and change the button for a label for displaying messages 
    def callPops(self,pTitle,pConten):
        """
         Shows popups to the user, with information or alerts from the app. 

        Parameters
        ----------
            pTitle : string 
                Title for the popup
            
            pContent : string 
                COntent of the popup ie message or alert 
        """

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
