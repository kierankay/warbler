"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
import os
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test model for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up added sample data"""
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=""
        )
        db.session.add(u)

        u2 = User.signup(
            email="test2@test2.com",
            username="testuser2",
            password="HASHED_PASSWORD2",
            image_url=""
        )
        db.session.add(u2)
        db.session.commit()

        follow = Follows(
            user_being_followed_id=u.id,
            user_following_id=u2.id
        )
        db.session.add(follow)

        db.session.commit()

        # Users should have no messages
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u2.messages), 0)

        # relationship property return correct number of followers
        self.assertEqual(len(u.followers), 1)
        self.assertEqual(len(u2.followers), 0)

        # relationship property returns correct number of users followed
        self.assertEqual(len(u.following), 0)
        self.assertEqual(len(u2.following), 1)

        # followed_by function returns the correct output
        self.assertEqual(u.is_followed_by(u2), True)
        self.assertEqual(u2.is_followed_by(u), False)

        # is_following function returns the correct output
        self.assertEqual(u.is_following(u2), False)
        self.assertEqual(u2.is_following(u), True)

        # User instance should return helpful repr on instance call
        self.assertEqual(str(u), f"<User #{u.id}: testuser, test@test.com>")

        # Checking for new user creation through .signup class method
        new_user = User.signup("new_user", "new_user@test.com", "HASHED_PW", "")
        db.session.add(new_user)
        db.session.commit()
        self.assertEqual(str(new_user.username), 'new_user')

        # Checking for invalid signup
        new_user_invalid = User.signup("new_user2", "new_user@test.com", "HASHED_PW", "")
        db.session.add(new_user_invalid)
        # db.session.commit()
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

        #authenticating a valid username
        u2 = User.authenticate("testuser2", "HASHED_PASSWORD2")
        self.assertEqual(u2.username, "testuser2")

        #username failing authentication
        u2_fail = User.authenticate("test", "HASHED_PASSWORD2")
        self.assertEqual(u2_fail, False)

        #password failing authentication
        u2_fail_pw = User.authenticate("testuser2", "testtest")
        self.assertEqual(u2_fail_pw, False)