import sqlalchemy
from sqlalchemy import create_engine
engine = create_engine("mysql+pymysql://root:Ira.ko03@127.0.0.1:3306/article_service", encoding="utf-8", echo=True, future=True)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

from model import User

user = session.query(User).filter(User.username=="Tom2").one_or_none()

if (user == None):
    user = User(
        username = "Tom2",
        firstName = "Tom",
        lastName ="Jerry",
        email = "tom@gmail.com",
        password = "ttttom",
        phone = "+23 0394756182",
        isModerator = True,
        isActive = False)
    session.add(user)
    session.commit()

user.lastName = "Smith"
session.commit()

slovo ="ith"
from sqlalchemy import or_
list = session.query(User).filter(or_(User.username.like('%'+slovo+'%'),User.lastName.like('%'+slovo+'%'))).all()
for y in list:
    print(y.lastName, y.password)