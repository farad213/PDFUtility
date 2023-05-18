import subprocess
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter


def get_files(paths):
    files = []
    for path in paths:
        if os.path.isfile(path):
            # if the path is a file, add it to the list of files
            files.append(path)
        elif os.path.isdir(path):
            # if the path is a directory, get a list of all the files in the directory and its subdirectories
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    # exclude hidden files
                    if not filename.startswith('.'):
                        files.append(os.path.join(dirpath, filename))
        else:
            # if the path is neither a file nor a directory, raise an exception
            raise ValueError(f"{path} is not a valid file or directory")
    return files


def get_supported_paths(paths):
    input_formats = [
        'md', 'markdown', 'mdown', 'mkd', 'tex', 'html', 'htm', 'epub', 'docx', 'odt', 'mediawiki', 'wiki',
        'rst', 'adoc', 'asciidoc', 'asc', 'ipynb', 'csv', 'yml', 'yaml'
    ]

    # Check the extension of each path against the list of supported input formats
    supported_paths = []
    for path in paths:
        ext = os.path.splitext(path)[1][1:].lower()
        if ext in input_formats:
            supported_paths.append(path)

    return supported_paths



def convert_to_pdf(paths, output_dir):
    os.makedirs(output_dir, exist_ok=True)  # Make sure the output directory exists

    for path in paths:
        # Create the output file path by changing the file extension to .pdf and
        # adding it to the output directory
        output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(path))[0] + '.pdf')

        # Convert the file to PDF using Pandoc
        subprocess.run(['pandoc', path, '-o', output_path])


def get_pdf_files(files):
    pdf_files = []
    for file in files:
        if os.path.splitext(file)[1].lower() == '.pdf':
            pdf_files.append(file)
    return pdf_files


def merge_pdfs(paths, output_dir):
    merger = PdfMerger()
    for path in paths:
        merger.append(open(path, 'rb'))
    with open(os.path.join(output_dir, "merged.pdf"), 'wb') as output_file:
        merger.write(output_file)


def split_pdf(input_files, output_dir):

    if input_files is None or output_dir is None:
        return

    for input_path in input_files:
        # Open the PDF file
        with open(input_path, 'rb') as file:
            pdf = PdfReader(file)

            # Iterate over each page in the PDF
            for page_number, page in enumerate(pdf.pages, start=1):
                # Get the current page

                # Create the output file path based on the naming schema
                output_filename = f"{os.path.splitext(os.path.basename(input_path))[0]}_{page_number}.pdf"
                output_path = os.path.join(output_dir, output_filename)

                # Create a new PDF writer and add the current page to it
                writer = PdfWriter()
                writer.add_page(page)

                # Write the output file
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

