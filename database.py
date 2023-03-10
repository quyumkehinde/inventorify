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
        user = User(
            business_name=business_name,
            email=email,
            password=password
        )
        try:
            self.session.add(user)
            self.save()
            return user
        except IntegrityError:
            self.session.rollback()
            raise AlreadyExistError('User already exist.')

    def fetch_user(self, email):
        return (
            self.session.query(User)
                .filter(User.email == email)
                .first()
        )

    def add_category(self, name, user_id):
        category = Category(name=name, user_id=user_id)
        try:
            self.session.add(category)
            self.save()
        except IntegrityError:
            self.session.rollback()
            raise AlreadyExistError('Category already exist.')
        return category

    def update_category(self, category_id, name, user_id):
        try:
            (self.session.query(Category)
                .filter(Category.id == category_id)
                .filter(Category.user_id == user_id)
                .update({Category.name: name}))
            self.save()
        except IntegrityError:
            self.session.rollback()
            raise AlreadyExistError('Category already exist.')

    def fetch_category(self, user_id, category_id):
        return (
            self.session.query(Category)
                .filter(Category.id == category_id)
                .filter(Category.user_id == user_id)
                .first()
        )

    def fetch_categories(self, user_id):
        return (
            self.session.query(Category)
                .filter(Category.user_id == user_id)
                .all()
        )

    def delete_category(self, category_id, user_id):
        return (
            self.session.query(Category)
                .filter(Category.id == category_id)
                .filter(Category.user_id == user_id)
                .delete()
        )

    def add_product(self, name, price, quantity, category_id, user_id):
        product = Product(
            name=name,
            price=price,
            quantity=quantity,
            category_id=category_id,
            user_id=user_id
        )
        try:
            self.session.add(product)
            self.save()
        except IntegrityError:
            self.session.rollback()
            raise AlreadyExistError('Product already exist.')
        return product

    def update_product(self, product_id, name, price, quantity, category_id, user_id):
        try:
            (self.session.query(Product)
                .filter(Product.id == product_id)
                .filter(Product.user_id == user_id)
                .update({
                    Product.name: name,
                    Product.price: price,
                    Product.quantity: quantity,
                    Product.category_id: category_id,
                }))
            self.save()
        except IntegrityError:
            self.session.rollback()
            raise AlreadyExistError('Category already exist.')

    def fetch_product(self, user_id, product_id):
        return (
            self.session.query(Product)
                .filter(Product.user_id == user_id)
                .filter(Product.id == product_id)
                .first()
        )

    def fetch_products(self, user_id):
        return (
            self.session.query(Product)
                .filter(Product.user_id == user_id)
                .all()
        )

    def delete_product(self, product_id, user_id):
        return (
            self.session.query(Product)
                .filter(Product.id == product_id)
                .filter(Product.user_id == user_id)
                .delete()
        )

    def fetch_products_and_categories_count(self, user_id):
        total_products = (
            self.session.query(Product)
                .filter(Product.user_id == user_id)
                .count()
        )
        products_out_of_stock = (
            self.session.query(Product)
                .filter(Product.user_id == user_id)
                .filter(Product.quantity == 0)
                .count()
        )
        total_categories = (
            self.session.query(Category)
                .filter(Category.user_id == user_id)
                .count()
        )
        empty_categories = (
            self.session.query(Category)
                .where(~Category.products.any())
                .count()
        )

        return ((total_products, products_out_of_stock), (total_categories, empty_categories))
