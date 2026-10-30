"""
skeleton code
Class to handle authentication processes for login
To be implemented with hash passwords methods
"""

class AuthManager:

    def __init__(self, database_manager):
        # Store the database manager for accessing user information
        self.database_manager = database_manager

    def authenticate(self, username, password):
        # Verify the username and password
        pass

    def authorize(self, user_id, action):
        # Check whether a user has permission to perform an action
        pass