# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
from pylinkvalidator import api

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    data = {}

    form = request.form
    if len(form):
        website_url = form.get('website_url')
        timeout = int(form.get('timeout'))
        depth = int(form.get('depth'))
        result = return_error_pages(
            site_links=[website_url],
            config={
                'depth': depth,
                'timeout': timeout,
            },
        )
        data['bad_links'] = result
    return render_template('index.html', **data)

def return_error_pages(site_links=[], config={}):
    crawled_site = api.crawl_with_options(
        site_links,
        config,
    )
    error_pages = crawled_site.error_pages
    error_items = []
    for item in error_pages:
        raw = error_pages[item]
        item_url = raw.url_split.geturl()
        item_status = raw.status
        item_message = raw.get_status_message()
        data = {
            'item_url': item_url,
            'item_status': item_status,
            'item_message': item_message,
        }
        error_items.append(data)
    return error_items
