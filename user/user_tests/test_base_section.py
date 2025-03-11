from django.test import TestCase
from django.contrib.auth import get_user_model
from section.models import Section

User = get_user_model()

class UserBaseSectionTest(TestCase):

    def test_user_creation_creates_section(self) -> None:
        """Checks that when a user is created, a section is created and bound to the user"""
        user = User.objects.create(username='testuser')

        # Check that the section has been created
        self.assertIsNotNone(user.base_section)

        # Check that the section actually exists in the database
        section = Section.objects.get(id=user.base_section.id)  # type: ignore
        self.assertEqual(section.name, 'Home')

        # Check that the user is in the created section
        self.assertTrue(section.users.filter(id=user.id).exists())

    def test_save_does_not_create_new_section_on_update(self) -> None:
        """Checks that a new section is not created when a user is updated"""
        user = User.objects.create(username='testuser')
        initial_section = user.base_section

        # Change something on the user and save
        user.telegram_id = 123456789
        user.save()

        # Check that the section remains the same
        self.assertEqual(user.base_section, initial_section)

        # Check that no new sections have appeared
        self.assertEqual(Section.objects.count(), 1)

    def test_section_is_associated_correctly(self) -> None:
        """Verifies that the section is properly bound to the user"""
        user = User.objects.create(username='anotheruser')
        section: Section = user.base_section  # type: ignore

        # Check that the section exists and is associated with the user
        self.assertEqual(section.users.count(), 1)
        self.assertEqual(section.users.first(), user)