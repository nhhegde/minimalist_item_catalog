from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, User
import add_test_user

engine = create_engine('postgresql://postgres:postgresql@localhost:5432/user_item_catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def serialize_sqlalchemy_object(o):
    return {key: value for key, value in o.__dict__.items()
            if not key.startswith('_')
            }

users = session.query(User).all()  # test_user has an id of 1
print("Database Session: {}".format(repr(session)))
print("Convert sqlalchemy object to python dictionary with: {}".format(
        repr(serialize_sqlalchemy_object)))

print("Tables: [{}, {}]".format(repr(User), repr(Item)))
print('users: {}'.format(users))

test_user = session.query(User).filter_by(username='test_user').one()

print('test_user.username: "{}" test_user.id: "{}"'.format(
    test_user.username, test_user.id))
