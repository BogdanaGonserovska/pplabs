import sqlalchemy
from sqlalchemy import create_engine
engine = create_engine("mysql+pymysql://root:Ira.ko03@127.0.0.1:3306/article_service", encoding="utf-8", echo=True, future=True)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

from sqlalchemy.ext.declarative import declarative_base
BaseModel = declarative_base()

from sqlalchemy import Column, String, Integer, Boolean
class User(BaseModel):
    __tablename__ = "user5"
    id = Column(Integer,  primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    firstName = Column(String(50), nullable=False)
    lastName = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    phone = Column(String(15))
    isModerator = Column(Boolean, nullable=False)
    isActive = Column(Boolean, nullable=False)

if __name__ == "__main__":
    BaseModel.metadata.create_all(engine)


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

user_from_db = session.query(User).filter(User.id==user.id).one_or_none()
user_from_db.lastName = "Smith"
session.commit()

slovo ="ith"
from sqlalchemy import or_
list = session.query(User).filter(or_(User.username.like('%'+slovo+'%'),User.lastName.like('%'+slovo+'%'))).all()
for y in list:
    print(y.password)