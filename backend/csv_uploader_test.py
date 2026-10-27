import unittest
import tempfile
from pathlib import Path
from io import BytesIO

# Import the classes we want to test
from CSV_validator import CSV_validator
from CSV_uploader import CSVUploader


class TestCSVUploader(unittest.TestCase):

    def setUp(self):

        # Create a temporary directory for each test
        self.temp_folder = tempfile.TemporaryDirectory()

        # Store the temporary folder path
        self.folder_path = Path(self.temp_folder.name)

        # Create a CSV validator object
        self.validator = CSV_validator()

        # Create the uploader using our validator and temporary folder
        self.uploader = CSVUploader(
            self.validator,
            self.folder_path / "uploads"
        )

    def tearDown(self):

        # Delete the temporary folder and uploaded files after each test
        self.temp_folder.cleanup()

    def create_test_file(self, filename, content):

        # Convert the CSV content into bytes
        file = BytesIO(content.encode("utf-8"))

        # Add a filename attribute to simulate a Flask upload
        file.filename = filename

        # Return the simulated uploaded file
        return file

    # ==================================================
    # Test successful CSV uploads
    # ==================================================

    def test_valid_upload(self):

        # Create a properly formatted CSV file
        file = self.create_test_file(
            "students.csv",
            "Month,Students_Served\nAugust,95\nSeptember,120\n"
        )

        # Upload the file using a sample user ID
        result = self.uploader.upload_file(file, 1)

        # The upload should succeed
        self.assertTrue(result["success"])

        # The uploaded file should exist in the upload folder
        self.assertTrue(Path(result["file_path"]).exists())

    # ==================================================
    # Test invalid file extensions
    # ==================================================

    def test_invalid_extension(self):

        # Create a text file instead of a CSV
        file = self.create_test_file(
            "students.txt",
            "Month,Students_Served\nAugust,95\n"
        )

        # Attempt to upload the file
        result = self.uploader.upload_file(file, 1)

        # The upload should fail
        self.assertFalse(result["success"])

    # ==================================================
    # Test invalid CSV structure
    # ==================================================

    def test_invalid_structure(self):

        # Create a CSV with an inconsistent number of columns
        file = self.create_test_file(
            "students.csv",
            "Month,Students_Served\nAugust,95\nSeptember\n"
        )

        # Attempt to upload the invalid CSV
        result = self.uploader.upload_file(file, 1)

        # The upload should fail
        self.assertFalse(result["success"])

        # No invalid file should remain in the upload directory
        self.assertEqual(len(list(self.uploader.upload_directory.iterdir())), 0)

    # ==================================================
    # Test missing required columns
    # ==================================================

    def test_missing_required_column(self):

        # Create a CSV without the Students_Served column
        file = self.create_test_file(
            "students.csv",
            "Month,Department\nAugust,Retriever Essentials\n"
        )

        # Define the required columns
        required_columns = [
            "Month",
            "Department",
            "Students_Served"
        ]

        # Attempt to upload the file
        result = self.uploader.upload_file(file, 1, required_columns)

        # The upload should fail
        self.assertFalse(result["success"])

    # ==================================================
    # Test invalid user IDs
    # ==================================================

    def test_invalid_user_id(self):

        # Create a valid CSV file
        file = self.create_test_file(
            "students.csv",
            "Month,Students_Served\nAugust,95\n"
        )

        # Attempt to upload using an invalid user ID
        result = self.uploader.upload_file(file, -1)

        # The upload should fail
        self.assertFalse(result["success"])

    # ==================================================
    # Test files exceeding the size limit
    # ==================================================

    def test_file_too_large(self):

        # Create a validator with a small 20-byte size limit
        small_validator = CSV_validator(max_file_size=20)

        # Create an uploader using the smaller size limit
        small_uploader = CSVUploader(
            small_validator,
            self.folder_path / "small_uploads"
        )

        # Create a CSV larger than the allowed limit
        file = self.create_test_file(
            "students.csv",
            "Month,Students_Served\nAugust,95\n"
        )

        # Attempt to upload the oversized file
        result = small_uploader.upload_file(file, 1)

        # The upload should fail
        self.assertFalse(result["success"])

        # The rejected file should not remain in the upload directory
        self.assertEqual(len(list(small_uploader.upload_directory.iterdir())), 0)

    # ==================================================
    # Test unique filenames
    # ==================================================

    def test_unique_names(self):

        # Create two files with the same original filename
        file1 = self.create_test_file(
            "students.csv",
            "Month,Students_Served\nAugust,95\n"
        )

        file2 = self.create_test_file(
            "students.csv",
            "Month,Students_Served\nSeptember,120\n"
        )

        # Upload both files
        result1 = self.uploader.upload_file(file1, 1)
        result2 = self.uploader.upload_file(file2, 1)

        # Both uploads should succeed
        self.assertTrue(result1["success"])
        self.assertTrue(result2["success"])

        # The saved filenames should be different
        self.assertNotEqual(result1["filename"], result2["filename"])


# Run the tests when this file is executed directly
if __name__ == "__main__":
    unittest.main()