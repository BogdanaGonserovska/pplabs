import datetime, uuid
import sqlalchemy

from typing import List, Any
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.sql import exists
from sqlalchemy.orm import sessionmaker, Query, aliased
from model import User, UserLogin, Articleversion, Article, ArticleVersionStatus

class ArticleShortInfo:
    id: int
    name: str
    authorName: str
    publishDate: datetime.datetime

class ArticleInfo(ArticleShortInfo):
    text: str
    versionId: int
    lastModificationDate: datetime.datetime

class ArticleVersionShortInfo:
    id: int
    name: str
    publishDate: datetime.datetime
    lastModificationDate: datetime.datetime
    versionDate: datetime.datetime
    authorName: str
    editorName: str
    moderatorName: str
    status: ArticleVersionStatus


class ArticleVersionInfo(ArticleVersionShortInfo):
    text: str
    originalId: int
    originalName: str
    originalText: str
    originalDate: datetime.datetime


class ArticleServiceManager():
    def __init__(self):
        self.session = self.createSession()

    def createSession(self):
        mysql_engine = create_engine("mysql+pymysql://root:Ira.ko03@127.0.0.1:3306/article_service", encoding="utf-8", echo=True, future=True)
        Session = sessionmaker(bind=mysql_engine)
        return Session()

    def userExists(self, username: str)->bool:
        return self.session.query(self.session.query(User).filter(User.username == username).exists()).scalar()

    def createUser(self, username: str, firstName: str, lastName: str, email: str, password: str, phone: str) -> str:
        user: User = self.session.query(User).filter(User.username == username).one_or_none()
        if (user != None):
            raise Exception("User already exists")

        user = User(username = username,
            firstName = firstName,
            lastName = lastName,
            email = email,
            password = password,
            phone = phone,
            isModerator = False,
            isActive = True)
        self.session.add(user)
        self.session.commit()
        return user

    def generateUniqueToken(self) -> str:
        return str(uuid.uuid4())

    def loginUser(self, userName: str, password: str) -> str:
        user: User = self.session.query(User).filter(User.username == userName, User.isActive == True).one_or_none()
        if (user == None):
            raise Exception("User does not exist or is inaactive")
        if (user.password != password):
            raise Exception("Invalid password. Please try again")
        userlogin: UserLogin = UserLogin(userId = user.id,
            token = self.generateUniqueToken(),
            loginDate = datetime.datetime.utcnow())
        self.session.add(userlogin)
        self.session.commit()
        return userlogin.token

    def getCurrentUser(self, token: str) -> User:
        uselogin: UserLogin = self.session.query(UserLogin).filter(UserLogin.token == token, UserLogin.logoutDate == None).one_or_none()
        if (uselogin == None):
            raise Exception("The login token is invalid or expired")

        user = self.session.query(User).filter(User.id == uselogin.userId).one()
        if (user.isActive == False):
            raise Exception("The user is not longer active")

        return user

    def logoutUser(self,token: str):
        userlogin: UserLogin = self.session.query(UserLogin).filter(UserLogin.token == token, UserLogin.logoutDate == None).one_or_none()
        if (userlogin == None):
            return
        userlogin.logoutDate = datetime.datetime.utcnow()
        self.session.commit()
        return

    def setAsModerator(self, userId: int):
        user: User = self.session.query(User).filter(and_(User.id == userId)).one_or_none()
        if (user == None):
            raise Exception("User does not exist")
        if (user.isActive == False):
            raise Exception("User is inactive")
        user.isModerator = True
        self.session.commit()
        return

    def createVersion(self, editorUser: User, name: str, text: str, originalVersionId: int = None) -> Articleversion:
        originalVersion: Articleversion = None
        if (originalVersionId != None):
            originalVersion = self.session.query(Articleversion).filter(Articleversion.id == originalVersionId).one_or_none()
            if (originalVersion == None):
                raise Exception("Version does not exist")
            if (originalVersion.status != 'accepted'):
                raise Exception("Original version is not accepted yet")
        version = Articleversion(editorUserId = editorUser.id,
            date = datetime.datetime.utcnow(),
            originalId = originalVersionId,
            articleId = originalVersion and originalVersion.articleId or None,
            name = name,
            text = text,
            status = 'new')
        self.session.add(version)
        self.session.commit()
        return version

    def acceptVersion(self, moderatorUser: User, versionId: int) -> Article:
        version: Articleversion = self.session.query(Articleversion).filter(Articleversion.id == versionId).one_or_none()
        if (version == None):
            raise Exception("Version does not exist")
        if (version.status == 'accepted'):
            raise Exception("Version is already accepted")
        if (version.status == 'declined'):
            raise Exception("Version was declined so cannot be accepted")

        article: Article = None
        if (version.articleId == None):
            authorUser: User = self.session.query(User).filter(User.id == version.editorUserId).one()
            article = Article(name = version.name,
                text = version.text,
                authorUserId = authorUser.id,
                versionId = version.id,
                publishDate = datetime.datetime.utcnow())
            self.session.add(article)
        else:
            article: Article = self.session.query(Article).filter(Article.id == version.articleId).one()
            if (article.versionId != version.originalId):
                raise Exception("Article was changed while this version was prepared. Please decline with approppriate reason instead")
            article.name = version.name
            article.text = version.text,
            article.versionId = version.id,
            article.lastModificationDate = datetime.datetime.utcnow()

        version.moderatedDate = datetime.datetime.utcnow()
        version.moderatorUserId = moderatorUser.id
        version.status = 'accepted'
        version.articleId = article.id

        self.session.commit()

        return article

    def declineVersion(self, moderatorUser: User, versionId: int, declineReason: str) -> Articleversion:
        version: Articleversion = self.session.query(Articleversion).filter(Articleversion.id == versionId).one_or_none()
        if (version == None):
            raise Exception("Version does not exist")
        if (version.status == 'accepted'):
            raise Exception("Version was accepted so cannot be declined")
        if (version.status == 'declined'):
            raise Exception("Version was already declined")

        version.moderatedDate = datetime.datetime.utcnow()
        version.moderatorUserId = moderatorUser.id
        version.status = 'declined'
        version.declineReason = declineReason

        self.session.commit()
        return version

    def findArticles(self, searchText: str) -> List[ArticleShortInfo]:
        articles: List[ArticleShortInfo] = self.session.query(\
                Article.id, Article.name,\
                (User.firstName + " " + User.lastName).label("authorName"),\
                Article.publishDate)\
            .join(Article.user)\
            .filter(or_(Article.name.like('%' + searchText + '%'), Article.text.like('%' + searchText + '%'), (User.firstName + " " + User.lastName).like('%' + searchText + '%')))\
            .all()
        return articles

    def getArticle(self, id: int) -> ArticleInfo:
        article: ArticleInfo = self.session.query(\
                Article.id, Article.name,\
                (User.firstName + " " + User.lastName).label("authorName"),\
                Article.publishDate, Article.text, Article.versionId, Article.lastModificationDate)\
            .join(Article.user)\
            .filter(Article.id == id)\
            .one_or_none()
        if article == None:
            raise Exception("Article does not exist")
        return article

    def findArticleVersions(self, status: ArticleVersionStatus, searchText: str) -> List[ArticleVersionShortInfo]:
        Editor = aliased(User)
        Moderator = aliased(User)
        articleVersions: List[ArticleVersionShortInfo] = self.session.query(\
                Articleversion.id, Articleversion.name,\
                Article.publishDate, Article.lastModificationDate,\
                Articleversion.date.label("versionDate"),
                (User.firstName + " " + User.lastName).label("authorName"),\
                (Editor.firstName + " " + Editor.lastName).label("editorName"),\
                (Moderator.firstName + " " + Moderator.lastName).label("moderatorName"),\
                Articleversion.status)\
            .join(Editor, Articleversion.user)\
            .join(Moderator, Articleversion.user1)\
            .join(Articleversion.article)\
            .join(Article.user)\
            .filter(Articleversion.status == status, Article.name.like('%' + searchText + '%'))\
            .all()
        return articleVersions

    def getArticleVersion(self, id: int) -> ArticleVersionInfo:
        Editor = aliased(User)
        Moderator = aliased(User)
        Original = aliased(Articleversion)
        articleVersion: ArticleVersionInfo = self.session.query(\
                Articleversion.id, Articleversion.name,\
                Article.publishDate, Article.lastModificationDate,\
                Articleversion.date.label("versionDate"),
                (User.firstName + " " + User.lastName).label("authorName"),\
                (Editor.firstName + " " + Editor.lastName).label("editorName"),\
                (Moderator.firstName + " " + Moderator.lastName).label("moderatorName"),\
                Articleversion.text,\
                Articleversion.status,\
                Articleversion.originalId,\
                Original.name.label("originalName"),\
                Original.text.label("originalText"),\
                Original.date.label("originalDate"))\
            .join(Editor, Articleversion.user)\
            .join(Moderator, Articleversion.user1)\
            .join(Articleversion.article)\
            .join(Article.user)\
            .join(Original, Articleversion.parent)\
            .filter(Articleversion.id == id)\
            .one_or_none()

        if (articleVersion == None):
            raise Exception("Article Version does not exist")

        return articleVersion

def setUpFirstModerator(articleServiceManager: ArticleServiceManager):
    if not articleServiceManager.userExists("Tom2"):
        moderatorUser = articleServiceManager.createUser("Tom2", "Tom", "Jerry", "tom@gmail.com", "ttttom", "+23 0394756182")
        articleServiceManager.setAsModerator(moderatorUser.id)

