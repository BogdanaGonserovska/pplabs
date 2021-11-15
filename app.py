from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from model import User, Article, Articleversion, Session
from schema import UserSchema, ArticleSchema, ArticleVersionSchema
from marshmallow import ValidationError
from datetime import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)
session = Session()

@app.route('/api/v1/hello-world-3')
def hello():
    return 'Hello World 3'

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        username = data['username'], 
        firstName = data['firstName'],
        lastName = data['lastName'], 
        email = data['email'], 
        password = bcrypt.generate_password_hash(data['password']).decode('utf-8'),
        phone = data['phone'],
        isActive = True,
        isModerator = False
    )
    
    if not session.query(User).filter(User.username == data['username']).one_or_none() is None:
        return 'This username already exists', '400'

    if not session.query(User).filter(User.email == data['email']).one_or_none() is None:
        return 'This email is taken', '400'

    session.add(new_user)
    session.commit()

    return jsonify ({'message': 'successful operation'})

@app.route('/user/login', methods=['GET'])
def login():
    pass

@app.route('/user/logout', methods=['GET'])
def logout():
    pass

@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    find_user = session.query(User).filter(User.username == username).one_or_none()
    user_schema = UserSchema()
    try:
        user = user_schema.dump(find_user)
    except ValidationError as error:
        return error.messages, 'Invalid username supplied', '400'

    if find_user is None:
        return 'User not found', '404'

    return user

@app.route('/user/<username>', methods=['PUT'])
def edit_user(username):
    find_user = session.query(User).filter(User.username == username).one_or_none()
    
    if find_user is None:
        return 'User not found', '404'

    data = request.json
    if username != data['username']:
        if not session.query(User).filter(User.username == data['username']).one_or_none() is None:
            return 'This username already exists', '400'
    if find_user.email!=data['email']:
        if not session.query(User).filter(User.email == data['email']).one_or_none() is None:
            return 'This email is taken', '400'

    find_user.username = data['username'] if 'username' in data else find_user.username
    find_user.firstName = data['name'] if 'firstName' in data else find_user.firstName
    find_user.lastName = data['surname'] if 'lastName' in data else find_user.lastName
    find_user.email = data['email'] if 'email' in data else find_user.email
    find_user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8') if 'password' in data else find_user.password
    find_user.phone = data['phone'] if 'phone' in data else find_user.phone

    session.commit()
    return UserSchema().dump(find_user)

@app.route('/user/<username>', methods=['DELETE'])
def delete_user(username):
    find_user = session.query(User).filter(User.username == username).one_or_none()

    try:
        UserSchema().dump(find_user)
    except ValidationError as error:
        return error.messages, 'Invalid user supplied', '400'

    if find_user is None:
        return 'User not found', '404'
    find_article = session.query(Article).filter(Article.authorUserId == find_user.id).all()
    session.query(Articleversion).filter(Articleversion.editorUserId == find_user.id).update({Articleversion.articleId: None})
    find_version = session.query(Articleversion).filter(Articleversion.editorUserId == find_user.id).all()
    if find_article:
        for i in find_article:
            session.delete(i)
    if find_version:
        for i in find_version:
            session.delete(i)
    session.delete(find_user)
    session.commit()
    return 'successfull operation', '200'

@app.route('/article', methods=['POST'])
def create_article():
    data = request.json
    new_article = Article(
        name = data['name'], 
        authorUserId = data['editorUserId'],
        text = data['text'],
        versionId = 1,
        publishDate = datetime.now(),
        lastModificationDate = datetime.now()
    )
#curl -X POST http://127.0.0.1:5000/article -H "Content-Type: application/json" --data "{\"name\": \"article1\", \"authorUserId\": \"1\", \"text\": \"sometext\", \"versionId\": \"1\"}"
        
    session.add(new_article)
    session.commit()

    return jsonify({'message': 'successful operation'})

@app.route('/article', methods=['GET'])
def articles():

    article_list = session.query(Article)
    if article_list:
        return jsonify(ArticleSchema(many=True).dump(article_list)), '200'
    else:
        return 'Articles not found', '404'

@app.route('/article/<ArticleId>', methods=['GET'])
def get_article(ArticleId):
    find_article = session.query(Article).filter(Article.id == ArticleId).one_or_none()

    try:
        article = ArticleSchema().dump(find_article)
    except ValidationError as error:
        return error.messages, 'Invalid article supplied', '400'

    if find_article is None:
        return 'article not found', '404'

    return article, 'successfull operation'
    
@app.route('/article/<ArticleId>', methods=['DELETE'])
def delete_article(ArticleId):
    find_article = session.query(Article).filter(Article.id == ArticleId).one_or_none()

    try:
        article = ArticleSchema().dump(find_article)
    except ValidationError as error:
        return error.messages, 'Invalid Article supplied', '400'

    if find_article is None:
        return 'Article not found', '404'

    session.query(Articleversion).filter(Articleversion.articleId == ArticleId).update({Articleversion.articleId: None})
    session.delete(find_article)
    session.commit()

    return 'successfull operation', '200'


@app.route('/versions', methods=['POST'])
def create_version():
    data = request.json
    new_version = Articleversion(
        editorUserId = data['editorUserId'],
        articleId = data['articleId'], #to create new article put here 0
        name = data['name'],
        text = data['text'],
        date = datetime.now(),
        status = 'new',
        originalId = None,
        moderatorUserId = None,
        moderatedDate = None,
        declineReason = None
    )

#curl -X POST http://127.0.0.1:5000/versions -H "Content-Type: application/json" --data "{\"editorUserId\": \"1\", \"articleId\": \"0\",  \"name\": \"First version\", \"text\": \"First text\"}"
    
    find_user = session.query(User).filter(User.id == int(data['editorUserId'])).one_or_none()
    if find_user is None:
        return 'User not found', '404'

    if data['articleId'] != '0':
        find_article = session.query(Article).filter(Article.id == int(data['articleId'])).one_or_none()

        if find_article is None:
            return 'Article not found', '404'   
        session.add(new_version)
        
    else:
        new_version.articleId = None
        session.add(new_version)
    
    session.commit()
    return 'succesfully added', '200'

@app.route('/versions', methods=['GET'])
def get_versions():
    if session.query(Articleversion):
        return jsonify(ArticleVersionSchema(many=True).dump(session.query(Articleversion).filter(Articleversion.status == 'new'))), '200'
    else:
        return 'Versions not found', '404'

@app.route('/versions/<ChangeId>', methods=['GET'])
def get_version(ChangeId):
    find_version = session.query(Articleversion).filter(Articleversion.id == ChangeId).one_or_none()

    try:
        article_version = ArticleVersionSchema().dump(find_version)
    except ValidationError as error:
        return error.messages, 'Invalid article supplied', '400'

    if find_version is None:
        return 'article not found', '404'

    return article_version

@app.route('/versions/<ChangeId>', methods=['PUT'])
def accept_version(ChangeId):
    find_version = session.query(Articleversion).filter(Articleversion.id == ChangeId).one_or_none()

    if find_version is None:
        return 'Version not found'

    find_article = session.query(Article).filter(Article.id == find_version.articleId).one_or_none()
    if find_article is None:
        new_article = Article(
            name = find_version.name, 
            authorUserId = find_version.editorUserId,
            text = find_version.text,
            versionId = find_version.id,
            publishDate = datetime.now(),
            lastModificationDate = datetime.now()
        )
        session.add(new_article)
        session.commit()
        find_version.articleId = new_article.id
        find_article = session.query(Article).filter(Article.id == find_version.articleId).one_or_none()
    else:
        find_article.name = find_version.name
        find_article.text = find_version.text
        find_article.lastModificationDate = datetime.now()
        
    find_version.status = 'accepted'
    find_version.moderatedDate = datetime.now()

#curl -X PUT http://127.0.0.1:5000/versions/18

    session.commit()

    return ArticleSchema().dump(find_article), '200'

@app.route('/versions/<ChangeId>', methods=['DELETE'])
def decline_version(ChangeId):
    find_version = session.query(Articleversion).filter(Articleversion.id == ChangeId).one_or_none()

    try:
        ArticleVersionSchema().dump(find_version)
    except ValidationError as error:
        return error.messages, 'Invalid Article supplied', '400'

    if find_version is None:
        return 'Version not found', '404'

    find_version.status = 'declined'

    #session.delete(find_version)
    session.commit()
    return 'successful operation'


#create_user
#curl -X POST http://127.0.0.1:5000/user -H "Content-Type: application/json" --data "{\"username\": \"user1\", \"firstName\": \"Bohdana\", \"lastName\": \"Honserovska\", \"email\": \"someemail@gmail.com\", \"password\": \"1111\", \"phone\": \"0992341122\"}"
#curl -X POST http://127.0.0.1:5000/user -H "Content-Type: application/json" --data "{\"username\": \"user_to_delete\", \"firstName\": \"Bohdana\", \"lastName\": \"Honserovska\", \"email\": \"newemail@gmail.com\", \"password\": \"1111\", \"phone\": \"0992341122\"}"

#get_user
#curl -X GET http://127.0.0.1:5000/user/user1

#edit_user
#curl -X PUT http://127.0.0.1:5000/user/user1 -H "Content-Type: application/json" --data "{\"username\": \"new_user\",\"email\": \"newemail@gmail.com\", \"password\": \"1234\"}"

#delete_user
#curl -X DELETE http://127.0.0.1:5000/user/user_to_delete

#create_version
#curl -X POST http://127.0.0.1:5000/versions -H "Content-Type: application/json" --data "{\"editorUserId\": \"1\", \"articleId\": \"0\",  \"name\": \"First version\", \"text\": \"First text\"}"
#curl -X POST http://127.0.0.1:5000/versions -H "Content-Type: application/json" --data "{\"editorUserId\": \"1\", \"articleId\": \"5\",  \"name\": \"Edited version\", \"text\": \"Edited text\"}"

#get_version
#curl -X GET http://127.0.0.1:5000/versions/29

#accept_version
#curl -X PUT http://127.0.0.1:5000/versions/29

#decline_version
#curl -X DELETE http://127.0.0.1:5000/versions/29

#get_article
#curl -X GET http://127.0.0.1:5000/article/5

#delete_article
#curl -X DELETE http://127.0.0.1:5000/article/5