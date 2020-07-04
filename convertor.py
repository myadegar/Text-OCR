#Import modules
import os
#import time
import glob
import pytesseract
from PIL import Image
from PyPDF2 import PdfFileWriter, PdfFileReader
from mtranslate import translate
import cv2
import re
import imutils
import shutil
from pytesseract import Output
import logging
import argparse

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser(description='pdf OCR')
ap.add_argument("--back", type=int, required=True, help="removing background (1: yes, 0: no)", default=0)
ap.add_argument("--lang", type=str, required=True, help="intended language (eng: English, deu: German)", default='deu')
ap.add_argument("--tess", type=str, required=True, help='tesseract.exe path, like: "C:/Program Files/Tesseract-OCR/tesseract.exe"', default=r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe")


if __name__ == '__main__':
    args = ap.parse_args()
    
    #print(args.back)
    
    
    ### logger
    # remove previouse log file
    if os.path.exists('logfile.log'):
        os.remove('logfile.log')

    # Create or get the logger
    logger = logging.getLogger(__name__)  

    # set log level
    logger.setLevel(logging.ERROR)

    # define file handler and set formatter
    file_handler = logging.FileHandler('logfile.log')
    formatter    = logging.Formatter('\n\n%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    file_handler.setFormatter(formatter)

    # add file handler to logger
    logger.addHandler(file_handler)
    
    
    ### pytesseract initialazation
    pytesseract.pytesseract.tesseract_cmd = args.tess
    
    
    #pdf splitting to its pages
    for pdf in glob.glob('./01-PDFs/*.pdf'):

        similar_text_files = []
        similar_CF_text_files = []

        file_name = pdf[10:-4]

        #delete previous contents of '02-input' folder
        #removing_files('02-input')

        print('{}.pdf is in progress ...'.format(file_name))

        inputpdf = PdfFileReader(open(pdf, "rb"))

        for ii in range(inputpdf.numPages):
            output = PdfFileWriter()
            output.addPage(inputpdf.getPage(ii))
            if ii < 9:
                page_number = f'00{ii+1}'
            elif ii < 99:
                page_number = f'0{ii+1}'
            else:
                page_number = f'{ii+1}'
            with open("./02-input/{}_page-{}.pdf".format(file_name, page_number), "wb") as outputStream:
                output.write(outputStream)

        #convert pdf(s) to image(s)
        for pdf in glob.glob('./02-input/{}*.pdf'.format(file_name)):
            pdf_name = pdf[:-4]
            cmd = 'magick convert  -density 300   -quality 100  -flatten   "{}".pdf  "{}".jpg'.format(pdf_name, pdf_name)
            os.system(cmd)

        # convert image file(s) to text file(s) (in German language)  
        for img in glob.glob('./02-input/{}*.jpg'.format(file_name)):

            try:

                #t1_I2T = time.time()
                # create a new folder as name 'file_name'
                new_folder = f"./03-TXTs/{file_name}" 
                if not os.path.exists(new_folder):
                    os.makedirs(new_folder)

                #try:

                #delete previous contents of '03-TXTs' folder
                #removing_files('03-TXTs')

                # reading image by opencv
                #im_bgr = cv2.imread(img, 0)
                #image = cv2.cvtColor(im_bgr, cv2.COLOR_BGR2RGB)

                # detecting image orientation and fix that
                osd = pytesseract.image_to_osd(Image.open(img))
                image_angle = float(re.search('(?<=Rotate: )\d+', osd).group(0))

                #print("image_angle = "+str(image_angle))

                if image_angle != 0 :
                        cv_image = cv2.imread(img)
                        rotated = imutils.rotate_bound(cv_image, image_angle)
                        cv2.imwrite(img, rotated)


                # applying median blur on the image
                if args.back:
                    kernel_size = 3
                    image = cv2.imread(img, 0)
                    m_img = cv2.medianBlur(image,kernel_size)
                    #m_img = cv2.Laplacian(m_img, cv2.CV_8U)
                    cv2.imwrite(img, m_img)

                # image to text
                # 1. by pytesseract
                custom_config = f'-c preserve_interword_spaces=1 --psm 6 -l {args.lang}'
                extractedInformation = pytesseract.image_to_string(Image.open(img), config=custom_config)
                with open('./03-TXTs/{}.txt'.format(img[11:-4]), 'w', encoding="utf-8") as file:
                    file.write(extractedInformation)

                similar_text_files.append('./03-TXTs/{}.txt'.format(img[11:-4]))


                # 2. by tesseract CLI
                #cmd = 'tesseract 103000003673_page-1.jpg tt.txt -c preserve_interword_spaces=1 --psm 4 -l deu'
                #os.system(cmd)

                # writing with confidence
                #print('{}.pdf is in confidence inserting progress ...'.format(file_name))
                # 1. creating text data tabel
                text_table = pytesseract.image_to_data(Image.open(img), lang=args.lang , output_type=Output.DATAFRAME)
                text_table.to_csv('./03-TXTs/{}/{}.csv'.format(file_name, img[11:-4]), encoding='utf8', index=False)

                # 2. creating properties file
                Words = len(text_table[text_table.conf>=0]['conf'].index)
                Std = text_table[text_table.conf>=0]['conf'].std()
                Average = text_table[text_table.conf>=0]['conf'].mean()
                Max = text_table[text_table.conf>=0]['conf'].max()
                Min = text_table[text_table.conf>=0]['conf'].min()

                # pdf file properties
                #with open('./03-TXTs/{}/{}_Properties.txt'.format(file_name, img[11:-4]), 'w') as Prop_file:
                    #line1 = 'In the name of GOD\n'
                    #line2 = f"Number of detected words = {Words}"
                    #line3 = f'Standard deviation of confidence = {Std}'
                    #line4 = f'Average confidence = {Average}'
                    #line5 = f'Maximum confidence = {Max}'
                    #line6 = f'Minimum confidence = {Min}'
                    #Prop_file.write(f'{line1}\n{line2}\n{line3}\n{line4}\n{line5}\n{line6}\n\n\n')

                # 3. converting text file to list
                text_list = []
                with open('./03-TXTs/{}.txt'.format(img[11:-4]), 'r', encoding='utf8') as file: 
                    # reading each line     
                    for line in file:
                        word = line.split(' ')
                        text_list.append(word)

                # 4. inserting confidence of each word
                start_point = 0
                for row in text_list:
                    for i in range(len(row)):
                        word = row[i]
                        s_word = word.replace('\n','')

                        # to avoid engaging confidence of iterated words
                        for j in range(start_point, text_table.index.stop):
                            if text_table.text[j] == s_word:
                                confidence = text_table.conf[j]
                                row[i] = s_word + f"({confidence}%)"
                                #start_point = j+1
                                break

                # 5. creating new text file
                new_text_list = []

                for k in range(len(text_list)):
                    words = " ".join(text_list[k])
                    new_text_list.append(words)

                with open('./03-TXTs/{}_CF.txt'.format(img[11:-4]), 'w', encoding="utf-8") as output_with_confidence_file:
                    for item in new_text_list:
                        output_with_confidence_file.write("%s\n" % item)

                similar_CF_text_files.append('./03-TXTs/{}_CF.txt'.format(img[11:-4]))

                # Time consuming
                #t2_I2T = time.time()
                #with open('./03-TXTs/{}/{}_Properties.txt'.format(file_name, img[11:-4]), 'a') as Prop_file:

                    #Prop_file.write("** Time consuming (image2text and quality estimating) = {} seconds **"
                                    #.format(str(t2_I2T - t1_I2T)))


            except:

                logger.exception(f"When \"{img}\" was being processed an error has occured!")

        # merge text files             

        with open(f"./03-TXTs/{file_name}/{file_name}.txt",'wb') as outfile:
            for f in similar_text_files:
                with open(f,'rb') as infile:
                    outfile.write(b"\n\n********** The Beginning of The Page **********\n\n")
                    shutil.copyfileobj(infile, outfile)



        # merge CF text files             

        with open(f"./03-TXTs/{file_name}/{file_name}_CF.txt",'wb') as outfile:
            for f in similar_CF_text_files:
                with open(f,'rb') as infile:
                    outfile.write(b"\n\n********** The Beginning of The Page **********\n\n")
                    shutil.copyfileobj(infile, outfile)





        # copy the processed pdf to its processing folder
        shutil.copyfile(f"./01-PDFs/{file_name}.pdf", f"./03-TXTs/{file_name}/{file_name}.pdf")

        # remove seperated pages of the pdf file
        files = glob.glob('./03-TXTs/*.txt')
        for f in files:
            os.remove(f)







        # translating to English

        #txt = f"./03-TXTs/{file_name}.txt"

        #with open(txt, 'r', encoding="utf8") as file:
            #text = file.read()
            #trans = translate(text,"en","de")
            #with open('./04-output/{}_translated.txt'.format(txt[10:-4]), 'w', encoding="utf-8") as file:
                #file.write(trans)


        print('{}.pdf is finished. \n'.format(file_name))



    print('The End!')
    


