# -*- coding: utf-8 -*-

from flask import Flask, render_template
from pylinkvalidator import api

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def index():
    data = {
        'error_pages': return_error_pages(),
    }
    return render_template('index.html', **data)


def return_error_pages(site_links=['https://www.operun.de']):
    crawled_site = api.crawl_with_options(
        site_links,
        {
            'run-once': True,
            'workers': 4,
        },
    )
    error_pages = crawled_site.error_pages
    error_links = []
    for item in error_pages:
        error_links.append(item.geturl())
    return error_links
