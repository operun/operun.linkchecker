# -*- coding: utf-8 -*-

import csv
import StringIO

from flask import Flask, make_response, render_template, request
from pylinkvalidator import api

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    template = 'index.html'
    form = request.form
    data = {}

    if len(form):
        submit = form.get('form.button.submit', '')
        website_url = form.get('website_url', '')
        timeout = int(form.get('timeout', '5'))
        depth = int(form.get('depth', '0'))
        csv_data = form.get('csv_data', '')

        if submit == 'csv':
            if csv_data:
                return csv_response(csv_data)
            return render_template(template)

        result = return_error_pages(
            site_links=[website_url],
            config={
                'depth': depth,
                'timeout': timeout,
            },
        )

        csv_data = generate_csv(result)

        data['errors'] = result
        data['website_url'] = website_url
        data['timeout'] = timeout
        data['depth'] = depth
        data['csv_data'] = csv_data

    return render_template(template, **data)


def return_error_pages(site_links=[], config={}):
    error_items = []
    crawled_site = api.crawl_with_options(
        site_links,
        config,
    )
    error_pages = crawled_site.error_pages
    for item in error_pages:
        raw = error_pages[item]
        item_url = raw.url_split.geturl()
        item_status = raw.status
        item_status_message = raw.get_status_message()
        data = {
            'item_url': item_url,
            'item_status': item_status,
            'item_status_message': item_status_message,
        }
        error_items.append(data)
    return error_items


def generate_csv(items):
    header = ['url', 'status']
    strIO = StringIO.StringIO()
    writer = csv.DictWriter(
        strIO,
        delimiter=',',
        lineterminator='\n',
        fieldnames=header,
    )
    writer.writeheader()
    for item in items:
        data = {
            'url': item['item_url'],
            'status': item['item_status'],
        }
        writer.writerow(data)
    return strIO.getvalue()


def csv_response(data):
    output = make_response(data)
    output.headers['Content-Disposition'] = 'attachment; filename=export.csv'
    output.headers["Content-type"] = "text/csv"
    return output
