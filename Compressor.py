from kivy import app
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.properties import ObjectProperty

#TinyPng
import tinify
import os 

# Designate our .kv design file
Builder.load_file('compressorlayout.kv')

class MyCompressor ():
    tinify.key = "hlH2Tr7d0p0gpnPsypV53Klp5kR3pbPv"
    PLAN_TOTAL_USAGE = 500
    CMPCODE ="cmp-" 

    #input_path = Path of the image to compress 
    #output_path = To store the compressed image 
    def compressImage( input_path, output_path ):
        try:
            source = tinify.from_file(input_path)
            resize = source.resize(
                method="fit",
                width=980,
                height=700
            )
            #source.preserve("creation")
            resize.to_file(output_path)
            # compressions_this_month = 500 - tinify.compression_count
            # print("%d compressions left"%(compressions_this_month))
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
    def planUsageLeft(planTotalUsage):
        try:
            compressions_this_month = planTotalUsage - tinify.compression_count
            print("%d compressions left"%(compressions_this_month))
            pass
        except tinify.AccountError:
            # Verify your API key and account limit.
            print ("Invalid KEY")
            pass
        except tinify.ClientError:
            print("File type not supported")
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
    def bulkCompressing( dirPath, dirArr, compressImageFunction, cmpCode ):
        for i,image in enumerate(dirArr):
            print( "Compressing %d out of %d"%((i+1), len(dirArr)) )

            input_Path = dirPath + image   
            output_Path = dirPath + cmpCode + image

            #Compress every image and stores it in the same directory
            if( not compressImageFunction(input_Path,output_Path) ):
                print( "An unexpected error was found. Compression Cancelled" )
                return 
            



class CompressorLayout(Widget):
    name = ObjectProperty(None)
    pizza = ObjectProperty(None)

    def press(self):
        #Get input information
        name = self.name.text
        pizza = self.pizza.text

        print("Hello %s you like %s pizza!"%(name, pizza))

        #Clear input boxes
        self.name.text = " "
        self.pizza.text = " "

    pass

class CompressorApp(App):
    def build (self):
        return CompressorLayout()

if __name__ == '__main__':
    CompressorApp().run()
