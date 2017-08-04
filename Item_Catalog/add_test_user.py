from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Item

engine = create_engine('sqlite:///user_item_catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()
test_user = User(username='test_user', password='nopass', id="TEST")
tu_in_database = session.query(User).filter_by(id=test_user.id)
if tu_in_database is not None and tu_in_database.one().id != test_user.id:
    session.add(test_user)
    session.commit()

    snowboard_item = Item(name='snowboard', category='outdoor',
                          description='Cannot wait for next season!',
                          user=test_user)
    session.add(snowboard_item)
    session.commit()

    frying_pan_item = Item(name='frying pan', category='kitchen',
                           description='My daily cooking tool', user=test_user)
    session.add(frying_pan_item)
    session.commit()

    print('Added test_user, and a snowboard and frying pan to their catalog!')
else:
    print('test_user already in database')
