#import datetime, uuid
#import sqlalchemy
#from typing import List
#from sqlalchemy import create_engine, or_, and_
#from sqlalchemy.sql import exists
#from sqlalchemy.orm import sessionmaker, Query, aliased

#from model import User, UserLogin, Articleversion, Article, ArticleVersionStatus

#def createUser(username: str, firstName: str, lastName: str, email: str, password: str, phone: str) -> str:
#    user = session.query(User).filter(User.username == username).one_or_none()
#    if (user != None):
#        raise Exception("User already exists")

#    user = User(username = username,
#        firstName = firstName,
#        lastName = lastName,
#        email = email,
#        password = password,
#        phone = phone,
#        isModerator = False,
#        isActive = True)
#    session.add(user)
#    session.commit()
#    return user

#def generateUniqueToken() -> str:
#    return str(uuid.uuid4())

#def loginUser(userName: str, password: str) -> str:
#    user: User = session.query(User).filter(User.username == userName, User.isActive == True).one_or_none()
#    if (user == None):
#        raise Exception("User does not exist or is inaactive")
#    if (user.password != password):
#        raise Exception("Invalid password. Please try again")
#    userlogin: UserLogin = UserLogin(userId = user.id,
#        token = generateUniqueToken(),
#        loginDate = datetime.datetime.utcnow())
#    session.add(userlogin)
#    session.commit()
#    return userlogin.token

#def getCurrentUser(token: str) -> User:
#    uselogin: UserLogin = session.query(UserLogin).filter(UserLogin.token == token, UserLogin.logoutDate == None).one_or_none()
#    if (uselogin == None):
#        raise Exception("The login token is invalid or expired")

#    user = session.query(User).filter(User.id == uselogin.userId).one()
#    if (user.isActive == False):
#        raise Exception("The user is not longer active")

#    return user

#def logoutUser(token: str):
#    userlogin: UserLogin = session.query(UserLogin).filter(UserLogin.token == token, UserLogin.logoutDate == None).one_or_none()
#    if (userlogin == None):
#        return
#    userlogin.logoutDate = datetime.datetime.utcnow()
#    session.commit()
#    return

#def setAsModerator(userId: int):
#    user: User = session.query(User).filter(and_(User.id == userId)).one_or_none()
#    if (user == None):
#        raise Exception("User does not exist")
#    if (user.isActive == False):
#        raise Exception("User is inactive")
#    user.isModerator = True
#    session.commit()
#    return

#def createVersion(editorUser: User, name: str, text: str, originalVersionId: int = None) -> Articleversion:
#    originalVersion: Articleversion = None 
#    if (originalVersionId != None):
#        originalVersion = session.query(Articleversion).filter(Articleversion.id == originalVersionId).one_or_none()
#        if (originalVersion == None):
#            raise Exception("Version does not exist")
#        if (originalVersion.status != 'accepted'):
#            raise Exception("Original version is not accepted yet")
#    version = Articleversion(editorUserId = editorUser.id,
#        date = datetime.datetime.utcnow(),
#        originalId = originalVersionId,
#        articleId = originalVersion and originalVersion.articleId or None,
#        name = name,
#        text = text,
#        status = 'new')
#    session.add(version)
#    session.commit()
#    return version

#def acceptVersion(moderatorUser: User, versionId: int) -> Article:
#    version: Articleversion = session.query(Articleversion).filter(Articleversion.id == versionId).one_or_none()
#    if (version == None):
#        raise Exception("Version does not exist")
#    if (version.status == 'accepted'):
#        raise Exception("Version is already accepted")
#    if (version.status == 'declined'):
#        raise Exception("Version was declined so cannot be accepted")

#    article: Article = None
#    if (version.articleId == None):
#        authorUser: User = session.query(User).filter(User.id == version.editorUserId).one()
#        article = Article(name = version.name,
#            text = version.text,
#            authorUserId = authorUser.id,
#            versionId = version.id,
#            publishDate = datetime.datetime.utcnow())
#        session.add(article)
#    else:
#        article: Article = session.query(Article).filter(Article.id == version.articleId).one()
#        if (article.versionId != version.originalId):
#            raise Exception("Article was changed while this version was prepared. Please decline with approppriate reason instead")
#        article.name = version.name
#        article.text = version.text,
#        article.versionId = version.id,
#        article.lastModificationDate = datetime.datetime.utcnow()

#    version.moderatedDate = datetime.datetime.utcnow()
#    version.moderatorUserId = moderatorUser.id
#    version.status = 'accepted'
#    version.articleId = article.id

#    session.commit()

#    return article

#def declineVersion(moderatorUser: User, versionId: int, declineReason: str) -> Articleversion:
#    version: Articleversion = session.query(Articleversion).filter(Articleversion.id == versionId).one_or_none()
#    if (version == None):
#        raise Exception("Version does not exist")
#    if (version.status == 'accepted'):
#        raise Exception("Version was accepted so cannot be declined")
#    if (version.status == 'declined'):
#        raise Exception("Version was already declined")

#    version.moderatedDate = datetime.datetime.utcnow()
#    version.moderatorUserId = moderatorUser.id
#    version.status = 'declined'
#    version.declineReason = declineReason 

#    session.commit()
#    return version

#class ArticleShortInfo:
#    id: int
#    name: str
#    authorName: str
#    publishDate: datetime.datetime

#def findArticles(searchText: str) -> List[ArticleShortInfo]:
#    articles: List[ArticleShortInfo] = session.query(\
#            Article.id, Article.name,\
#            (User.firstName + " " + User.lastName).label("authorName"),\
#            Article.publishDate)\
#        .join(Article.user)\
#        .filter(or_(Article.name.like('%' + searchText + '%'), Article.text.like('%' + searchText + '%'), (User.firstName + " " + User.lastName).like('%' + searchText + '%')))\
#        .all()
#    return articles

#class ArticleInfo(ArticleShortInfo):
#    text: str
#    versionId: int
#    lastModificationDate: datetime.datetime 

#def getArticle(id: int) -> ArticleInfo:
#    article: ArticleInfo = session.query(\
#            Article.id, Article.name,\
#            (User.firstName + " " + User.lastName).label("authorName"),\
#            Article.publishDate, Article.text, Article.versionId, Article.lastModificationDate)\
#        .join(Article.user)\
#        .filter(Article.id == id)\
#        .one_or_none()
#    if (article == None):
#        raise Exception("Article does not exist")
#    return article

#class ArticleVersionShortInfo:
#    id: int
#    name: str
#    publishDate: datetime.datetime
#    lastModificationDate: datetime.datetime
#    versionDate: datetime.datetime
#    authorName: str
#    editorName: str
#    moderatorName: str
#    status: ArticleVersionStatus

#def findArticleVersions(status: ArticleVersionStatus, searchText: str) -> List[ArticleVersionShortInfo]:
#    Editor = aliased(User)
#    Moderator = aliased(User)
#    articleVersions: List[ArticleVersionShortInfo] = session.query(\
#            Articleversion.id, Articleversion.name,\
#            Article.publishDate, Article.lastModificationDate,\
#            Articleversion.date.label("versionDate"),
#            (User.firstName + " " + User.lastName).label("authorName"),\
#            (Editor.firstName + " " + Editor.lastName).label("editorName"),\
#            (Moderator.firstName + " " + Moderator.lastName).label("moderatorName"),\
#            Articleversion.status)\
#        .join(Editor, Articleversion.user)\
#        .join(Moderator, Articleversion.user1)\
#        .join(Articleversion.article)\
#        .join(Article.user)\
#        .filter(Articleversion.status == status, Article.name.like('%' + searchText + '%'))\
#        .all()
#    return articleVersions

#class ArticleVersionInfo(ArticleVersionShortInfo):
#    text: str
#    originalId: int
#    originalName: str
#    originalText: str
#    originalDate: datetime.datetime

#def getArticleVersion(id: int) -> ArticleVersionInfo:
#    Editor = aliased(User)
#    Moderator = aliased(User)
#    Original = aliased(Articleversion)
#    articleVersion: ArticleVersionInfo = session.query(\
#            Articleversion.id, Articleversion.name,\
#            Article.publishDate, Article.lastModificationDate,\
#            Articleversion.date.label("versionDate"),
#            (User.firstName + " " + User.lastName).label("authorName"),\
#            (Editor.firstName + " " + Editor.lastName).label("editorName"),\
#            (Moderator.firstName + " " + Moderator.lastName).label("moderatorName"),\
#            Articleversion.text,\
#            Articleversion.status,\
#            Articleversion.originalId,\
#            Original.name.label("originalName"),\
#            Original.text.label("originalText"),\
#            Original.date.label("originalDate"))\
#        .join(Editor, Articleversion.user)\
#        .join(Moderator, Articleversion.user1)\
#        .join(Articleversion.article)\
#        .join(Article.user)\
#        .join(Original, Articleversion.parent)\
#        .filter(Articleversion.id == id)\
#        .one_or_none()

#    #if (article == None):
#     #   raise Exception("Article Version does not exist")

#    return articleVersion

#if (not session.query(session.query(User).filter(User.username == "BettyBoom").exists()).scalar()):
 #   moderatorUser = createUser("Tom2", "Tom", "Jerry", "tom@gmail.com", "ttttom", "+23 0394756182")
  #  setAsModerator(moderatorUser.id)
#if (not session.query(session.query(User).filter(User.username == "BettyBoom").exists()).scalar()):
 #   createUser("BettyBoom", "Betty", "Blossom", "bet.bloss7@gmail.com", "b1l2o3s4s5o6m", "+84 0782538460")
#if (not session.query(session.query(User).filter(User.username == "MickeyMouse").exists()).scalar()):
 #   createUser("MickeyMouse", "Mickey", "Dark", "mickey.dark9097@gmail.com", "MickeY123", "+54 7583752084")

#editorUserToken = loginUser("BettyBoom", "b1l2o3s4s5o6m")
#editorUser = getCurrentUser(editorUserToken)

#moderatorUserToken = loginUser("Tom2", "ttttom")
#moderatorUser = getCurrentUser(moderatorUserToken)

#version = createVersion(editorUser, "New Article", "This article is about ...")
#article = acceptVersion(moderatorUser, version.id)
#editedArticleVersion = createVersion(editorUser, "Updated Article", "This article is not about ...", article.versionId)

#article = acceptVersion(moderatorUser, editedArticleVersion.id)

#otherEditedArticleVersion = createVersion(editorUser, "Updated Article in parralel", "This is quite long change and I'm not sure if my changes will be accepted ...", version.id)
##article = acceptVersion(moderatorUser, otherEditedArticleVersion.id)
#article = declineVersion(moderatorUser, otherEditedArticleVersion.id, "Article was changed since you started your updates. Please merge your updates with the most recent version and resubmit")

#searchText = "Betty Blossom"
#list = findArticles(searchText)
#print("Articles Search Text:", searchText)
#for x in list:
  #  print(x.id, "|", x.name, "|", x.authorName, "|", x.publishDate)

#articleId = list[0].id
#article = getArticle(articleId)
#print("== Article #", articleId, " ==") 
#print("Author: ", article.authorName) 
#print("Name: ", article.name) 
#print("Text: ", article.text) 
#print("Version ID: ", article.versionId) 


#searchText = "Updated Article"
#status: ArticleVersionStatus = 'declined'
#articleVersions = findArticleVersions(status, "Updated Article")
#print("Article Versions Search Text:", searchText, "| Status:", status)
#for x in articleVersions:
 #   print(x.id, "|", x.name, "|", x.status, "|", x.authorName, "|", x.publishDate, "|", x.versionDate, "|", x.editorName, "|", x.moderatorName)

#articleVersionId = articleVersions[len(articleVersions)-1].id
#articleVersion = getArticleVersion(articleVersionId)
#print("== Article Version #", articleVersionId, " ==") 
#print("Editor Name: ", articleVersion.editorName) 
#print("Original ID: ", articleVersion.originalId) 
#print("Original Date: ", articleVersion.originalDate) 
#print("Version ID: ", articleVersion.id) 
#print("Version Date: ", articleVersion.versionDate) 
#print("Version Status: ", articleVersion.status) 
#print("Original Name: ", articleVersion.originalName) 
#print("Updated Name: ", articleVersion.name) 
#print("Original Text: ", articleVersion.originalText) 
#print("Updated  Text: ", articleVersion.text) 
