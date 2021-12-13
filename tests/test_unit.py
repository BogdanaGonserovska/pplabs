from model import User

import os
os.environ["ENVIRONMENT"] = "test";

from app import app, bcrypt, verify_password
from model import db
from tests.test_api import BaseTestCase

class TestAuthentication(BaseTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()
        
    def create_user_db(self, data):
        new_user = User(
            username = data['username'], 
            firstName = data['firstName'],
            lastName = data['lastName'], 
            email = data['email'], 
            password = bcrypt.generate_password_hash(data['password']).decode('utf-8'),
            phone = data['phone'],
            isActive = data['isActive'],
            isModerator = data['isModerator']
        )
    
        db.session.add(new_user)
        db.session.commit()
        return new_user


    def test_verify_password_failed(self):
        new_user = self.create_user_db(self.user_1_data)
        user = verify_password(self.user_1_data["username"], "InvalidPassword")
        self.assertIsNone(user)

    def test_verify_password_success(self):
        new_user = self.create_user_db(self.user_1_data)
        user = verify_password(self.user_1_data["username"], self.user_1_data["password"])
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.user_1_data["email"])
