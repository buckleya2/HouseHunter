from flask_wtf import FlaskForm
from sqlalchemy import create_engine
from wtforms import FloatField, IntegerField, PasswordField, SelectField, StringField
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
    min_taxable_value = IntegerField(label = 'min_taxable_value', validators = [Optional(), NumberRange(0, 8000000)])
    min_bedrooms = IntegerField(label = 'min_bedrooms', validators = [Optional(), NumberRange(0, 10)])
    min_bathrooms = IntegerField(label = 'min_bathrooms', validators = [Optional(), NumberRange(0, 10)])
    min_square_feet = IntegerField(label = 'min_square_feet', validators = [Optional(), NumberRange(0, 20000)])
    min_land_acres = FloatField(label = 'min_land_acres', validators = [Optional(), NumberRange(0, 100)])
    min_stories = SelectField(label = 'min_stories', choices = ['', '1', '2', '3'])
    min_year_built = IntegerField(label = 'min_year_built', validators = [Optional(), NumberRange(0, 3000)])
    min_last_sold_year = IntegerField(label = 'min_last_sold_year', validators = [Optional(), NumberRange(0, 3000)])
    max_taxable_value = IntegerField(label = 'max_taxable_value', validators = [Optional(), NumberRange(0, 8000000)])
    max_bedrooms = IntegerField(label = 'max_bedrooms', validators = [Optional(), NumberRange(0, 10)])
    max_bathrooms = IntegerField(label = 'max_bathrooms', validators = [Optional(), NumberRange(0, 10)])
    max_square_feet = IntegerField(label = 'max_square_feet', validators = [Optional(), NumberRange(0, 20000)])
    max_land_acres = FloatField(label = 'max_land_acres', validators = [Optional(), NumberRange(0, 100)])
    max_stories = SelectField(label = 'max_stories', choices = ['', '1', '2', '3'])
    max_year_built = IntegerField(label = 'max_year_built', validators = [Optional(), NumberRange(0, 3000)])
    max_last_sold_year = IntegerField(label = 'max_last_sold_year', validators = [Optional(), NumberRange(0, 3000)])
