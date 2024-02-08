import os
import shutil
import pdf2image
import pytesseract
import cv2
import numpy as np
from PyPDF2 import PdfMerger
from tqdm import tqdm
import zipfile
from typing import Optional

def extract_zip(in_file: str, out_folder: Optional[str] = None):
    """Extracts a zip file"""
    # If output folder is not specified, extract in place
    if out_folder is None:
        out_folder = os.path.dirname(in_file)
    with zipfile.ZipFile(in_file, 'r') as zip_ref:
        zip_ref.extractall(out_folder)
        
def pdf_conversion(inpath):
    OUTPUT_FOLDER = None
    FIRST_PAGE = None
    LAST_PAGE = None
    FORMAT = "jpg"
    USER_PWD = None
    USE_CROPBOX = None
    STRICT = None
    pil_images = pdf2image.convert_from_path(inpath,
                                             first_page=FIRST_PAGE,
                                             last_page=LAST_PAGE,
                                             fmt=FORMAT,
                                             )
    print(f"Total {len(pil_images)} pages in pdf")
    return pil_images


def convert_image_to_text(image):
    """Here's a breakdown of what each part of the configuration does:

--oem 3: Specifies the OCR Engine Mode. The value 3 indicates that both the legacy and LSTM (Long Short-Term Memory) engines are used.
--psm 6: Sets the Page Segmentation Mode to 6, which assumes a single uniform block of text.
-l heb: Specifies the language model to use, in this case, Hebrew.
To potentially improve the accuracy of OCR for Hebrew text, consider the following adjustments:
1) Experiment with Different PSM Values: The Page Segmentation Mode (PSM) can significantly affect
 the OCR results. PSM 6 assumes a single uniform block of text. If your document structure varies
  (like multiple columns, non-uniform text blocks, etc.), try different PSM values such as 3
   (Fully automatic page segmentation, but no OSD) or 11 (Sparse text with OSD).
2) Use a Different OEM: If you are working with newer, high-quality images or PDFs, you might want to
 experiment with using only the LSTM engine (--oem 1).
 The LSTM engine is generally more accurate with modern text and fonts.
3) Image Preprocessing: Before passing images to Tesseract, consider implementing image preprocessing
 steps such as rescaling, denoising, or thresholding, as these can significantly enhance the text's clarity
 and contrast, leading to better OCR results.
4) Language Models and Fonts: Ensure you are using the appropriate language model for Hebrew.
 Additionally, if you have control over the fonts used in the documents, choose those that are OCR-friendly and support
  the necessary character sets and diacritics for Hebrew.
Incorporating these adjustments could enhance the precision of the OCR process for Hebrew documents.
 Testing with different configurations and preprocessing methods on sample documents can help determine
  the most effective setup for your specific use case."""

    # Convert PIL Image to numpy array (image in PIL is in (R, G, B) mode)
    numpy_image = np.array(image)

    # Convert RGB to BGR
    opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

    custom_oem_psm_config = r'--oem 1 --psm 3 -l heb'
    # custom_oem_psm_config = r'--oem 3 --psm 6 -l heb'

    result = pytesseract.image_to_pdf_or_hocr(opencv_image, config=custom_oem_psm_config, extension='pdf')

    return result


def save_to_file(data, output_file_path):
    # Open the file in write-binary mode and write the result
    with open(output_file_path, 'wb') as f:
        f.write(data)


def merge_pdfs(results_file_path, tmp_folder):
    merger = PdfMerger()
    for pdf in sorted(os.listdir(tmp_folder)):
        if pdf.endswith(".pdf"):
            merger.append(os.path.join(tmp_folder, pdf))
            os.remove(os.path.join(tmp_folder, pdf))  # remove the file once it's merged
    merger.write(results_file_path)
    merger.close()


# This function will allow us to reflect the structure of an output folder
def get_output_path(input_path, input_folder, output_folder):
    rel_path = os.path.relpath(input_path, start=input_folder)
    output_path = os.path.join(output_folder, rel_path)
    return output_path 

def process_files_in_folder(folder: str, tmp_folder: str, results_folder: str, is_zip=False):
    for root, _, files in os.walk(folder):
        for filename in files:
            # Process pdf files
            if filename.endswith(".pdf"):
                file_path = os.path.join(root, filename)
                file_path_res = get_output_path(file_path, folder, results_folder) if is_zip else os.path.join(results_folder, filename)
                os.makedirs(os.path.dirname(file_path_res), exist_ok=True)  # Create directories as needed
                print(f"Processing {file_path}")
                pil_images = pdf_conversion(file_path)

                for i, image in enumerate(pil_images):
                    result = convert_image_to_text(image)
                    output_file_path = os.path.join(tmp_folder, f"{i}_{os.path.splitext(filename)[0]}.pdf")
                    save_to_file(result, output_file_path)

                merge_pdfs(file_path_res, tmp_folder)  # Save the processed file in the results folder

            # Extract zip files and process them
            elif filename.endswith(".zip"):
                zip_path = os.path.join(root, filename)
                # Create a unique temporary directory to avoid conflicts
                extracted_dir = os.path.join(tmp_folder, f"tmp_{os.path.splitext(filename)[0]}")
                os.makedirs(extracted_dir, exist_ok=True)

                # Extract the zip file
                extract_zip(zip_path, extracted_dir)

                # Process the extracted files
                process_files_in_folder(extracted_dir, tmp_folder, results_folder, is_zip=True)

                # Clean up temporary extraction folder
                shutil.rmtree(extracted_dir)



# Specify the input folder, temporary folder, and results folder
input_folder = "./folders/in"
tmp_folder = "./folders/tmp"
results_folder = "./folders/results"

process_files_in_folder(input_folder, tmp_folder, results_folder)
