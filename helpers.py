import datetime
import json
import geopandas as gpd
import pandas as pd
import numpy as np
import plotly
import plotly_express as px
import plotly.graph_objects as go

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from typing import Tuple
from werkzeug.security import generate_password_hash, check_password_hash

from config import *
from db import *

engine = create_engine("sqlite:////Users/abuckley/Documents/flask/data/sqllite/testdb.db")


def tax_stats(parcel_number: str) -> Tuple[str, str]:
    """
    Function to gather data about the parcel's tax history

    @param parcel_number: parcel ID
    @returns: tuple of: how much tax is due (if any) and a JSON formatted plotly chart
              of historical tax values
    """    
    tax = filter_table(tax_history, {'parcel_number': parcel_number})
    # make plot of tax values over time
    fig = px.line(tax, x = 'tax_year', y = 'tax_value', title = 'Tax Value History',
        labels={'tax_year': 'Tax Year',
                'tax_value': 'Assessed Value ($)'}, text = 'tax_value')
    fig.update_traces(textposition = 'top left', line_color = '#C23F54')
    fig.update_layout(plot_bgcolor="white")
    graphJSON = json.dumps(fig, cls = plotly.utils.PlotlyJSONEncoder)
    # find out if tax is due and how much
    amount_due = filter_table(property_data, {'parcel_number': parcel_number}).total_due.item()
    return (graphJSON, amount_due)

def sales_stats(parcel_number: str) -> dict:
    """
    Function to gather data about the parcel's most recent sale

    @param parcel_number: parcel ID
    @returns: dict of attribute: parcel value for sales stats
    """
    sales = filter_table(sale_history, {'parcel_number': parcel_number})
    # get only most recent sale
    sales = sales[sales.sale_number	 == '1']
    if len(sales.sale_date) == 0:
        return {'last sold' : 'no record of sales'}
    years_since_sold = round((datetime.datetime.now() - pd.to_datetime(sales.sale_date.item())).days/365, 2)
    # create dict of sale metrics
    sale_dict = {'years since sold': years_since_sold,
                'previous owner': sales.grantor.item(),
                'current owner': sales.grantee.item(),
                'last sold price': sales.sale_price.item(),
                'sale date': sales.sale_date.item()}
    return sale_dict

def neighborhood_stats(parceldf: pd.DataFrame, parcel_number: str) -> dict:
    """
    Function that calculates Z-scores for parcek of interest relative to the other
    parcels in the neighborhood. Attributes used to calculate Z-scores are defined in
    config.py

    @param parceldf: pd.DataFrame with attribute data for parcels of interest
    @param parcel_number: parcel ID
    @returns: dict of attribute: (parcel value, z-score) for every attribute in NEIGHBORHOOD_ATTRIBUTES
    """
    Z = {}
    for col in NEIGHBORHOOD_ATTRIBUTES:
        parcel_value = float(parceldf.loc[parceldf.parcel_number == parcel_number, col])
        score = (parcel_value- np.mean(parceldf[col]))/ np.std(parceldf[col])
        name = str(col).replace('square_feet', 'sqft').replace('_', ' ')
        Z[name] = (parcel_value, round(float(score), 2))
    return Z

def find_neighborhood(parcel_number: str) -> Tuple[gpd.GeoDataFrame, pd.DataFrame]:
    """
    Function to find all parcels in a neighborhood for a given parcel number

    @param parcel_number: parcel ID
    @returns: gpd.GeoDataFrame and pd.DataFrame of parcel coordinates and attribute data
              for all parcels in neighborhood
    """
    gdf = gpd.read_file(MAP_JSON)
    # query DB for parcel information
    neighborhood = filter_table(property_data, {'parcel_number': parcel_number}).neighborhood[0]
    neighborhood_parcels = filter_table(property_data, {'neighborhood': neighborhood})
    # filter for parcel of interest
    filtered_geojson = gdf[gdf.parcel_number.isin(neighborhood_parcels.parcel_number)]
    return (filtered_geojson, neighborhood_parcels)

def plot_map(geojson: gpd.GeoDataFrame, parceldf: pd.DataFrame, highlight_parcel: str = None) -> json:
    """
    Function to create a plotly choropleth plot in json format

    @param geojson: GeoDataFrame with coordinate information for parcels of interest
    @param parceldf: pd.DataFrame with attribute data for parcels of interest
    @param highlight_parcel: optional, name of parcel to highlight with a point
    @returns: json of plotly-express plot
    """
    # if highlighting a parcel, center on that parcel, else center on Gig Harbor
    if highlight_parcel:
        parcel_markers = geojson[geojson.parcel_number == highlight_parcel]
        COORDS = (float(parcel_markers.Latitude), float(parcel_markers.Longitude))
    # make base plot
    fig = px.choropleth_mapbox(parceldf, geojson = geojson,
                               locations = 'parcel_number', color = 'taxable_value',
                               featureidkey = 'properties.parcel_number',
                               mapbox_style = 'carto-positron',
                               zoom = 13, center = {'lat': COORDS[0], 'lon': COORDS[1]},
                               opacity = 0.5,
                               hover_data = {'parcel_number': True,
                                             'taxable_value': ':.2f',
                                             'site_address': True})
    fig.update_layout(margin={'r': 0,'t': 0,'l': 0,'b': 0})
    # optionally add marker for parcel of interest
    if highlight_parcel:
        fig.add_trace(go.Scattermapbox(
                      lat = parcel_markers.Latitude,
                      lon = parcel_markers.Longitude,
                      mode = 'markers',
                      hoverinfo = 'none',
                      marker = go.scattermapbox.Marker(size = 14, color = 'black')))
    graphJSON = json.dumps(fig, cls = plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def search_and_paginate(table, search_dict: dict, page: int):
    """
    Function to filter an SQL Alchemy table using paramters specified in search_dict
    a dict of 'column': 'search text'. Returns a paginate object with 15 records per page

    @param table: SQL Alchmeny clasd object
    @param search_dict: a dict of columns: search text 
    @param page: integer to indicate what page to start from
    @returns: SQL Alchemy paginate object with specified filters applied
    """
    # initalize empty list of filters
    filters = []
    # iterate through search_dict and add filters to list
    for col, text in search_dict.items():
        if col != "":
            search = f'%{text}%'
            filters.append(getattr(table, col).like(search))
    # apply filters and paginate
    page_obj = db.session.query(table).\
               where(and_(*filters)).paginate(page = page, per_page = 15)
    return page_obj


def filter_table(table, filter_dict: dict = None) -> pd.DataFrame:
    """
    Function to return pd.DataFrame of a SQL table, with specified filters applied

    @param table: name of table to query
    @param filter_dict: a dict of columns: values to be used to filter table
    @returns: pd.DataFrame of SQL query
    """
    filters = []
    if filter_dict:
        for col, value in filter_dict.items():
            filters.append(getattr(table, col) == value)
    query = db.session.query(table).where(and_(*filters))
    df = pd.read_sql(query.statement, db.session.connection())
    return df

def check_password(form):
    """
    Function to check if user-input username and password match database record

    @param form: Flask WTF-Form with fields 'name' and 'password'
    @returns: bool to indicate if password was correct
    """
    user = form.name.data
    pw = form.password.data
    # replace this with function to retrieve user's password credentials
    dbpass = db.session.execute(db.select(web_users.password)).first()[0]
    check = check_password_hash(dbpass, pw)
    return check

def login_required(f):
    """
    Wrapper for Flask route to ensure user has logged in
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'), code = 302)
        return f(*args, **kwargs)
    return decorated_function


def get_list(table, column: str) -> list:
    """
    Function to return all unique values in specified table, column of database

    @param table: name of table to query
    @param column: name of column to find unique values
    @returns: sorted list of unique values in specified table and column
    """
    query = db.session.execute(db.select(getattr(table, column))).all()
    try:
        res = [tup[0] for tup in query]
        # make unique
        uniq = list(set(res))
        return sorted(uniq, key = str.lower)
    except:
        return []



def filter_properties(searchdict: dict, page: int):
    """
    Function to take user-entered paramteres from SearchForm() and query sqllite property database

    @param searchdict: dict of data from SearchForm()
    @param page: integer to indicate what page to start from
    @returns: flask-sqlalchmeny pagination object
    """
    # map max and min to operators
    mapping = {'max': '<=', 'min': '>='}
    # initalize a list of filters
    filters = []
    for col, searchval in searchdict.items():
        if searchval:
            operator = mapping.get(col.split('_')[0])
            column = '_'.join(col.split('_')[1:])
            search = f'%{text}%'
            filters.append(text(f'{getattr(property_data, column)} {operator} {searchval}'))
    page_obj = db.session.query(property_data).\
               where(and_(*filters)).paginate(page = page, per_page = 15)
    return page_obj

