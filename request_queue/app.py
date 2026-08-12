import os
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

DB_PATH = os.environ.get('DB_PATH', './data/jobs.db')
SLSKD_BASE = os.environ.get('SLSKD_BASE_URL', 'http://slskd:5030')
MUSIC_DIR = os.environ.get('MUSIC_DIR', '/music')

app = Flask(__name__)


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        line TEXT,
        artist TEXT,
        album TEXT,
        status TEXT,
        created_at TEXT,
        updated_at TEXT,
        result TEXT,
        error TEXT
    )
    ''')
    conn.commit()
    conn.close()


def add_job(line, artist, album):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute('INSERT INTO jobs (line, artist, album, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)',
              (line, artist, album, 'queued', now, now))
    conn.commit()
    conn.close()


def get_jobs(limit=100):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, line, artist, album, status, created_at, updated_at, result, error FROM jobs ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    jobs = []
    for r in rows:
        jobs.append({
            'id': r[0], 'line': r[1], 'artist': r[2], 'album': r[3], 'status': r[4],
            'created_at': r[5], 'updated_at': r[6], 'result': r[7], 'error': r[8]
        })
    return jobs


def pick_next_job():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, artist, album FROM jobs WHERE status = 'queued' ORDER BY id ASC LIMIT 1")
    row = c.fetchone()
    if row:
        job_id, artist, album = row
        now = datetime.utcnow().isoformat()
        c.execute("UPDATE jobs SET status = 'searching', updated_at = ? WHERE id = ?", (now, job_id))
        conn.commit()
        conn.close()
        return job_id, artist, album
    conn.close()
    return None


def mark_job(job_id, status, result=None, error=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute('UPDATE jobs SET status = ?, updated_at = ?, result = ?, error = ? WHERE id = ?', (status, now, result, error, job_id))
    conn.commit()
    conn.close()


def normalize_line(line):
    # Expect: Artist - Album
    parts = [p.strip() for p in line.split('-')]
    if len(parts) >= 2:
        artist = parts[0]
        album = ' - '.join(parts[1:])
    else:
        artist = parts[0]
        album = ''
    return artist, album


def slskd_search(artist, album):
    # Try a best-effort search using slskd's web API. This may need adjustment depending on slskd version.
    q = f"{artist} {album}".strip()
    try:
        resp = requests.get(f"{SLSKD_BASE}/api/search", params={'q': q}, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {'error': str(e)}


def choose_candidate(results):
    # Results format unknown; try to be defensive.
    # Search for FLAC first, then MP3 >=256
    if not isinstance(results, list):
        return None
    flac = None
    mp3_256 = None
    for r in results:
        ftype = r.get('format') or r.get('filetype') or ''
        bitrate = r.get('bitrate') or r.get('kbps') or 0
        if 'flac' in ftype.lower() or ftype.lower() == 'flac':
            flac = r
            break
        if 'mp3' in ftype.lower() and int(bitrate or 0) >= 256:
            mp3_256 = mp3_256 or r
    return flac or mp3_256


def initiate_download(candidate):
    # Best-effort: call slskd download API. If unavailable, return False.
    try:
        url = f"{SLSKD_BASE}/api/download"
        resp = requests.post(url, json={'id': candidate.get('id')}, timeout=10)
        resp.raise_for_status()
        return True
    except Exception:
        return False


def wait_for_file(artist, album, timeout=300):
    # Poll MUSIC_DIR for a new file matching artist/album in filename for up to timeout seconds
    deadline = datetime.utcnow() + timedelta(seconds=timeout)
    while datetime.utcnow() < deadline:
        for root, dirs, files in os.walk(MUSIC_DIR):
            for fn in files:
                low = fn.lower()
                if artist.lower() in low and album.lower() in low:
                    return os.path.join(root, fn)
        time.sleep(5)
    return None


def worker_loop():
    while True:
        next_job = pick_next_job()
        if next_job is None:
            time.sleep(5)
            continue
        job_id, artist, album = next_job
        try:
            results = slskd_search(artist, album)
            if results.get('error'):
                mark_job(job_id, 'failed', error='slskd search error: ' + results.get('error'))
                continue
            candidate = choose_candidate(results if isinstance(results, list) else results.get('results', []))
            if not candidate:
                mark_job(job_id, 'failed', error='no suitable candidate found')
                continue
            ok = initiate_download(candidate)
            if not ok:
                mark_job(job_id, 'failed', error='failed to initiate download')
                continue
            mark_job(job_id, 'downloading', result=str(candidate))
            found = wait_for_file(artist, album, timeout=600)
            if found:
                mark_job(job_id, 'completed', result=found)
            else:
                mark_job(job_id, 'failed', error='download timeout or file not found')
        except Exception as e:
            mark_job(job_id, 'failed', error=str(e))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    text = request.form.get('requests', '')
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines:
        artist, album = normalize_line(line)
        add_job(line, artist, album)
    return redirect(url_for('status'))


@app.route('/status')
def status():
    jobs = get_jobs(200)
    return render_template('status.html', jobs=jobs)


@app.route('/api/jobs')
def api_jobs():
    return jsonify(get_jobs(200))


if __name__ == '__main__':
    init_db()
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5000)
