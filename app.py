# -*- coding: utf-8 -*-

import csv
from io import StringIO

from flask import Flask, render_template, request, stream_with_context
from pylinkvalidator import api
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    template = 'index.html'
    data = {}
    form = request.form
    if len(form):
        website_url = form.get('website_url', '')
        if not website_url:
            return render_template(template)
        timeout = int(form.get('timeout', '5'))
        depth = int(form.get('depth', '0'))
        result = return_error_pages(
            site_links=[website_url],
            config={
                'depth': depth,
                'timeout': timeout,
            },
        )
        # Append data
        data['errors'] = result
        data['website_url'] = website_url
        data['timeout'] = timeout
        data['depth'] = depth
        # Generate CSV
        generate_csv(result)
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
    data = StringIO()
    writer = csv.DictWriter(
        data,
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
