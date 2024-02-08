import shutil
import streamlit as st
import os
from pdf_ocr import process_files_in_folder

def clean_up_directory(dir):
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

st.title('OCR processing')

input_folder = "./folders/in"
tmp_folder = "./folders/tmp"
results_folder = "./folders/results"
output_zip = "./folders/results.zip"

if not os.path.exists(input_folder):
    os.mkdir(input_folder)

if not os.path.exists(tmp_folder):
    os.mkdir(tmp_folder)

if not os.path.exists(results_folder):
    os.mkdir(results_folder)

uploaded_files = st.file_uploader("Choose a file or zip", type=['pdf', 'zip'], accept_multiple_files=True)
process_button = st.button('Start Processing')

bar = st.progress(0)
result_str = ""

if process_button:
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with open(os.path.join(input_folder, os.path.basename(uploaded_file.name)), "wb") as f:
                f.write(uploaded_file.getbuffer())
            # Update the progress bar while processing
            for i in range(100):
                # Update progress
                bar.progress(i + 1)

        # Process the files and generate output in the 'results_folder'
        process_files_in_folder(input_folder, tmp_folder, results_folder)

        # Create a Zip file for all the processed files
        shutil.make_archive(output_zip.replace('.zip', ''), 'zip', results_folder)
        result_str = "The processed files are available for download."
        st.write(result_str)
        with open(output_zip, "rb") as file:
            st.download_button(
                label="Download File",
                data=file,
                file_name=output_zip,
                mime="application/zip"
            )
        # Clean up the folders
        clean_up_directory(input_folder)
        clean_up_directory(tmp_folder)
        clean_up_directory(results_folder)

clean_up_button = st.button('Clean Up')
if clean_up_button:
    clean_up_directory(input_folder)
    clean_up_directory(tmp_folder)
    clean_up_directory(results_folder)
    # delete the zip file if it exists
    if os.path.exists(output_zip):
        os.remove(output_zip)