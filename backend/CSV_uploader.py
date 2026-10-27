import uuid
from pathlib import Path

# Import the CSV validator class we previously created
from CSV_validator import CSV_validator


class CSVUploader:

    def __init__(self, validator, upload_directory="uploads"):

        # Store the CSV validator object so we can use its functions
        self.validator = validator

        # Set the folder where uploaded CSV files will be saved
        self.upload_directory = Path(upload_directory)

        # Create the upload folder if it does not already exist
        self.upload_directory.mkdir(parents=True, exist_ok=True)

    def upload_file(self, file, user_id, required_columns=None):
        """
        Receive an uploaded file, validate it, and save it.

        file: Uploaded file object from Flask or another file stream
        user_id: ID of the user uploading the file
        required_columns: Columns that must exist in the CSV
        """

        # Check whether the user ID was provided
        if not isinstance(user_id, int) or isinstance(user_id, bool) or user_id <= 0:
            return {
                "success": False,
                "message": "Invalid user ID."
            }

        # Check whether a file was provided
        if file is None:
            return {
                "success": False,
                "message": "No file was uploaded."
            }

        # Get the original filename from the uploaded file
        original_filename = getattr(file, "filename", None)

        # Check whether the uploaded file has a filename
        if not original_filename:
            return {
                "success": False,
                "message": "Uploaded file has no filename."
            }

        # Use the existing CSV validator to check the extension
        if not self.validator.validate_extension(original_filename):
            return {
                "success": False,
                "message": "Only CSV files are allowed."
            }

        # Generate a unique filename to prevent files from overwriting each other
        unique_filename = str(uuid.uuid4()) + ".csv"

        # Create the complete path where the file will be saved
        saved_path = self.upload_directory / unique_filename

        try:
            # Keep track of the total number of bytes uploaded
            total_size = 0

            # Open the destination file in binary write mode
            with open(saved_path, "xb") as saved_file:

                # Read the uploaded file in chunks instead of all at once
                while True:

                    # Read up to 64 KB from the uploaded file
                    chunk = file.read(64 * 1024)

                    # Stop reading when there is no more data
                    if not chunk:
                        break

                    # Add the chunk size to the total uploaded size
                    total_size += len(chunk)

                    # Reject the file if it exceeds the validator's size limit
                    if total_size > self.validator.max_file_size:
                        return {
                            "success": False,
                            "message": "CSV file exceeds the maximum allowed size."
                        }

                    # Write the current chunk to the destination file
                    saved_file.write(chunk)

            # Run the CSV validator on the saved file
            if not self.validator.validate(str(saved_path), required_columns):
                return {
                    "success": False,
                    "message": "CSV file failed validation."
                }

            # Return information about the successful upload
            return {
                "success": True,
                "message": "CSV uploaded successfully.",
                "filename": unique_filename,
                "original_filename": original_filename,
                "file_path": str(saved_path),
                "uploaded_by": user_id
            }

        # Handle errors when reading or saving the file
        except (OSError, TypeError, ValueError):
            return {
                "success": False,
                "message": "An error occurred while uploading the file."
            }

        finally:
            # Remove rejected or incomplete files from the upload folder
            # A successfully validated file will be kept
            if saved_path.exists():

                # Check whether the saved file is valid
                if not self.validator.validate(str(saved_path), required_columns):

                    # Delete the invalid file
                    saved_path.unlink()

    def get_upload_status(self, dataset_id):
        """
        Retrieve the status of an uploaded dataset.

        This function will be implemented when we connect
        the uploader to DatabaseManager and MySQL.
        """

        # Database integration has not been implemented yet
        return {
            "success": False,
            "message": "Upload status is not available yet."
        }