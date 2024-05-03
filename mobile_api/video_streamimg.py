import mimetypes
import os
import re

from flask import Blueprint, request, jsonify, Response

video_stram_blueprint = Blueprint('video_steam_blueprint', __name__)


@video_stram_blueprint.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response


def get_chunk(full_path, byte1=None, byte2=None):
    file_size = os.stat(full_path).st_size
    start = 0

    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(full_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size


@video_stram_blueprint.route('/video/<path:file_path>', methods=['GET'])
def get_file(file_path):
    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    chunk, start, length, file_size = get_chunk(file_path, byte1, byte2)

    mimetype, _ = mimetypes.guess_type(file_path)
    if mimetype is None:
        mimetype = 'application/octet-stream'

    if range_header:
        resp = Response(chunk, 206, mimetype='video/mov',
                    content_type='video/mov', direct_passthrough=True)
        resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    else:
        resp = Response(chunk, 200, mimetype=mimetype,
                        content_type=mimetype, direct_passthrough=True)
    return resp
