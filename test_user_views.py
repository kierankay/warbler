"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from models import User, db

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app

db.create_all()
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['cool']


class ViewModelTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        
        User.query.delete()

        self.client = app.test_client()

    def test_user_creation(self):
        with app.test_client() as client:
            url = '/signup'
            data = {
                "username": "test4",
                "email": "test4@test.com",
                "password": "testtest"
            }
            response = client.post(url, data=data, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            query = User.query.filter(User.username == 'test4').first()
            self.assertIsInstance(query, User)

            fail_data = {
                "username": "test3",
                "email": "test3@test.com",
                "password": ""
            }
            response = client.post(url, data=fail_data, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Field must be at least 6 characters long.', str(
                response.data))

    def test_user_login(self):
        with app.test_client() as client:
            url = '/login'
            data2 = {
                "username": "test5",
                "email": "test5@test.com",
                "password": "testtest"
            }
            response = client.post('/signup', data=data2, follow_redirects=True)
            data2 = {
                "username": "test5",
                "password": "testtest"
            }
            response = client.post(url, data=data2, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Hello, test5!', str(response.data))
