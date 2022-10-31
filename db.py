from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.engine import reflection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData, Table

db = SQLAlchemy()
engine = create_engine("sqlite:////Users/abuckley/Documents/flask/data/sqllite/propertydb.db")
metadata = MetaData(bind = engine)

# create tables using reflection

def to_dict(obj):
    """
    Function to pull attributes from an SQLAlchemy object, excluding private attributes
    """
    excl = ('_sa_adapter', '_sa_instance_state')
    return {k: v for k, v in vars(obj).items() if not k.startswith('_') and
            not any(hasattr(v, a) for a in excl)}

class Base(db.Model):
    __abstract__ = True

    def __repr__(self):
        params = to_dict(self)
        return f"{params}"

Base = declarative_base(cls = Base)

class sale_history(Base):
    __table__ = Table('sale_history', metadata, autoload=True)

class tax_history(Base):
    __table__ = Table('tax_history', metadata, autoload=True)

class property_data(Base):
    __table__ = Table('property_data', metadata, autoload=True)


    