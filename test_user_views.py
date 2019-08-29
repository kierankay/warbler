"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
from flask import session
from models import User, db, Follows
from unittest import TestCase
from app import app
import os
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

db.create_all()
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['cool']


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        db.session.rollback()
        User.query.delete()
        Follows.query.delete()
        self.client = app.test_client()

        # insert a user in the db
        # put that user on self.user = user

        self.user5 = User.signup(username="test5",
                                 email="test5@test.com",
                                 password="testtest",
                                 image_url="")

        self.user6 = User.signup(username="test6",
                                 email="test6@test.com",
                                 password="testtest",
                                 image_url="")
        db.session.commit()

        follow = Follows(
            user_being_followed_id=self.user5.id,
            user_following_id=self.user6.id
        )
        db.session.add(follow)
        db.session.commit()

    def _login(self, username, password):
        with app.test_client() as client:
            url = '/login'
            user_login = {
                "username": username,
                "password": password
            }
            response = client.post(url, data=user_login, follow_redirects=True)
        return response

    def test_user_creation(self):
        with app.test_client() as client:
            url = '/signup'
            user4 = {
                "username": "test4",
                "email": "test4@test.com",
                "password": "testtest"
            }
            response = client.post(url, data=user4, follow_redirects=True)
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
        # successful login
        response = self._login(
            username=self.user5.username, password="testtest")
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hello, test5!', str(response.data))

        # failed logins
        response = self._login(
            username="test500", password="testtest")
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid credentials.', str(response.data))

        response = self._login(
            username="test5", password="testtttt")
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid credentials.', str(response.data))

    def test_followers_page(self):
        with app.test_client() as client:
            with client.session_transaction() as s:
                s["curr_user"] = self.user5.id

            self._login(username=self.user5.username, password="testtest")

            url = f"/users/{self.user5.id}/followers"
            response = client.get(url, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('<p>@test6</p>', str(response.data))
