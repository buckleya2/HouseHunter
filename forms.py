from flask_wtf import FlaskForm
from sqlalchemy import create_engine
from wtforms import BooleanField, DateField, FloatField, IntegerField, IntegerRangeField, PasswordField, StringField
from wtforms.validators import InputRequired, NumberRange, Optional, Regexp, Length, ValidationError

from config import *
from db import *
from helpers import *

def validate_one(field):
    """
    """
    if field.data == '' or field.data is None:
        raise ValsationError("TEST")

def validate_many(self, field):
    """
    """
    a = self.field1.data
    b = self.field2.data

    if a > b:
        raise ValidationError("TEST2")

class AddressForm(FlaskForm):
    address = StringField(id = 'address', label = 'address')
    parcel = StringField(id = 'parcel', label = 'parcel')

class SearchForm(FlaskForm):
    estimated_price = IntegerRangeField(id = 'estimated_price', label = 'estimated_price',
                                   validators = [Optional(), NumberRange(0, 8000000)])
    number_bed = IntegerField(id = 'number_bed', label = 'number_bed',
                        validators = [Optional(), NumberRange(0, 10)])
    number_bath = IntegerField(id = 'number_bath', label = 'number_bath',
                        validators = [Optional(), NumberRange(0, 10)])
    sqft = IntegerField(id = 'sqft', label = 'sqft',
                        validators = [Optional(), NumberRange(0, 20000)])
    lot_size = FloatField(id = 'lot_size', label = 'lot_size',
                        validators = [Optional(), NumberRange(0, 100)])


