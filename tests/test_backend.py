import os
import unittest
from io import BytesIO
from unittest import mock
from unittest.mock import patch

from PyPDF2 import PdfMerger, PdfFileReader

from backend import get_files, get_supported_paths, convert_to_pdf, get_pdf_files


class TestGetFiles(unittest.TestCase):

    def test_get_files_with_file(self):
        # test that get_files returns the path of a file when given a file path
        path = "test_file.txt"
        with open(path, "w") as f:
            f.write("This is a test file.")
        result = get_files(path)
        self.assertEqual(result, [path])
        os.remove(path)

    def test_get_files_with_directory(self):
        # test that get_files returns a list of file paths when given a directory path
        directory_path = "test_directory"
        os.mkdir(directory_path)
        file_paths = []
        for i in range(3):
            file_path = os.path.join(directory_path, f"test_file_{i}.txt")
            with open(file_path, "w") as f:
                f.write("This is a test file.")
            file_paths.append(file_path)

        result = get_files(directory_path)
        self.assertCountEqual(result, file_paths)

        for file_path in file_paths:
            os.remove(file_path)
        os.rmdir(directory_path)

    def test_get_files_with_invalid_path(self):
        # test that get_files raises a ValueError when given an invalid path
        path = "invalid_path"
        with self.assertRaises(ValueError):
            get_files(path)


class TestGetSupportedPaths(unittest.TestCase):
    @mock.patch('backend.os.path.splitext')
    def test_supported_paths(self, mock_path):
        mock_path.return_value = ('/path/to/file1', '.md')
        paths = ['/path/to/file1.md', '/path/to/file2.csv', '/path/to/file3.docx']
        result = get_supported_paths(paths)
        self.assertEqual(result, paths)

    @mock.patch('backend.os.path.splitext')
    def test_unsupported_paths(self, mock_path):
        mock_path.return_value = ('/path/to/file4', '.pdf')
        paths = ['/path/to/file4.pdf', '/path/to/file5.jpg', '/path/to/file6.py']
        result = get_supported_paths(paths)
        self.assertEqual(result, [])


class TestConvertToPdf(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to hold the PDF output
        self.output_dir = 'pdf_output_test'
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        # Clean up the temporary directory
        for file in os.listdir(self.output_dir):
            os.remove(os.path.join(self.output_dir, file))
        os.rmdir(self.output_dir)

    @mock.patch('backend.subprocess.run')
    def test_convert_file(self, mock_run):
        paths = ['/path/to/myfile.md']
        convert_to_pdf(paths, output_dir=self.output_dir)
        mock_run.assert_called_once_with(
            ['pandoc', '/path/to/myfile.md', '-o', os.path.join(self.output_dir, 'myfile.pdf')])

    @mock.patch('backend.subprocess.run')
    def test_convert_multiple_files(self, mock_run):
        paths = ['/path/to/myfile1.md', '/path/to/myfile2.tex', '/path/to/myfile3.html']
        convert_to_pdf(paths, output_dir=self.output_dir)
        mock_run.assert_has_calls([
            mock.call(['pandoc', '/path/to/myfile1.md', '-o', os.path.join(self.output_dir, 'myfile1.pdf')]),
            mock.call(['pandoc', '/path/to/myfile2.tex', '-o', os.path.join(self.output_dir, 'myfile2.pdf')]),
            mock.call(['pandoc', '/path/to/myfile3.html', '-o', os.path.join(self.output_dir, 'myfile3.pdf')])
        ])


class TestGetPdfFiles(unittest.TestCase):

    def setUp(self):
        self.files = [
            '/path/to/myfile.md',
            '/path/to/myfile.pdf',
            '/path/to/myfile.docx',
            '/path/to/myfile.pdf',
            '/path/to/myfile.txt',
        ]

    def test_get_pdf_files(self):
        with patch('os.path.splitext') as mock_splitext:
            mock_splitext.side_effect = [
                ('/path/to/myfile', '.md'),
                ('/path/to/myfile', '.pdf'),
                ('/path/to/myfile', '.docx'),
                ('/path/to/myfile', '.pdf'),
                ('/path/to/myfile', '.txt'),
            ]
            result = get_pdf_files(self.files)
            expected_result = ['/path/to/myfile.pdf', '/path/to/myfile.pdf']
            self.assertEqual(result, expected_result)


