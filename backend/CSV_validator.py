"""
Retriever Essentials - Basic Needs Impact Dashboard

CSV Validator

Check whether an uploaded CSV file is valid before
allowing it to be processed and stored in the database.
"""

import csv
from pathlib import Path


# ============================================================
# CLASS 1: CSV_validator
# ============================================================
# Purpose:
# Check whether an uploaded file is a valid CSV file.
#
# What it does:
# - Check that the file has a .csv extension
# - Check that the file is within the allowed size limit
# - Verify that the file contains readable CSV data
# - Check that CSV headers and rows are properly formatted
#
# This class will eventually be used by CSVUploader.
# ============================================================

class CSV_validator:

    def __init__(self, max_file_size=10 * 1024 * 1024):

        # Maximum allowed file size (default: 10 MB)
        self.max_file_size = max_file_size

        # Only CSV files are allowed by the project requirements
        self.allowed_extensions = {".csv"}

    def validate_extension(self, filename: str) -> bool:
        """
        Check whether the uploaded file has a .csv extension.
        """

        # Use Path to get the file extension
        extension = Path(filename).suffix.lower()

        # Check if the extension is in our allowed extensions
        if extension in self.allowed_extensions:
            return True

        # Return False if the extension is not allowed
        return False

    def validate_file_size(self, file_path: str) -> bool:
        """
        Check whether the file exceeds the maximum allowed size.
        """

        # Convert the file path into a Path object
        file = Path(file_path)

        # Check whether the file exists and is a regular file
        if not file.is_file():
            return False

        try:
            # Get the size of the file in bytes
            file_size = file.stat().st_size

            # Reject empty files
            if file_size == 0:
                return False

            # Check whether the file is within the allowed size
            if file_size <= self.max_file_size:
                return True

        # Handle errors when accessing the file
        except OSError:
            return False

        # Return False if the file is too large
        return False

    def validate_structure(self, file_path: str) -> bool:
        """
        Verify that the file contains properly formatted CSV data.
        """

        try:
            # Open the CSV file in read mode
            with open(file_path, "r", newline="", encoding="utf-8-sig") as file:

                # Create a CSV reader to read each row
                reader = csv.reader(file, strict=True)

                # Read the first row containing column headers
                headers = next(reader, None)

                # Reject files that have no headers
                if headers is None:
                    return False

                # Reject files containing empty column names
                if any(header.strip() == "" for header in headers):
                    return False

                # Reject duplicate column names
                if len(headers) != len(set(headers)):
                    return False

                # Store the number of columns expected in each row
                column_count = len(headers)

                # Check each remaining row in the CSV
                for row in reader:

                    # Reject rows with missing or extra columns
                    if len(row) != column_count:
                        return False

            # Return True if all rows have the correct structure
            return True

        # Handle missing files, invalid text, and CSV formatting errors
        except (OSError, UnicodeError, csv.Error):
            return False

    def validate_columns(self, file_path: str, required_columns: list) -> bool:
        """
        Check whether the CSV contains all required columns.
        """

        try:
            # Open the CSV file
            with open(file_path, "r", newline="", encoding="utf-8-sig") as file:

                # Read the CSV as dictionaries
                reader = csv.DictReader(file)

                # Get the column names from the CSV
                headers = reader.fieldnames

                # Reject files without headers
                if headers is None:
                    return False

                # Check every required column
                for column in required_columns:

                    # Return False if a required column is missing
                    if column not in headers:
                        return False

            # All required columns were found
            return True

        # Handle errors when reading the file
        except (OSError, UnicodeError, csv.Error):
            return False

    def validate(self, file_path: str, required_columns=None) -> bool:
        """
        Run all validation checks on the uploaded file.
        """

        # Check whether the file has a CSV extension
        if not self.validate_extension(file_path):
            return False

        # Check whether the file size is allowed
        if not self.validate_file_size(file_path):
            return False

        # Check whether the CSV structure is valid
        if not self.validate_structure(file_path):
            return False

        # Check required columns if they were provided
        if required_columns is not None:

            if not self.validate_columns(file_path, required_columns):
                return False

        # Return True only if every validation check passes
        return True