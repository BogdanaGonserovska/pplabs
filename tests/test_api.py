from unittest.mock import ANY
from flask import url_for
from flask_bcrypt import generate_password_hash
from flask_testing import TestCase
from model import User, Articleversion, Article, ArticleVersionStatus
import base64

import os
os.environ["ENVIRONMENT"] = "test";

from app import app, bcrypt
from model import db

class BaseTestCase(TestCase):
    def setUp(self):
        super().setUp()

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

        self.version_1_data = {
            "name" : "aricle1",
            "text" : "Today is ..."
         }

        self.version_2_data = {
            "name" : "aricle2",
            "text" : "yesterday was ..."
         }

        self.client = self.app.test_client()

        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()

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
            self.assertTrue("id" in resp.json)
            self.assertIsNotNone(resp.json["id"])

        return resp

    def create_version(self, versionData, credentials, checkIsSuccessful: bool = False):
        url = url_for('create_version')
        resp = self.client.post(url, json=versionData, headers = self.get_auth_headers(credentials))
        
        if checkIsSuccessful:
            self.assertEqual(resp.status_code, 200)
            self.assertTrue("id" in resp.json)
            self.assertIsNotNone(resp.json["id"])

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
        resp = self.client.put(url, json=self.user_2_data, headers = self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {'message': 'User not found'})

        resp = self.create_user(self.user_2_data, checkIsSuccessful = True)

        resp = self.client.put(url, json=self.user_2_data, headers = self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {'message': 'You can\'t update this user'})

        user1name = self.user_1_data['username']
        url = url_for('edit_user', username=user1name)
        self.user_1_data["username"] = self.user_2_data["username"]
        resp = self.client.put(url, json=self.user_1_data, headers = self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {'message':'This username already exists'})

        url = url_for('edit_user', username=user1name)
        self.user_1_data["email"] = self.user_2_data["email"]
        self.user_1_data["username"] = user1name
        resp = self.client.put(url, json=self.user_1_data, headers = self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {'message':'This email is taken'})

        url = url_for('edit_user', username=user1name)

        self.user_1_data["username"] = "newusername1"
        self.user_1_data["firstName"] = "newfirstName1"
        self.user_1_data["lastName"] = "newlastName1"
        self.user_1_data["email"] = "newemail1"
        self.user_1_data["phone"] = "newphone1"
        self.user_1_data["password"] = "newpassword1"

        resp = self.client.put(url, json=self.user_1_data, headers = self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 200)

        found_user = db.session.query(User).filter(User.username==self.user_1_data["username"]).one_or_none()
        self.assertIsNotNone(found_user)

        self.assertEqual(found_user.username, self.user_1_data["username"])
        self.assertEqual(found_user.firstName, self.user_1_data["firstName"])
        self.assertEqual(found_user.lastName, self.user_1_data["lastName"])
        self.assertEqual(found_user.email, self.user_1_data["email"])
        self.assertEqual(found_user.phone, self.user_1_data["phone"])
        self.assertTrue(bcrypt.check_password_hash(found_user.password, self.user_1_data["password"]))

    def test_delete_user(self):
        self.user_1_data["isModerator"] = False
        resp = self.create_user(self.user_1_data, checkIsSuccessful = True)

        user2name = self.user_2_data['username']
        url = url_for('delete_user', username=user2name)
        resp = self.client.delete(url, headers = self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {'message': 'User not found'})

        self.user_2_data["isModerator"] = True
        resp = self.create_user(self.user_2_data, checkIsSuccessful = True)

        resp = self.client.delete(url, headers = self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {'message':'You don\'t have permission to delete users'})

        user1name = self.user_1_data['username']
        url = url_for('delete_user', username=user1name)
        resp = self.client.delete(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {'message':'successfull operation'})

        found_user = db.session.query(User).filter(User.username==self.user_1_data["username"]).one_or_none()
        self.assertIsNone(found_user)

        resp = self.create_user(self.user_1_data, checkIsSuccessful = True)
        resp = self.create_version(self.version_1_data, self.user_1_credentials, checkIsSuccessful = True)

        resp = self.client.delete(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {'message':'The user cannot be deleted because it\'s referenced in articles history'})
        

class TestVersions(BaseTestCase):
    def test_create_version(self):
        resp = self.create_user(self.user_1_data, checkIsSuccessful = True)
        user1Id = resp.json["id"]

        resp = self.create_version(self.version_1_data, self.user_1_credentials, checkIsSuccessful = True)
        originalId = resp.json["id"]

        self.version_2_data["originalId"] = 100
        resp = self.create_version(self.version_2_data, self.user_1_credentials)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {'message': 'Original version is not found'})

        self.version_2_data["originalId"] = originalId        
        resp = self.create_version(self.version_2_data, self.user_1_credentials, checkIsSuccessful = True)
        versionId = resp.json["id"]

        find_version = db.session.query(Articleversion).filter(Articleversion.id == versionId).one_or_none()
        self.assertIsNotNone(find_version)
        self.assertEqual(self.version_2_data["originalId"], find_version.originalId)
        self.assertEqual("new", find_version.status)
        self.assertEqual(self.version_2_data["name"], find_version.name)
        self.assertEqual(self.version_2_data["text"], find_version.text)
        self.assertEqual(user1Id, find_version.editorUserId)


    def test_get_versions(self):
        url = url_for('get_versions')

        self.user_1_data["isModerator"] = False
        resp = self.create_user(self.user_1_data, checkIsSuccessful = True)

        resp = self.client.get(url, headers = self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {'message': 'You don\'t have permission to get versions'})

        self.user_2_data["isModerator"] = True
        resp = self.create_user(self.user_2_data, checkIsSuccessful = True)

        resp = self.client.get(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {'message': 'New versions not found'})

        resp = self.create_version(self.version_1_data, self.user_1_credentials, checkIsSuccessful = True)
        resp = self.create_version(self.version_2_data, self.user_2_credentials, checkIsSuccessful = True)

        resp = self.client.get(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json), 2)

    def test_get_version(self):

        self.user_1_data["isModerator"] = False
        resp = self.create_user(self.user_1_data, checkIsSuccessful = True)

        url = url_for('get_version', ChangeId=5)
        resp = self.client.get(url, headers = self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {'message': 'You don\'t have permission to view this version'})

        self.user_2_data["isModerator"] = True
        resp = self.create_user(self.user_2_data, checkIsSuccessful = True)

        resp = self.client.get(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {'message': 'Version not found'})

        resp = self.create_version(self.version_1_data, self.user_1_credentials, checkIsSuccessful = True)

        versionId = resp.json["id"]
        url = url_for('get_version', ChangeId=versionId)
        resp = self.client.get(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["id"], versionId)
        self.assertEqual(resp.json["name"], self.version_1_data["name"])
        self.assertEqual(resp.json["text"], self.version_1_data["text"])

    def test_accept_version(self):
        self.user_1_data["isModerator"] = False
        resp = self.create_user(self.user_1_data, checkIsSuccessful = True)
        user1Id = resp.json["id"]

        url = url_for('accept_version', ChangeId=5)
        resp = self.client.put(url, headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {'message': 'You don\'t have permission to moderate articles'})

        self.user_2_data["isModerator"] = True
        resp = self.create_user(self.user_2_data, checkIsSuccessful = True)
        user2Id = resp.json["id"]

        resp = self.client.put(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {'message': 'Version not found'})

        resp = self.create_version(self.version_1_data, self.user_1_credentials, checkIsSuccessful = True)

        versionId = resp.json["id"]
        url = url_for('accept_version', ChangeId=versionId)
        resp = self.client.put(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["authorUserId"], user1Id)
        self.assertEqual(resp.json["versionId"], versionId)
        self.assertEqual(resp.json["name"], self.version_1_data["name"])
        self.assertEqual(resp.json["text"], self.version_1_data["text"])

        find_version = db.session.query(Articleversion).filter(Articleversion.id == versionId).one()
        self.assertEqual(resp.json["id"], find_version.articleId)
        self.assertEqual("accepted", find_version.status)
        self.assertEqual(user2Id, find_version.moderatorUserId)

        resp = self.client.put(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {'message': 'Version is already moderated'})

        self.version_2_data["originalId"] = versionId
        resp = self.create_version(self.version_2_data, self.user_1_credentials, checkIsSuccessful = True)
        user1versionId = resp.json["id"]
        resp = self.create_version(self.version_2_data, self.user_2_credentials, checkIsSuccessful = True)
        user2versionId = resp.json["id"]

        url = url_for('accept_version', ChangeId=user2versionId)
        resp = self.client.put(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["versionId"], user2versionId)
        self.assertEqual(resp.json["name"], self.version_2_data["name"])
        self.assertEqual(resp.json["text"], self.version_2_data["text"])

        find_version = db.session.query(Articleversion).filter(Articleversion.id == user2versionId).one()
        self.assertEqual(resp.json["id"], find_version.articleId)
        self.assertEqual("accepted", find_version.status)
        self.assertEqual(user2Id, find_version.moderatorUserId)

        url = url_for('accept_version', ChangeId=user1versionId)
        resp = self.client.put(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {'message': 'Article was changed by another user in parallel'})

    def test_decline_version(self):
        self.user_1_data["isModerator"] = False
        resp = self.create_user(self.user_1_data, checkIsSuccessful = True)
        user1Id = resp.json["id"]

        url = url_for('decline_version', ChangeId=5)
        resp = self.client.delete(url, headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {'message': 'You don\'t have permission to moderate articles'})

        self.user_2_data["isModerator"] = True
        resp = self.create_user(self.user_2_data, checkIsSuccessful = True)
        user2Id = resp.json["id"]

        resp = self.client.delete(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {'message': 'Version not found'})

        resp = self.create_version(self.version_1_data, self.user_1_credentials, checkIsSuccessful = True)
        versionId = resp.json["id"]
        declineReason = "test reason"

        url = url_for('decline_version', ChangeId=versionId)
        resp = self.client.delete(url, json={"declineReason": declineReason}, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {'message': 'successful operation'})

        find_version = db.session.query(Articleversion).filter(Articleversion.id == versionId).one()
        self.assertEqual("declined", find_version.status)
        self.assertEqual(user2Id, find_version.moderatorUserId)
        self.assertEqual(declineReason, find_version.declineReason)

        resp = self.client.delete(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {'message': 'Version is already moderated'})

class TestArticles(BaseTestCase):
    def test_get_articles(self):
        url = url_for('get_articles')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {'message': 'Articles not found'})

        self.user_1_data["isModerator"] = False
        resp = self.create_user(self.user_1_data, checkIsSuccessful = True)

        self.user_2_data["isModerator"] = True
        resp = self.create_user(self.user_2_data, checkIsSuccessful = True)

        resp = self.create_version(self.version_1_data, self.user_1_credentials, checkIsSuccessful = True)
        versionId = resp.json["id"]

        url = url_for('accept_version', ChangeId=versionId)
        resp = self.client.put(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 200)

        url = url_for('get_articles')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json), 1)
        self.assertEqual(resp.json[0]["versionId"], versionId)

    def test_get_article(self):
        url = url_for('get_article', ArticleId=5)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {'message': 'Article not found'})

        self.user_1_data["isModerator"] = False
        resp = self.create_user(self.user_1_data, checkIsSuccessful = True)

        self.user_2_data["isModerator"] = True
        resp = self.create_user(self.user_2_data, checkIsSuccessful = True)

        resp = self.create_version(self.version_1_data, self.user_1_credentials, checkIsSuccessful = True)
        versionId = resp.json["id"]

        url = url_for('accept_version', ChangeId=versionId)
        resp = self.client.put(url, headers = self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(resp.status_code, 200)
        articleId = resp.json["id"]

        url = url_for('get_article', ArticleId=articleId)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["id"], articleId)
        self.assertEqual(resp.json["name"], self.version_1_data["name"])
        self.assertEqual(resp.json["text"], self.version_1_data["text"])
