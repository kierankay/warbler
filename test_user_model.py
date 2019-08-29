"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

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

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)

        u2 = User(
            email="test2@test2.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
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
