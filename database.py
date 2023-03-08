from sqlalchemy import select, delete, create_engine
from sqlalchemy.orm import sessionmaker
from models import Base


class Database():
    def __init__(self, path="sqlite:///database.db", logging=True):
        self.engine = create_engine(path, echo=logging)
        Session = sessionmaker(self.engine)
        self.session = Session()

    def save(self):
        self.session.commit()

    def migrate(self):
        Base.metadata.create_all(self.engine)
