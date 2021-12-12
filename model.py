from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Article(db.Model):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    authorUserId = Column(ForeignKey('user.id', name = 'article_ibfk_2'), nullable=False, index=True)
    text = Column(Text, nullable=False)
    versionId = Column(ForeignKey('articleversion.id', name = 'article_ibfk_1'), nullable=False, index=True)
    publishDate = Column(DateTime, nullable=False)
    lastModificationDate = Column(DateTime)

    user = relationship('User')
    articleversion = relationship('Articleversion', primaryjoin='Article.versionId == Articleversion.id')

ArticleVersionStatus = Enum('new', 'accepted', 'declined')

class Articleversion(db.Model):
    __tablename__ = 'articleversion'

    id = Column(Integer, primary_key=True)
    editorUserId = Column(ForeignKey('user.id', ondelete='RESTRICT', onupdate='RESTRICT', name = 'articleversion_ibfk_2'), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    originalId = Column(ForeignKey('articleversion.id', ondelete='RESTRICT', onupdate='RESTRICT', name = 'articleversion_ibfk_3'))
    articleId = Column(ForeignKey('article.id', ondelete='RESTRICT', onupdate='RESTRICT', name = 'articleversion_ibfk_1'), index=True)
    name = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    status = Column(ArticleVersionStatus, nullable=False)
    moderatorUserId = Column(ForeignKey('user.id', ondelete='RESTRICT', onupdate='RESTRICT', name='articleversion_ibfk_4'), index=True)
    moderatedDate = Column(DateTime, index=True)
    declineReason = Column(String(255))

    article = relationship('Article', primaryjoin='Articleversion.articleId == Article.id')
    user = relationship('User', primaryjoin='Articleversion.editorUserId == User.id')
    user1 = relationship('User', primaryjoin='Articleversion.moderatorUserId == User.id')
    parent = relationship('Articleversion', remote_side=[id])


class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    firstName = Column(String(50), nullable=False)
    lastName = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    phone = Column(String(15))
    isModerator = Column(Boolean, nullable=False)
    isActive = Column(Boolean, nullable=False)


class UserLogin(db.Model):
    __tablename__ = 'userlogins'

    id = Column(Integer, primary_key=True)
    userId = Column(ForeignKey('user.id'), nullable=False, index=True, name = 'userlogins_ibfk_1')
    token = Column(String(50), nullable=False, unique=True)
    loginDate = Column(DateTime, nullable=False)
    logoutDate = Column(DateTime)

    user = relationship('User')
