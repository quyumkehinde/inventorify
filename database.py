from sqlalchemy import select, delete, create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Product
from sqlalchemy.exc import IntegrityError
from exceptions import AlreadyExistError


class Database():
    def __init__(self, path="sqlite:///database.db", logging=True):
        self.engine = create_engine(path, echo=logging)
        Session = sessionmaker(self.engine)
        self.session = Session()

    def save(self):
        self.session.commit()

    def migrate(self):
        Base.metadata.create_all(self.engine)

    def add_user(self, business_name, email, password):
        try:
            self.session.add(
                User(business_name=business_name, email=email, password=password))
            self.save()
        except IntegrityError:
            raise AlreadyExistError('User already exist.')

    def add_category(self, name, user_id):
        try:
            self.session.add(Category(name=name, user_id=user_id))
            self.save()
        except IntegrityError:
            raise AlreadyExistError('Category already exist.')

    def add_product(self, name, user_id, category_id):
        try:
            self.session.add(
                Product(name=name, user_id=user_id, category_id=category_id))
            self.save()
        except IntegrityError:
            raise AlreadyExistError('Product already exist.')
