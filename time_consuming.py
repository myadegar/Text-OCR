#Import modules
import os
import glob
import pytesseract
from PIL import Image
from PyPDF2 import PdfFileWriter, PdfFileReader
from mtranslate import translate
import time

#pdf splitting to its pages
time_tottal_start = time.time()
for pdf in glob.glob('./01-PDFs/*.pdf'):

    file_name = pdf[10:-4]
    
    #delete previous contents of '02-input' folder
    #removing_files('02-input')
    
    #print('{}.pdf is in progress ...'.format(file_name))
    
    inputpdf = PdfFileReader(open(pdf, "rb"))

    for i in range(inputpdf.numPages):
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(i))
        with open("./02-input/{}_page-{}.pdf".format(file_name, str(i+1)), "wb") as outputStream:
            output.write(outputStream)
            
    #convert pdf(s) to image(s)
    print('STARTING PROCESS FOR --{}-- PDF FILE(s) ... '.format(inputpdf.numPages))
    print('')
    print('* pdf to image starting!')
    t1_PIT = time.time()
    for pdf in glob.glob('./02-input/{}*.pdf'.format(file_name)):
        pdf_name = pdf[:-4]
        cmd = 'magick convert  -density 300   -quality 100  -flatten   "{}".pdf  "{}".jpg'.format(pdf_name, pdf_name)
        os.system(cmd)
    t2_PIT = time.time()
    print('* Pdf2Image time consuming = {} seconds'.format(str(t2_PIT - t1_PIT)))
    print()
        
    # convert image file(s) to text file(s) (in German language)
    print('** OCR starting!')
    t1_IT = time.time()
    for img in glob.glob('./02-input/{}*.jpg'.format(file_name)):
        
        #delete previous contents of '03-TXTs' folder
        #removing_files('03-TXTs')
        
        extractedInformation = pytesseract.image_to_string(Image.open(img), lang='deu')
        with open('./03-TXTs/{}.txt'.format(img[11:-4]), 'w', encoding="utf-8") as file:
            file.write(extractedInformation)
    t2_IT = time.time()
    print('** Image2Text time consuming = {} seconds'.format(str(t2_IT - t1_IT)))
    print()
    print()
    
#    # translating to English
#    for txt in glob.glob('./03-TXTs/{}*.txt'.format(file_name)):
        
#        txt_name = txt[10:-4]
        
#        with open(txt, 'r', encoding="utf8") as file:
#            text = file.read()
#            trans = translate(text,"en","de")
#            with open('./04-output/{}_translated.txt'.format(txt_name), 'w', encoding="utf-8") as file:
#                file.write(trans)
                
    
    #print('{}.pdf is finished. \n'.format(file_name))
    

time_tottal_end = time.time()

print('The End! in *{}* seconds'.format(str(time_tottal_end - time_tottal_start)))