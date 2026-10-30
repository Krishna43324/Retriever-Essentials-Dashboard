# user_test.py
# Unit tests for the User class.
# These tests check role permissions and role changes.

import unittest

from user import User


class TestUser(unittest.TestCase):

    def setUp(self):
        """
        Create sample users before each test.
        """

        # Create one user for each role
        self.admin = User(1, "admin1", "admin")
        self.staff = User(2, "staff1", "staff")
        self.viewer = User(3, "viewer1", "viewer")

    def test_admin_can_upload(self):
        # Admins should be able to upload CSV files
        self.assertTrue(self.admin.can_upload())

    def test_staff_can_upload(self):
        # Staff should be able to upload CSV files
        self.assertTrue(self.staff.can_upload())

    def test_viewer_cannot_upload(self):
        # Viewers should not be able to upload CSV files
        self.assertFalse(self.viewer.can_upload())

    def test_admin_can_manage_accounts(self):
        # Admins should be able to manage user accounts
        self.assertTrue(self.admin.can_manage_accounts())

    def test_staff_cannot_manage_accounts(self):
        # Staff should not be able to manage other accounts
        self.assertFalse(self.staff.can_manage_accounts())

    def test_viewer_cannot_manage_accounts(self):
        # Viewers should not be able to manage other accounts
        self.assertFalse(self.viewer.can_manage_accounts())

    def test_all_roles_can_view_dashboard(self):
        # All three roles should be able to view the dashboard
        self.assertTrue(self.admin.can_view_dashboard())
        self.assertTrue(self.staff.can_view_dashboard())
        self.assertTrue(self.viewer.can_view_dashboard())

    def test_admin_can_delete_any_dataset(self):
        # Admin can delete a dataset uploaded by another user
        self.assertTrue(self.admin.can_delete_dataset(2))

    def test_staff_can_delete_own_dataset(self):
        # Staff can delete a dataset they uploaded
        self.assertTrue(self.staff.can_delete_dataset(2))

    def test_staff_cannot_delete_other_dataset(self):
        # Staff cannot delete another user's dataset
        self.assertFalse(self.staff.can_delete_dataset(3))

    def test_viewer_cannot_delete_dataset(self):
        # Viewer cannot delete any dataset
        self.assertFalse(self.viewer.can_delete_dataset(3))

    def test_change_role(self):
        # Change a viewer into a staff member
        result = self.viewer.change_role("staff")

        # Verify the role change was successful
        self.assertTrue(result)

        # Verify the user's role was updated
        self.assertEqual(self.viewer.role, "staff")

        # Verify the user now has staff permissions
        self.assertTrue(self.viewer.can_upload())

    def test_invalid_role_change(self):
        # Attempt to assign a role that does not exist
        result = self.staff.change_role("superuser")

        # Verify the change was rejected
        self.assertFalse(result)

        # Verify the original role remains unchanged
        self.assertEqual(self.staff.role, "staff")

    def test_invalid_role_creation(self):
        # Creating a user with an invalid role should fail
        with self.assertRaises(ValueError):
            User(4, "invalid_user", "superuser")


if __name__ == "__main__":
    unittest.main()