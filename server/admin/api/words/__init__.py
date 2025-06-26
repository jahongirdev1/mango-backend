from sanic import Blueprint

from admin.api.words.item import WordView
from admin.api.words.list import WordsView

words_bp = Blueprint('words', url_prefix='/words')

words_bp.add_route(WordsView.as_view(), '/')
words_bp.add_route(WordView.as_view(), '/<word_id>')
