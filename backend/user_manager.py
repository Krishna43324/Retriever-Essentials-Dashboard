"""
skeleton code
class to handle account manager, authority based on role,
account ownership, etc.
to be implement 
"""

class UserManager:

    def __init__(self, database_manager):
        # Store the database manager for accessing user accounts
        self.database_manager = database_manager

    def create_user(self, admin_id, user_data):
        # Create a new account after checking admin permissions
        pass

    def get_user(self, user_id):
        # Retrieve information about a specific user
        pass

    def get_all_users(self, admin_id):
        # Retrieve all user accounts for an administrator
        pass

    def update_user(self, admin_id, user_id, updated_data):
        # Update another user's account information
        pass

    def update_own_profile(self, user_id, updated_data):
        # Allow users to update permitted personal information
        pass

    def delete_user(self, admin_id, user_id):
        # Delete an account after checking admin permissions
        pass

    def change_user_role(self, admin_user, target_user, new_role):
        # Check whether the requesting user is an admin
        if not admin_user.can_manage_accounts():
            return False
