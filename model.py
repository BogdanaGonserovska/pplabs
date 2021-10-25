import sqlalchemy

from sqlalchemy.ext.declarative import declarative_base
BaseModel = declarative_base()

from sqlalchemy import Column, String, Integer, Boolean
class User(BaseModel):
    __tablename__ = "user"
    id = Column(Integer,  primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    firstName = Column(String(50), nullable=False)
    lastName = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    phone = Column(String(15))
    isModerator = Column(Boolean, nullable=False)
    isActive = Column(Boolean, nullable=False)

#if __name__ == "__main__":
#    BaseModel.metadata.create_all(engine)
