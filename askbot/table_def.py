from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///ask.db', echo=False)
Base = declarative_base()


class Question(Base):

    __tablename__ = "question"

    id = Column(Integer, primary_key=True)
    question = Column(String(140))
    answer = Column(String(140))

    def __init__(self, question):
        self.question = question


def init_db():
    Base.metadata.create_all(engine)
