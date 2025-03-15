from includes.pagination_class import PaginationClass
from flask import Flask, jsonify, request
from flask.blueprints import Blueprint
from includes.utils_class import clean_and_truncate, parse_date
from models.model import SessionFeed
from includes.utils_class import parse_date

feeds_router = Blueprint('feeds', __name__)

@feeds_router.route('/sessions/', defaults={'page': 1, 'per_page': 50}, endpoint='get_sessions')
@feeds_router.route('/sessions/<int:page>/', defaults={'per_page': 50}, endpoint='get_sessions')
@feeds_router.route('/sessions/<int:page>/<int:per_page>/', endpoint='get_sessions')
def get_sessions(page, per_page):
    paginator = PaginationClass()
    paginator.page = page
    paginator.per_page = per_page
    paginator.set_paging_params(request)

    # ✅ Query met paginatie
    sessions = SessionFeed.query \
        .order_by(SessionFeed.created_at.desc()) \
        .limit(paginator.per_page) \
        .offset(paginator.offset) \
        .all()

    total_sessions = SessionFeed.query.count()
    total_pages = (total_sessions + paginator.per_page - 1) // paginator.per_page

    # ✅ Data formatteren met absolute URL's
    formatted_sessions = []
    for session in sessions:
        formatted_sessions.append({
            'id': session.id,
            'created_at': parse_date(session.created_at) if session.created_at else None,
            'share_link': session.share_link,
            'target_link': session.target_link,
            'title': session.report_title,
            'summary': clean_and_truncate(session.summary) if session.summary else None,
            'preview_image': f"{request.host_url.rstrip('/')}{session.preview_image}" if session.preview_image else None,
            'thumbnail': f"{request.host_url.rstrip('/')}{session.thumbnail}" if session.thumbnail else None
        })

    # ✅ Teruggeven als JSON-response
    return jsonify({
        'sessions': formatted_sessions,
        'total_sessions': total_sessions,
        'total_pages': total_pages,
        'current_page': paginator.page,
        'per_page': paginator.per_page
    })
