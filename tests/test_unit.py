from unittest import TestCase
from unittest.mock import patch, Mock
from schema import UserSchema, ArticleSchema, ArticleVersionSchema
from model import User, Article, Articleversion

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Ira.ko03@127.0.0.1:3306/articles_test"

from app import bcrypt, verify_password

#from test_api import BaseTestCase

@patch("model.Session")
class TestAuthenticate(TestCase):
    def setUp(self):
        # articleservice.config['SECRET_KEY']=

        self.admin_username = "MODERATOR",
        self.admin_password = "ModeratorAdmin"
        self.hashed_admin_password = bcrypt.generate_password_hash(self.admin_password).decode('utf-8')
        self.user_username = 'MickeyMouse'
        self.user_password = 'MickeY123'
        self.hashed_user_password = bcrypt.generate_password_hash(self.user_password).decode('utf-8')

    def test_verify_password_failed(self, Session):
        #Session().query().filter_by().one_or_none = Mock(return_value=User(password=self.hashed_admin_password))
        user = verify_password(self.admin_username, "InvalidPassword")
        self.assertIsNone(user)

