from marshmallow import Schema, fields, validate, post_load
from model import *

class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    firstName = fields.Str()
    lastName = fields.Str()
    email = fields.Email(validate=validate.Email())
    password = fields.Str()
    phone = fields.Str()
    isModerator = fields.Bool()
    isActive = fields.Bool()

    #@post_load
    #def create_user(self, data, **kwargs):
    #    return User(**data)

class ArticleSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    authorUserId = fields.Int()
    text = fields.Str()
    versionId = fields.Int()
    publishDate = fields.DateTime()
    lastModificationDate = fields.DateTime()

    #@post_load
    #def create_article(self, data, **kwargs):
    #    return Article(**data)

class ArticleVersionSchema(Schema):
    id = fields.Int()
    editorUserId = fields.Int()
    date = fields.DateTime()
    originalId = fields.Int(required=False)
    articleId = fields.Int(required=False)
    name = fields.Str()
    text = fields.Str()
    status = fields.Str(validate=validate.OneOf(['new', 'accepted', 'declined']))
    moderatorUserId = fields.Int(required=False)
    moderatedDate = fields.DateTime(required=False)
    declineReason = fields.Str()

    #@post_load
    #def create_articleversion(self, data, **kwargs):
    #    return Articleversion(**data)

