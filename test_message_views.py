"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

import os
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from unittest import TestCase
from models import db, connect_db, Message, User
from sqlalchemy.orm.exc import NoResultFound


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        testmessage = Message(user_id=self.testuser2.id, text="1238841092419")
        db.session.add(testmessage)
        db.session.commit()
        self.testmessage_id = Message.query.filter(Message.text=="1238841092419").first().id

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            num_messages_before = Message.query.count()
            resp = c.post("/messages/new", data={"text": "Hello"})
            self.assertEqual(resp.status_code, 302)

            num_messages_after = Message.query.count()
            # Make sure it redirects
            self.assertEqual(num_messages_after - num_messages_before, 1)
    
    def test_delete_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            # add the message
            testmessage2 = Message(user_id=self.testuser.id, text="18249126739128371294")
            db.session.add(testmessage2)
            db.session.commit()

            #check messages before and after deletion count
            num_messages_before = Message.query.count()
            response = c.post(f'/messages/{testmessage2.id}/delete', follow_redirects=True)
            num_messages_after = Message.query.count()

            #assertions
            self.assertEqual(response.status_code, 200)
            self.assertEqual(num_messages_after - num_messages_before, -1) 
            message_search = Message.query.filter(Message.text == '18249126739128371294').one_or_none()
            self.assertEqual(message_search, None)

    def test_logged_out_delete_message(self):
        with self.client as c:
            testmessage2 = Message(user_id=self.testuser.id, text="18247129487124")
            db.session.add(testmessage2)
            db.session.commit()

            num_messages_before = Message.query.count()
            response = c.post(f'/messages/{testmessage2.id}/delete', follow_redirects=True)
            num_messages_after = Message.query.count()

            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', str(response.data))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(num_messages_after - num_messages_before, 0) 

            message_search = Message.query.filter(Message.text == '18247129487124').one_or_none()
            self.assertEqual(message_search.text, '18247129487124')

    def test_logged_out_add_message(self):
        with self.client as c:
            num_messages_before = Message.query.count()
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            num_messages_after = Message.query.count()

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', str(resp.data))

            self.assertEqual(num_messages_after - num_messages_before, 0)

    # def test_logged_in_delete_others_message(self):
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id

    #         num_messages_before = Message.query.count()
    #         response = c.post(f'/messages/{self.testmessage_id}/delete', follow_redirects=True)
    #         num_messages_after = Message.query.count()

    #         not_deleted_message = Message.query.filter(Message.text=='1238841092419').first()
    #         self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', str(response.data))
    #         self.assertEqual(not_deleted_message.text, '1238841092419')
    #         self.assertEqual(num_messages_after - num_messages_before, 0)
