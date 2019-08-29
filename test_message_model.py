"""Message model tests."""

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
from models import db, Message, User, Follows


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test model for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user1 = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=""
        )
        db.session.add(user1)

        user2 = User.signup(
            email="test2@test2.com",
            username="testuser2",
            password="HASHED_PASSWORD2",
            image_url=""
        )
        db.session.add(user2)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up added sample data"""
        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""

        #test message creation
        user2 = User.query.filter(User.username=="testuser2").first()
        msg1 = Message(text="Hi there", user_id=user2.id)

        self.assertEqual(msg1.text, "Hi there")
