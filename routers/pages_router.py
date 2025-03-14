from includes.pagination_class import PaginationClass
from flask import Flask, jsonify, render_template, redirect, request, send_from_directory
from flask.blueprints import Blueprint
from models.model import db, SessionFeed
from templates.partials.footer import render_footer
from templates.partials.nav_menu import render_nav

pages_router = Blueprint('pages', __name__)

# Rooutes for EN pages at root /
@pages_router.route('/')
def home():
    return render_template("index.html")

# Rooutes for NL pages at root /nl/
@pages_router.route('/nl/')
def home_nl():
    return render_template("/nl/index.html")

@pages_router.route('/shared-chat-sessions/', defaults={'page': 1, 'per_page': 10}, endpoint='shared_chat_sessions')
@pages_router.route('/shared-chat-sessions/<int:page>/', defaults={'per_page': 10}, endpoint='shared_chat_sessions')
@pages_router.route('/shared-chat-sessions/<int:page>/<int:per_page>/', endpoint='shared_chat_sessions')
def shared_chat_sessions(page, per_page):
    paginator = PaginationClass()
    paginator.page = page
    paginator.per_page = per_page
    paginator.set_paging_params(request)

    sessions = SessionFeed.query \
        .order_by(SessionFeed.created_at.desc()) \
        .limit(paginator.per_page) \
        .offset(paginator.offset) \
        .all()

    total_sessions = SessionFeed.query.count()
    total_pages = (total_sessions + paginator.per_page - 1) // paginator.per_page

    return render_template(
        'shared-chat-sessions.html',
        sessions=sessions,
        total_pages=total_pages,
        current_page=paginator.page,
        per_page=paginator.per_page
    )

@pages_router.context_processor
def inject_footer():
    return dict(render_footer=render_footer)

@pages_router.context_processor
def inject_nav():
    return dict(render_nav=render_nav)

@pages_router.route('/test')
def test():
    return render_template('test.html', user='Daniel')
