# HouseHunter

HouseHunter is a flask web app I created to compile and present data scraped from publicly available
[Pierce County property records](https://atip.piercecountywa.gov/app/parcelSearch/search).

[HosueHunter](https://buckleya2.pythonanywhere.com/)

I collected data from all single family homes in Gig Harbor, WA and built a SQLite database

I pulled parcel map data in JSON format from the same website to build the plots

Site is hosted on pythonanywhere

## Changelog

- 10/30/2022: inital commit of basic website

## Finding Information by Address

The main landing page of the site is a form to search property records for Gig Harbor
by address. The search form is a live search powered by jQuery using all addresses
in my database as possible options

![screenshot of search](/screenshots/livesearch_example.png)

## Parcel Information Display Page
![screenshot of website](/screenshots/website_overview.png)

After search for an address, you are directed to a URL built based on parcel ID.

This page contains multiple types of information

- map showing selected parcels and other parcels in the same census neighborhood
- z-scores showing the selected property as compared to it's neighborhood
- historical tax assessment values
- historical sale data


