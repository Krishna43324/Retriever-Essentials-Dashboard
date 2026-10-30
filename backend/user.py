# ============================================================
# User.py
#
# Represents a user of the Retriever Essentials Dashboard.
#
# Each user has a unique ID, username, role, and department.
#
# This class determines what actions a user is allowed to
# perform based on their assigned role.
# ============================================================

class User:

    # Define the roles supported by the website
    VALID_ROLES = ["admin", "staff", "viewer"]

    def __init__(self, user_id, username, role, department=None):

        # Store the user's information
        self.user_id = user_id
        self.username = username
        self.role = role.lower()
        self.department = department

        # Check whether the assigned role is valid
        if self.role not in self.VALID_ROLES:
            raise ValueError("Invalid user role.")

    def can_upload(self):
        # Admins and staff can upload CSV files
        return self.role in ["admin", "staff"]

    def can_manage_accounts(self):
        # Only admins can manage accounts
        return self.role == "admin"

    def can_view_dashboard(self):
        # All valid roles can view the dashboard
        return self.role in self.VALID_ROLES

    def can_delete_dataset(self, uploaded_by):
        # Admins can delete any dataset
        if self.role == "admin":
            return True

        # Staff can only delete their own uploads
        if self.role == "staff":
            return self.user_id == uploaded_by

        return False

    def change_role(self, new_role):
        # Admin can update user's roles
        # Admin authorization can be checked in user_manager

        # Convert the new role to lowercase
        new_role = new_role.lower()

        # Check whether the role is valid
        if new_role not in self.VALID_ROLES:
            return False

        # Update the user's role
        self.role = new_role

        return True