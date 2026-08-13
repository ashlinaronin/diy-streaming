from flask import Flask, request, jsonify
import os
import threading
import time

app = Flask(__name__)
last_search = {}

@app.route('/api/search')
def api_search():
    q = request.args.get('q','')
    # naive parse: assume 'Artist Album' or 'Artist - Album'
    artist = ''
    album = ''
    if '-' in q:
        parts = q.split('-')
        artist = parts[0].strip()
        album = ' - '.join(parts[1:]).strip()
    else:
        parts = q.split()
        if len(parts) >= 2:
            artist = parts[0]
            album = ' '.join(parts[1:])
    cid = f"mock-{int(time.time()*1000)}"
    last_search[cid] = {'artist': artist or 'Artist', 'album': album or 'Album'}
    # return a FLAC candidate
    return jsonify([{'id': cid, 'format': 'flac', 'bitrate': 0, 'filename': f"{artist} - {album}.flac"}])

@app.route('/api/download', methods=['POST'])
def api_download():
    data = request.get_json() or {}
    cid = data.get('id')
    info = last_search.get(cid)
    if not info:
        return jsonify({'error': 'unknown id'}), 400
    # create a file in /music to simulate download
    music_dir = '/music'
    os.makedirs(music_dir, exist_ok=True)
    # create a filename containing both artist and album so the worker's simple
    # substring search can find it reliably
    fname = f"{info['artist']} {info['album']} - mock.flac"
    fpath = os.path.join(music_dir, fname)
    with open(fpath, 'wb') as f:
        f.write(b'MOCK')
    return jsonify({'status': 'started', 'path': fpath})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5030'))
    app.run(host='0.0.0.0', port=port)
