<p align="center">
  <img src="/pics/GOD.PNG">
</p>

# pdf2text

This project is created to convert pdf files to text files in English and German language.

## Dependencies

You need dependencies below:

**Windows**

- Install tesseract :
    - download https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v4.1.0.20190314.exe (for 64x)
    - download https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w32-setup-v4.1.0.20190314.exe (for 32x)
	- in installing progress, in "choose component" , "Additional language data", tick "German"
	- set the installing location in system variables; e.g. C:\Program Files\Tesseract-OCR
	- set the folder of traineddata in system variables with variable name = TESSDATA_PREFIX and value = the directory of tessdata
	- restart windows


- Install imagemagick :
	- Download https://imagemagick.org/download/binaries/ImageMagick-7.0.10-4-Q16-x64-dll.exe (for 64bits)
	- set the installing location in system path; e.g. C:\Program Files\ImageMagick-7.0.10-Q16
	- install ghostscript : https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs950/gs950w64.exe


**Ubuntu**

```
$ sudo apt update
$ sudo apt install tesseract-ocr
$ sudo apt-get install tesseract-ocr-deu
$ sudo apt install imagemagick
$ sudo apt-get install ghostscript
```

then:

```
$ sudo vim /etc/ImageMagick-6/policy.xml
```
and replace the line:  
  
*\<policy domain="coder" rights="none" pattern="PDF" />*  
  
with:  
  
*\<policy domain="coder" rights="read|write" pattern="PDF" />*



## Requirements

```
> conda create -n pdf2text python=3.6.4
> conda activate pdf2text
> git clone https://gitlab.com/deeptools/image2text
> cd image2text
> pip install -r requirements
```

## Demo

### Test

You can test the code with pdf file(s).

**In this project your windows needs to have access to internet**
```
> git clone https://gitlab.com/deeptools/image2text
```

- Just place your pdf file(s) in "01-PDFs" folder and ... go rest!

```
> cd pdf2text
> conda activate pdf2text
> python convertor.py -h
```

for example for a pdf with watermark in German language :
``` 
> python convertor.py --back=1 --lang=deu --tess="C:/Program Files/Tesseract-OCR/tesseract.exe"
```

In this procedure the pdf file will be seprated to its pages and saved in '02-input' folder. Then these pages will be converted to image files and placed beside of their pdfs. In continuing, the code convert all of these images to text files and saved them in '03-TXTs' folder. Furthermore a text file with tesseract confidence of each word and a CSV file of tesseract output will be saved beside of text file.

