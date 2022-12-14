import datetime
import geopandas as gpd
import json
import plotly
import plotly_express as px

from flask import abort, Flask, url_for, render_template, request, redirect, session
import flask_sqlalchemy

from db import *
from forms import *
from helpers import *

app = Flask(__name__, static_folder = 'static')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////Users/abuckley/Documents/flask/data/sqllite/propertydb.db"
app.config['SECRET_KEY'] = '7efce7af669eed5d0e1b32cf48d1d243c7d8bec2ab9e2c40'

db.init_app(app)

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/single', methods = ['GET', 'POST'])
def single():
    form = AddressForm()
    address_list = get_list(property_data, 'site_address')
    parcel_list = get_list(property_data, 'parcel_number')
    if form.validate_on_submit():
        if request.form['address']:
            site_address = request.form['address']
            # test if address is in dataset
            if site_address not in address_list:
                msg = 'Address entered is not in dataset, please select from dropdown options'
                return render_template('find_single.html', form = form, address_list = address_list,
                                        parcel_list = parcel_list, msg = msg)
            parcel_number = filter_table(property_data, {'site_address': site_address}).parcel_number.item()
        return redirect(url_for('render_parcel', parcel_number = parcel_number))
    return render_template('find_single.html', form = form, address_list = address_list,
                            parcel_list = parcel_list)


@app.route('/parcel/<parcel_number>', methods = ['GET', 'POST'])
def render_parcel(parcel_number):
    # get address
    site_address = filter_table(property_data, {'parcel_number': parcel_number}).site_address.item()
    # get neighborhood map information 
    geojson, parceldf = find_neighborhood(parcel_number)
    # get neighborhood z-score stats
    z_dict = neighborhood_stats(parceldf, parcel_number)
    # get sale data
    sale_dict = sales_stats(parcel_number)
    # get tax data
    tax_plot, tax_due = tax_stats(parcel_number) 
    # make plot
    map_plot = plot_map(geojson, parceldf, parcel_number)
    return render_template('display_parcel.html', parcel_number = parcel_number, site_address = site_address, 
                           z_dict = z_dict, sale_dict = sale_dict, map_plot = map_plot, tax_plot = tax_plot)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search', methods = ['GET', 'POST'])
def search():
    # clear any prior searches
    session.pop('searchdict', None)
    form = SearchForm()
    if form.validate_on_submit():
        searchdict = form.data
        searchdict.pop('csrf_token')
        session['searchdict'] = searchdict
        return redirect(url_for('search_res'))
    return render_template('search.html', form = form)

@app.route('/result', methods = ['GET', 'POST'])
def search_res():
    if not session.get('searchdict'):
        msg = 'no search data'
        return render_template('pages.html', msg = msg)
    page = request.args.get('page', 1, type=int)
    pagination = filter_properties(session['searchdict'], page)
    return render_template('pages.html', pagination = pagination)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('nopage.html')

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 5000)
