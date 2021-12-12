# from unittest import TestCase
# from unittest.mock import patch, Mock
from unittest.mock import ANY
from flask import url_for
from flask_bcrypt import generate_password_hash
from flask_testing import TestCase
from model import User, UserLogin, Articleversion, Article, ArticleVersionStatus
import base64

import os
os.environ["ENVIRONMENT"] = "test";

from app import app, bcrypt
from model import db

class BaseTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.admin_credentials = {
            "username" : "MODERATOR",
            # "firstName" = "Admin",
            # "lastName" = "Admin",
            # "email" = "admin@gmail.com"
            "password" : "ModeratorAdmin",
            # "phone" = "phone0",
            # "isModerator" = True,
            # "isActive" = True,
        }

        self.user_1_data= {
            "username" : "username1",
            "firstName" : "firstName1",
            "lastName" : "lastName1",
            "email" : "email1",
            "password" : "password1",
            "phone" : "phone1",
            "isModerator" : False,
            "isActive" : True,
        }

        self.user_2_data={
            "username" : "username2",
            "firstName" : "firstName2",
            "lastName" : "lastName2",
            "email" : "email2",
            "password" : "password2",
            "phone" : "phone2",
            "isModerator" : False,
            "isActive" : True,
        }

        self.user_1_data_hashed ={
            **self.user_1_data,
            "password": bcrypt.generate_password_hash(self.user_1_data["password"]).decode('utf-8'),
        }

        self.user_2_data_hashed = {
            **self.user_2_data,
            "password": bcrypt.generate_password_hash(self.user_2_data["password"]).decode('utf-8'),
        }

        self.user_1_credentials = {
            "username" : self.user_1_data["username"],
            "password" : self.user_1_data["password"],
        }

        self.user_2_credentials = {
            "username": self.user_2_data["username"],
            "password": self.user_2_data["password"],
        }
        self.client = self.app.test_client()

        #mysql_engine = getSqlEngine()
        
        db.drop_all()
        #db.metadata.drop_all(db.engine)
        db.create_all()

        #self.session = getSession(mysql_engine)

        #self.context = self.app.test_request_context()

    def tearDown(self):
        db.session.remove()
        #self.context.pop()
        # TESTING = True

    def create_app(self):
        return app

    def get_auth_headers(self, credentials):
        base64_credentials = base64.b64encode((credentials["username"] + ":" + credentials["password"]).encode("utf-8")).decode("utf-8")
        return {"Authorization": "Basic " + base64_credentials}

    def create_user(self, userData, checkIsSuccessful: bool = False):
        url = url_for('create_user')
        resp = self.client.post(url, json=userData)
        
        if checkIsSuccessful:
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {'message': 'successful operation'})

        return resp


class TestUsers(BaseTestCase):
    def test_create_user(self):
        resp = self.create_user(self.user_1_data, checkIsSuccessful = True)

        found_user = db.session.query(User).filter(User.username==self.user_1_data['username']).one_or_none()
        self.assertIsNotNone(found_user)

        resp = self.create_user(self.user_1_data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {'message': 'This username already exists'})

        self.user_1_data['username'] = 'another_user'
        resp = self.create_user(self.user_1_data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {'message': 'This email is taken'})

    def test_get_user(self):
        resp = self.create_user(self.user_1_data)

        user2name = self.user_2_data['username']
        url = url_for('get_user', username=user2name)
        resp = self.client.get(url, headers = self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {'message': 'User not found'})

        resp = self.create_user(self.user_2_data, checkIsSuccessful = True)

        resp = self.client.get(url, headers = self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {'message': "You don't have required permission"})

        user1name = self.user_1_data['username']
        url = url_for('get_user', username=user1name)
        resp = self.client.get(url, headers = self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["username"], user1name)

    def test_edit_user(self):
        resp = self.create_user(self.user_1_data)

        user2name = self.user_2_data['username']
        url = url_for('edit_user', username=user2name)
        resp = self.client.put(url, headers = self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {'message': 'User not found'})

