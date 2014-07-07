import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from table_def import *


class AskDB():

    engine = None

    def __init__(self):
        if not os.path.isfile('ask.db'):
            init_db()
        self.engine = create_engine('sqlite:///ask.db', echo=False)

    def store_question(self, question):
        """
        Store question
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        t = Question(question)
        session.add(t)
        session.commit()
        res = session.query(Question).filter_by(question=question).all()
        return res[0].id

    def store_answer(self, id, answer):
        """
        Query base on rainbow id
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        ary = session.query(Question).filter_by(id=id).all()
        for q in ary:
            q.answer = answer
        session.commit()

    def query_question(self, id):
        """
        Query question base on rainbow id
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        ary = session.query(Question).filter_by(id=id).all()
        return ary[0].question

