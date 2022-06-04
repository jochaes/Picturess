#PIL
from tkinter import filedialog
import PIL
from PIL import Image

#TinyPng
import tinify

#Tkinter
from tkinter import * 
from tkinter import dialog

import os 
import sys
import glob



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
        except tinify.ConnectionError:
            print("A network connection error occurred.")
            return False
        except Exception:
            print("Something else went wrong, unrelated to the Tinify API.")
            return False

    #Returns the number of compressions left using the api
    def planUsageLeft(self, planTotalUsage):
        try:
            compressions_this_month = planTotalUsage - tinify.compression_count
            print("%d compressions left"%(compressions_this_month))
            pass
        except tinify.AccountError:
            # Verify your API key and account limit.
            print ("Verify your API key and account limit.")
            pass
        except tinify.ClientError:
            print("Check your source image and request options.")
            pass
        except tinify.ServerError:
            print("Temporary issue with the Tinify API.")
            pass        
        except tinify.ConnectionError:
            print("A network connection error occurred.")
            pass    
        except Exception:
            print("Something else went wrong, unrelated to the Tinify API.")
            pass

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

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


wtmarkPath = resource_path("logo_w_letters.png")
#wtmarkPath = "../watermark/logo_w_letters.png"
wtmrk = MyWatermark("","", wtmarkPath)
cmprssr = MyCompressor("", "")



def openFile():
    
    #Get Directory Path 
    directory_Path = filedialog.askdirectory()
    
    #Output Path 
    save_directory =  os.path.dirname(directory_Path) + "/ready_to_upload"

    #Check if path exists
    if not os.path.exists( save_directory ):
        os.makedirs(save_directory, exist_ok=False)

    
    wtmrk.folder_path = save_directory
    wtmrk.folder_save_path = save_directory

    cmprssr.folder_path = directory_Path
    cmprssr.folder_save_path = save_directory


    print("Compressing Images")
    cmprssr.bulkCompressing()
    
    print("Watermarking Images")
    wtmrk.bulkWatermark()


window = Tk()
button = Button(text="Open",command=openFile)
button.pack()
window.mainloop()