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

        # Create the original CSV content
        content = (
            "Month,Students_Served\n"
            "August,95\n"
            "September,120\n"
        )

        # Create a properly formatted CSV file
        file = self.create_test_file("students.csv", content)

        # Upload the file using a sample user ID
        result = self.uploader.upload_file(file, 1)

        # The upload should succeed
        self.assertTrue(result["success"])

        # Get the path of the uploaded file
        saved_path = Path(result["file_path"])

        # The uploaded file should exist in the upload folder
        self.assertTrue(saved_path.exists())

        # The saved file should contain the original CSV content
        self.assertEqual(
            saved_path.read_bytes(),
            content.encode("utf-8")
        )

        # The original filename should be preserved
        self.assertEqual(
            result["original_filename"],
            "students.csv"
        )

        # The correct uploader ID should be recorded
        self.assertEqual(result["uploaded_by"], 1)

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

        # No rejected file should remain in the upload directory
        self.assertEqual(
            len(list(self.uploader.upload_directory.iterdir())),
            0
        )

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
        self.assertEqual(
            len(list(self.uploader.upload_directory.iterdir())),
            0
        )

    def test_empty_file(self):

        # Create an empty CSV file
        file = self.create_test_file("empty.csv", "")

        # Attempt to upload the empty file
        result = self.uploader.upload_file(file, 1)

        # The upload should fail
        self.assertFalse(result["success"])

        # The empty file should not remain in the upload directory
        self.assertEqual(
            len(list(self.uploader.upload_directory.iterdir())),
            0
        )

    def test_header_only(self):

        # Create a CSV containing headers but no data rows
        file = self.create_test_file(
            "header_only.csv",
            "Month,Students_Served\n"
        )

        # Attempt to upload the file
        result = self.uploader.upload_file(file, 1)

        # The upload should fail
        self.assertFalse(result["success"])

        # The rejected file should be removed
        self.assertEqual(
            len(list(self.uploader.upload_directory.iterdir())),
            0
        )

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
        result = self.uploader.upload_file(
            file, 1, required_columns
        )

        # The upload should fail
        self.assertFalse(result["success"])

        # The rejected file should not remain in the upload directory
        self.assertEqual(
            len(list(self.uploader.upload_directory.iterdir())),
            0
        )

    def test_valid_required_columns(self):

        # Create a CSV containing all required columns
        file = self.create_test_file(
            "students.csv",
            "Month,Department,Students_Served\n"
            "August,Retriever Essentials,95\n"
        )

        # Define the required columns
        required_columns = [
            "Month",
            "Department",
            "Students_Served"
        ]

        # Attempt to upload the file
        result = self.uploader.upload_file(
            file, 1, required_columns
        )

        # The upload should succeed
        self.assertTrue(result["success"])

        # The uploaded file should exist
        self.assertTrue(Path(result["file_path"]).exists())

    # ==================================================
    # Test invalid user IDs
    # ==================================================

    def test_invalid_user_id(self):

        # Define several invalid user IDs
        invalid_user_ids = [-1, 0, None, "1", True, 1.5]

        # Test each invalid user ID
        for user_id in invalid_user_ids:

            with self.subTest(user_id=user_id):

                # Create a valid CSV file
                file = self.create_test_file(
                    "students.csv",
                    "Month,Students_Served\nAugust,95\n"
                )

                # Attempt to upload using an invalid user ID
                result = self.uploader.upload_file(file, user_id)

                # The upload should fail
                self.assertFalse(result["success"])

        # No file should be saved for an invalid user ID
        self.assertEqual(
            len(list(self.uploader.upload_directory.iterdir())),
            0
        )

    # ==================================================
    # Test missing files and filenames
    # ==================================================

    def test_missing_file(self):

        # Attempt to upload without providing a file
        result = self.uploader.upload_file(None, 1)

        # The upload should fail
        self.assertFalse(result["success"])

        # No file should be created
        self.assertEqual(
            len(list(self.uploader.upload_directory.iterdir())),
            0
        )

    def test_empty_filename(self):

        # Create a CSV file without a filename
        file = self.create_test_file(
            "",
            "Month,Students_Served\nAugust,95\n"
        )

        # Attempt to upload the file
        result = self.uploader.upload_file(file, 1)

        # The upload should fail
        self.assertFalse(result["success"])

        # No file should be saved
        self.assertEqual(
            len(list(self.uploader.upload_directory.iterdir())),
            0
        )

    # ==================================================
    # Test large CSV files
    # ==================================================

    def test_large_file_upload(self):

        # Create CSV content larger than the previous 10 MB limit
        content = (
            "Month,Students_Served\n" +
            "September,120\n" * 1000000
        )

        # Create the large CSV file
        file = self.create_test_file("large.csv", content)

        # Confirm that the file exceeds the previous size limit
        self.assertGreater(
            len(content.encode("utf-8")),
            10 * 1024 * 1024
        )

        # Attempt to upload the large CSV file
        result = self.uploader.upload_file(file, 1)

        # Large CSV files should now be accepted
        self.assertTrue(result["success"])

        # Get the path of the uploaded file
        saved_path = Path(result["file_path"])

        # The uploaded file should exist
        self.assertTrue(saved_path.exists())

        # Confirm that the entire file was saved
        self.assertEqual(
            saved_path.stat().st_size,
            len(content.encode("utf-8"))
        )

    # ==================================================
    # Test unsuccessful upload cleanup
    # ==================================================

    def test_interrupted_upload(self):

        # Create a file object that simulates an interrupted upload
        class InterruptedFile(BytesIO):

            def __init__(self, content):

                # Initialize the file with CSV content
                super().__init__(content)

                # Track how many times the file has been read
                self.read_count = 0

            def read(self, size=-1):

                # Increase the number of read attempts
                self.read_count += 1

                # Simulate an error after the first read
                if self.read_count > 1:
                    raise OSError("Simulated upload interruption")

                # Return the first portion of the file
                return super().read(size)

        # Create a simulated uploaded CSV file
        file = InterruptedFile(
            b"Month,Students_Served\nAugust,95\n"
        )

        # Assign a filename to the simulated upload
        file.filename = "interrupted.csv"

        # Attempt to upload the file
        result = self.uploader.upload_file(file, 1)

        # The interrupted upload should fail
        self.assertFalse(result["success"])

        # The partially saved file should be removed
        self.assertEqual(
            len(list(self.uploader.upload_directory.iterdir())),
            0
        )

    def test_failed_upload_preserves_existing_files(self):

        # Create a valid CSV file
        valid_file = self.create_test_file(
            "valid.csv",
            "Month,Students_Served\nAugust,95\n"
        )

        # Upload the valid file
        valid_result = self.uploader.upload_file(valid_file, 1)

        # The first upload should succeed
        self.assertTrue(valid_result["success"])

        # Create an invalid CSV file
        invalid_file = self.create_test_file(
            "invalid.csv",
            "Month,Students_Served\nSeptember\n"
        )

        # Attempt to upload the invalid file
        invalid_result = self.uploader.upload_file(invalid_file, 1)

        # The second upload should fail
        self.assertFalse(invalid_result["success"])

        # The previously uploaded valid file should still exist
        self.assertTrue(
            Path(valid_result["file_path"]).exists()
        )

        # Only the valid file should remain in the upload directory
        self.assertEqual(
            len(list(self.uploader.upload_directory.iterdir())),
            1
        )

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
        self.assertNotEqual(
            result1["filename"],
            result2["filename"]
        )

        # Both uploaded files should exist
        self.assertTrue(Path(result1["file_path"]).exists())
        self.assertTrue(Path(result2["file_path"]).exists())

        # Both files should remain in the upload directory
        self.assertEqual(
            len(list(self.uploader.upload_directory.iterdir())),
            2
        )


# Run the tests when this file is executed directly
if __name__ == "__main__":
    unittest.main()