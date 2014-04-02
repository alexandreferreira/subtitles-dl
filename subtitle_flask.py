
import json
from flask import Flask, request
from flask.helpers import make_response
from utils import search_for_subtitle, BASE_DIR
from subliminal import cache_region, MutexLock
import datetime
app = Flask(__name__)

def get_params(request):
    info = {}
    if request.method == 'GET':
        for key, value in request.args.lists():
            info[key] = value[0]
    else:
        for key, value in request.form.lists():
            info[key] = value[0]
    if request.files:
        info['post_file'] = {}
        for key, value in request.files.lists():
            info['post_file'][key] = value[0]
    return info

@app.route('/search', methods=['GET'])
def hello_world():
    params = get_params(request)
    infos = search_for_subtitle(params.get('file_name'), params.get('languages'))
    return make_response(json.dumps(infos))

if __name__ == '__main__':
    if not cache_region.is_configured:
        cache_region.configure('dogpile.cache.dbm', expiration_time=datetime.timedelta(days=30),  # @UndefinedVariable
                           arguments={'filename':BASE_DIR, 'lock_factory': MutexLock})
    app.run(host="0.0.0.0")


