import unittest
import tempfile
from pathlib import Path

# Import the CSV validator class from CSV_validator.py
from CSV_validator import CSV_validator


class TestCSVValidator(unittest.TestCase):

    def setUp(self):
        # Create a temporary folder before each test
        self.temp_folder = tempfile.TemporaryDirectory()

        # Get the path to the temporary folder
        self.folder_path = Path(self.temp_folder.name)

        # Create a CSV validator object
        self.validator = CSV_validator()

    def tearDown(self):
        # Delete the temporary folder and its files after each test
        self.temp_folder.cleanup()

    def create_test_file(self, filename, content):
        # Create the path for the temporary CSV file
        file_path = self.folder_path / filename

        # Write the provided content into the CSV file
        file_path.write_text(content, encoding="utf-8")

        # Return the file path as a string
        return str(file_path)

    # ==================================================
    # Test validate_extension()
    # ==================================================

    def test_valid_extension(self):
        # Check whether a valid CSV extension is accepted
        result = self.validator.validate_extension("students.csv")

        # The result should be True
        self.assertTrue(result)

    def test_invalid_extension(self):
        # Check whether a TXT extension is rejected
        result = self.validator.validate_extension("students.txt")

        # The result should be False
        self.assertFalse(result)

    def test_uppercase_extension(self):
        # Check whether an uppercase CSV extension is accepted
        result = self.validator.validate_extension("students.CSV")

        # The result should be True
        self.assertTrue(result)

    # ==================================================
    # Test validate_file_size()
    # ==================================================

    def test_valid_file_size(self):
        # Create a small CSV file
        file_path = self.create_test_file(
            "valid.csv",
            "Month,Students_Served\nAugust,95\n"
        )

        # Check whether the file size is allowed
        result = self.validator.validate_file_size(file_path)

        self.assertTrue(result)

    def test_empty_file(self):
        # Create an empty CSV file
        file_path = self.create_test_file("empty.csv", "")

        # Empty files should not be accepted
        result = self.validator.validate_file_size(file_path)

        self.assertFalse(result)

    def test_oversized_file(self):
        # Create a validator with a 10-byte limit for testing
        small_validator = CSV_validator(max_file_size=10)

        # Create a file larger than 10 bytes
        file_path = self.create_test_file(
            "large.csv",
            "Month,Students_Served\nAugust,95\n"
        )

        # Check whether the oversized file is rejected
        result = small_validator.validate_file_size(file_path)

        self.assertFalse(result)

    def test_missing_file(self):
        # Create a path to a file that does not exist
        file_path = str(self.folder_path / "missing.csv")

        # A nonexistent file should be rejected
        result = self.validator.validate_file_size(file_path)

        self.assertFalse(result)

    # ==================================================
    # Test validate_structure()
    # ==================================================

    def test_valid_structure(self):
        # Create a CSV with the correct number of columns
        file_path = self.create_test_file(
            "valid.csv",
            "Month,Students_Served\n"
            "August,95\n"
            "September,120\n"
        )

        # Check whether the CSV structure is valid
        result = self.validator.validate_structure(file_path)

        self.assertTrue(result)

    def test_missing_headers(self):
        # Create a CSV without any content or headers
        file_path = self.create_test_file("no_headers.csv", "")

        # The structure should be invalid
        result = self.validator.validate_structure(file_path)

        self.assertFalse(result)

    def test_invalid_structure(self):
        # Create a CSV where one row has fewer columns than expected
        file_path = self.create_test_file(
            "invalid.csv",
            "Month,Students_Served\n"
            "August,95\n"
            "September\n"
        )

        # Check whether the validator detects the incorrect structure
        result = self.validator.validate_structure(file_path)

        self.assertFalse(result)

    def test_duplicate_headers(self):
        # Create a CSV containing duplicate column names
        file_path = self.create_test_file(
            "duplicate.csv",
            "Month,Month\n"
            "August,September\n"
        )

        # Duplicate headers should not be accepted
        result = self.validator.validate_structure(file_path)

        self.assertFalse(result)

    # ==================================================
    # Test validate_columns()
    # ==================================================

    def test_valid_columns(self):
        # Create a CSV containing all required columns
        file_path = self.create_test_file(
            "valid.csv",
            "Month,Department,Students_Served\n"
            "August,Retriever Essentials,95\n"
        )

        # Define the columns expected in this dataset
        required_columns = [
            "Month",
            "Department",
            "Students_Served"
        ]

        # Check whether all required columns exist
        result = self.validator.validate_columns(
            file_path, required_columns
        )

        self.assertTrue(result)

    def test_missing_required_columns(self):
        # Create a CSV missing the Students_Served column
        file_path = self.create_test_file(
            "missing.csv",
            "Month,Department\n"
            "August,Retriever Essentials\n"
        )

        # Define the required columns
        required_columns = [
            "Month",
            "Department",
            "Students_Served"
        ]

        # Check whether the missing column is detected
        result = self.validator.validate_columns(
            file_path, required_columns
        )

        self.assertFalse(result)

    # ==================================================
    # Test validate()
    # ==================================================

    def test_complete_validation(self):
        # Create a CSV that meets all validation requirements
        file_path = self.create_test_file(
            "valid.csv",
            "Month,Department,Students_Served\n"
            "August,Retriever Essentials,95\n"
            "September,Retriever Essentials,120\n"
        )

        # Define the required columns
        required_columns = [
            "Month",
            "Department",
            "Students_Served"
        ]

        # Run all validation checks
        result = self.validator.validate(
            file_path, required_columns
        )

        # The file should pass every check
        self.assertTrue(result)

    def test_complete_validation_fails(self):
        # Create a CSV with a missing required column
        file_path = self.create_test_file(
            "invalid.csv",
            "Month,Department\n"
            "August,Retriever Essentials\n"
        )

        # Define the required columns
        required_columns = [
            "Month",
            "Department",
            "Students_Served"
        ]

        # Run the complete validation process
        result = self.validator.validate(
            file_path, required_columns
        )

        # The file should fail validation
        self.assertFalse(result)


# Run the tests when this file is executed directly
if __name__ == "__main__":
    unittest.main()