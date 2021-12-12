from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from model import db, User, Article, Articleversion
from schema import UserSchema, ArticleSchema, ArticleVersionSchema
from sqlalchemy import or_
from flask_sqlalchemy import SQLAlchemy
import os

from marshmallow import ValidationError
from datetime import datetime
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)

environment = os.environ.get("ENVIRONMENT")
if (environment is None):
    environment = "development"
app.config.from_json("config." + environment + '.json');

db.init_app(app)

bcrypt = Bcrypt(app)
auth = HTTPBasicAuth()

if __name__ == "__main__":
    app.run(debug=False)

@auth.verify_password
def verify_password(username, password):
    found_user = db.session.query(User).filter(User.username==username).one_or_none()
    if found_user is not None and bcrypt.check_password_hash(found_user.password, password):
        return found_user

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
        isModerator = data['isModerator']
    )
    
    if not db.session.query(User).filter(User.username == data['username']).one_or_none() is None:
        return jsonify ({'message': 'This username already exists'}), 400

    if not db.session.query(User).filter(User.email == data['email']).one_or_none() is None:
        return jsonify ({'message': 'This email is taken'}), 400

    db.session.add(new_user)
    db.session.commit()

    return jsonify ({'id': new_user.id}), 200

@app.route('/user/<username>', methods=['GET'])
@auth.login_required
def get_user(username):
    find_user = db.session.query(User).filter(User.username == username).one_or_none()

    if find_user is None:
        return jsonify ({'message': 'User not found'}), 404

    if find_user.username != auth.current_user().username:
        return jsonify ({'message': 'You don\'t have required permission'}), 401

    user = UserSchema().dump(find_user)
    return user, 200

@app.route('/user/<username>', methods=['PUT'])
@auth.login_required
def edit_user(username):
    find_user = db.session.query(User).filter(User.username == username).one_or_none()
    
    if find_user is None:
        return jsonify ({'message':'User not found'}), 404

    if find_user.username != auth.current_user().username:
        return jsonify ({'message':'You can\'t update this user'}), 401

    data = request.json
    if username != data['username']:
        if not db.session.query(User).filter(User.username == data['username']).one_or_none() is None:
            return jsonify ({'message':'This username already exists'}), 400

    if find_user.email!=data['email']:
        if not db.session.query(User).filter(User.email == data['email']).one_or_none() is None:
            return jsonify ({'message':'This email is taken'}), 400

    find_user.username = data['username'] if 'username' in data else find_user.username
    find_user.firstName = data['firstName'] if 'firstName' in data else find_user.firstName
    find_user.lastName = data['lastName'] if 'lastName' in data else find_user.lastName
    find_user.email = data['email'] if 'email' in data else find_user.email
    find_user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8') if 'password' in data else find_user.password
    find_user.phone = data['phone'] if 'phone' in data else find_user.phone

    db.session.commit()
    return UserSchema().dump(find_user)

@app.route('/user/<username>', methods=['DELETE'])
@auth.login_required
def delete_user(username):
    find_user = db.session.query(User).filter(User.username == username).one_or_none()
    if find_user is None:
        return jsonify ({'message':'User not found'}), 404

    if not auth.current_user().isModerator:
        return jsonify ({'message':'You don\'t have permission to delete users'}), 401

    find_version = db.session.query(Articleversion).filter(or_(Articleversion.editorUserId == find_user.id, Articleversion.moderatorUserId == find_user.id)).first()
    if find_version is not None:
        return jsonify ({'message':'The user cannot be deleted because it\'s referenced in articles history'}), 400

    db.session.delete(find_user)
    db.session.commit()

    return jsonify ({'message':'successfull operation'}), 200

@app.route('/article', methods=['POST'])
@auth.login_required
def create_article():
    data = request.json
    new_article = Article(
        name = data['name'], 
        authorUserId = data['authorUserId'],
        text = data['text'],
        versionId = 1,
        publishDate = datetime.now(),
        lastModificationDate = datetime.now()
    )
# curl -X POST http://127.0.0.1:5000/article -H "Content-Type: application/json" --data "{\"name\": \"article1\", \"authorUserId\": \"1\", \"text\": \"sometext\", \"versionId\": \"1\"}"
        
    db.session.add(new_article)
    db.session.commit()

    return jsonify({'message': 'successful operation'}), 200

@app.route('/article', methods=['GET'])
def articles():
    article_list = db.session.query(Article)
    if article_list:
        return jsonify(ArticleSchema(many=True).dump(article_list)), 200
    else:
        return jsonify ({'message':'Articles not found'}), 404

@app.route('/article/<ArticleId>', methods=['GET'])
def get_article(ArticleId):
    find_article = db.session.query(Article).filter(Article.id == ArticleId).one_or_none()

    try:
        article = ArticleSchema().dump(find_article)
    except ValidationError as error:
        return error.messages, jsonify ({'message':'Invalid article supplied'}), 400

    if find_article is None:
        return jsonify ({'message':'article not found'}), 404

    return article, jsonify ({'message':'successfull operation'}), 200
    
@app.route('/article/<ArticleId>', methods=['DELETE'])
@auth.login_required
def delete_article(ArticleId):
    find_article = db.session.query(Article).filter(Article.id == ArticleId).one_or_none()

    try:
        article = ArticleSchema().dump(find_article)
    except ValidationError as error:
        return error.messages, jsonify ({'message':'Invalid Article supplied'}), 400

    if find_article is None:
        return jsonify ({'message':'Article not found'}), 404

    if not auth.current_user().isModerator:
            # and find_article.authorUserId != auth.current_user():
        return jsonify ({'message':'You don\'t have permission to delete article'}), 401

    db.session.query(Articleversion).filter(Articleversion.articleId == ArticleId).update({Articleversion.articleId: None})
    db.session.delete(find_article)
    db.session.commit()

    return jsonify ({'message':'successfull operation'}), 200


@app.route('/versions', methods=['POST'])
@auth.login_required
def create_version():
    data = request.json

    originalId = data['originalId'] if 'originalId' in data else None
    articleId = None
    if originalId is not None:
        find_version = db.session.query(Articleversion).filter(Articleversion.id == int(data['originalId'])).one_or_none()
        if find_version is None:
            return jsonify ({'message':'Original version is not found'}), 404
        articleId = find_version.articleId

    new_version = Articleversion(
        editorUserId = auth.current_user().id,
        originalId = originalId,
        articleId = articleId,
        name = data['name'],
        text = data['text'],
        date = datetime.now(),
        status = 'new')

    db.session.add(new_version)
    db.session.commit()

#curl -X POST http://127.0.0.1:5000/versions -H "Content-Type: application/json" --data "{\"editorUserId\": \"1\", \"articleId\": \"0\",  \"name\": \"First version\", \"text\": \"First text\"}"
    
    return jsonify ({'id':new_version.id}), 200

@app.route('/versions', methods=['GET'])
@auth.login_required
def get_versions():
    if not auth.current_user().isModerator:
        return jsonify ({'message':'You don\'t have permission to get versions'}), 401
    versions = db.session.query(Articleversion).filter(Articleversion.status == 'new').all()
    if len(versions) > 0:
        return jsonify(ArticleVersionSchema(many=True).dump(versions)), 200
    else:
        return jsonify ({'message':'New versions not found'}), 404

@app.route('/versions/<ChangeId>', methods=['GET'])
@auth.login_required
def get_version(ChangeId):
    if not auth.current_user().isModerator:
        return jsonify ({'message':'You don\'t have permission to view this version'}), 401

    find_version = db.session.query(Articleversion).filter(Articleversion.id == ChangeId).one_or_none()
    if find_version is None:
        return jsonify ({'message':'Version not found'}), 404

    return ArticleVersionSchema().dump(find_version), 200

@app.route('/versions/<ChangeId>', methods=['PUT'])
@auth.login_required
def accept_version(ChangeId):
    if not auth.current_user().isModerator:
        return jsonify ({'message':'You don\'t have permission to moderate articles'}), 401

    find_version = db.session.query(Articleversion).filter(Articleversion.id == ChangeId).one_or_none()
    if find_version is None:
        return jsonify ({'message':'Version not found'}), 404

    if find_version.status != 'new':
        return jsonify ({'message':'Version is already moderated'}), 400

    find_article = None
    if find_version.articleId is None:
        new_article = Article(
            authorUserId = find_version.editorUserId,
            name = find_version.name, 
            text = find_version.text,
            versionId = find_version.id,
            publishDate = datetime.now(),
            lastModificationDate = datetime.now()
        )
        db.session.add(new_article)
        db.session.commit()
        find_version.articleId = new_article.id
        find_article = new_article
    else:
        find_article = db.session.query(Article).filter(Article.id == find_version.articleId).one()
        if find_article.versionId != find_version.originalId:
            return jsonify ({'message':'Article was changed by another user in parallel'}), 400
            
        find_article.name = find_version.name
        find_article.text = find_version.text
        find_article.versionId = find_version.id
        find_article.lastModificationDate = datetime.now()
        
    find_version.status = 'accepted'
    find_version.moderatedDate = datetime.now()
    find_version.moderatorUserId = auth.current_user().id


#curl -X PUT http://127.0.0.1:5000/versions/18

    db.session.commit()

    return ArticleSchema().dump(find_article), 200

@app.route('/versions/<ChangeId>', methods=['DELETE'])
@auth.login_required
def decline_version(ChangeId):
    if not auth.current_user().isModerator:
        return jsonify ({'message':'You don\'t have permission to moderate articles'}), 401

    find_version = db.session.query(Articleversion).filter(Articleversion.id == ChangeId).one_or_none()
    if find_version is None:
        return jsonify ({'message':'Version not found'}), 404

    if find_version.status != 'new':
        return jsonify ({'message':'Version is already moderated'}), 400

    declineReason = request.json["declineReason"] if "declineReason" in request.json else None  
    find_version.status = 'declined'
    find_version.moderatedDate = datetime.now()
    find_version.moderatorUserId = auth.current_user().id
    find_version.declineReason = declineReason

    db.session.commit()

    return jsonify ({'message':'successful operation'}), 200


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
# curl -X POST http://127.0.0.1:5000/versions -H "Content-Type: application/json" --data "{\"editorUserId\": \"1\", \"articleId\": \"0\",  \"name\": \"First version\", \"text\": \"First text\"}"
# curl -X POST http://127.0.0.1:5000/versions -H "Content-Type: application/json" --data "{\"editorUserId\": \"1\", \"articleId\": \"5\",  \"name\": \"Edited version\", \"text\": \"Edited text\"}"

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