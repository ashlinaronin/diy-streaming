import os
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import logging
import json
import ast

DB_PATH = os.environ.get('DB_PATH', './data/jobs.db')
SLSKD_BASE = os.environ.get('SLSKD_BASE_URL', 'http://slskd:5030')
MUSIC_DIR = os.environ.get('MUSIC_DIR', '/music')
SLSKD_USERNAME = os.environ.get('SLSKD_USERNAME', 'slskd')
SLSKD_PASSWORD = os.environ.get('SLSKD_PASSWORD', 'slskd')

slskd_token = None
slskd_token_expires_at = 0

app = Flask(__name__)

# simple request logging to help debug proxied paths
logging.basicConfig(level=logging.INFO)


@app.before_request
def log_incoming():
    env_uri = request.environ.get('REQUEST_URI') or ''
    app.logger.info(f"Incoming {request.method} path={request.path} full_path={request.full_path} REQUEST_URI={env_uri}")


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


def parse_result(raw_result):
    if raw_result in (None, ''):
        return None
    if isinstance(raw_result, (dict, list)):
        return raw_result
    try:
        return json.loads(raw_result)
    except Exception:
        pass
    text = str(raw_result).strip()
    if text.startswith('[') or text.startswith('{'):
        try:
            return ast.literal_eval(text)
        except Exception:
            pass
    return raw_result


def get_jobs(limit=100):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, line, artist, album, status, created_at, updated_at, result, error FROM jobs ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    jobs = []
    for r in rows:
        raw_result = r[7]
        parsed = parse_result(raw_result)
        progress = None

        if isinstance(parsed, dict) and parsed.get('expected_files'):
            expected = parsed.get('expected_files') or []
            total = len(expected)
            expected_basenames = [os.path.basename(f.replace('\\','/')).lower() for f in expected]
            search_dirs = []
            if MUSIC_DIR:
                search_dirs.append(MUSIC_DIR)
            local_music = os.path.join(os.getcwd(), 'music')
            if local_music not in search_dirs:
                search_dirs.append(local_music)
            found_set = set()
            for base_dir in search_dirs:
                if not os.path.exists(base_dir):
                    continue
                for root, dirs, files in os.walk(base_dir):
                    for fn in files:
                        low = fn.lower()
                        if low in expected_basenames:
                            found_set.add(low)
            found = len(found_set)
            progress = f"{found}/{total}"
        else:
            try:
                if isinstance(raw_result, str) and "filename" in raw_result:
                    import re
                    matches = re.findall(r"filename'?:\s*'([^']+)'", raw_result)
                    if matches:
                        expected = matches
                        total = len(expected)
                        expected_basenames = [os.path.basename(f.replace('\\','/')).lower() for f in expected]
                        search_dirs = []
                        if MUSIC_DIR:
                            search_dirs.append(MUSIC_DIR)
                        local_music = os.path.join(os.getcwd(), 'music')
                        if local_music not in search_dirs:
                            search_dirs.append(local_music)
                        found_set = set()
                        for base_dir in search_dirs:
                            if not os.path.exists(base_dir):
                                continue
                            for root, dirs, files in os.walk(base_dir):
                                for fn in files:
                                    low = fn.lower()
                                    if low in expected_basenames:
                                        found_set.add(low)
                        found = len(found_set)
                        progress = f"{found}/{total}"
            except Exception:
                pass

        jobs.append({
            'id': r[0], 'line': r[1], 'artist': r[2], 'album': r[3], 'status': r[4],
            'created_at': r[5], 'updated_at': r[6], 'result': parsed if parsed is not None else r[7], 'error': r[8], 'progress': progress
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
    # ensure result is JSON-serializable string when it's a list/dict
    store_result = result
    if result is not None and not isinstance(result, str):
        try:
            store_result = json.dumps(result)
        except Exception:
            store_result = str(result)

    c.execute('UPDATE jobs SET status = ?, updated_at = ?, result = ?, error = ? WHERE id = ?', (status, now, store_result, error, job_id))
    conn.commit()
    conn.close()


def normalize_line(line):
    # Treat the raw line as a free-form search query.
    # Older behavior expected "Artist - Album"; now we simply return the
    # entire line as `artist` (search text) and leave `album` empty so
    # downstream code builds the search query from the full line.
    q = line.strip()
    return q, ''


def get_slskd_headers():
    global slskd_token, slskd_token_expires_at
    now = int(time.time())
    if not slskd_token or now >= (slskd_token_expires_at - 60):
        login = requests.post(
            f"{SLSKD_BASE}/api/v0/session",
            json={"username": SLSKD_USERNAME, "password": SLSKD_PASSWORD},
            timeout=15,
        )
        if login.status_code >= 400:
            raise RuntimeError(f"slskd auth failed: {login.status_code} {login.text}")
        payload = login.json() if login.content else {}
        token = payload.get('token')
        expires = int(payload.get('expires') or 0)
        if not token:
            raise RuntimeError(f"slskd auth response missing token: {payload}")
        slskd_token = token
        slskd_token_expires_at = expires
    return {
        'Authorization': f'Bearer {slskd_token}',
        'Content-Type': 'application/json',
    }


def _extract_files_from_search_results(results):
    if not isinstance(results, (dict, list)):
        return []

    flattened = []
    payload = results.get('responses') if isinstance(results, dict) else results
    if isinstance(payload, dict):
        payload = [payload]

    for response in payload or []:
        if not isinstance(response, dict):
            continue

        search_id = response.get('id') or results.get('id') if isinstance(results, dict) else None
        username = response.get('username') or response.get('user') or ''
        files = response.get('files') or response.get('items') or []
        if not files and response.get('filename'):
            files = [response]

        for file_info in files:
            if not isinstance(file_info, dict):
                continue
            merged = dict(file_info)
            if username:
                merged['username'] = username
            if search_id:
                merged['searchId'] = search_id
            flattened.append(merged)

    return flattened


def _group_files_by_peer_and_release(files):
    """
    Group flattened file entries by username (peer) and by a release key derived
    from the filename path (best-effort). Returns a dict: { username: {release_key: [files...] } }
    """
    groups = {}
    for f in files:
        user = _candidate_username(f) or 'unknown'
        # best-effort release key: directory path of filename if present
        filename = (f.get('filename') or f.get('fileName') or '')
        rel = ''
        if filename:
            # normalize separators
            p = filename.replace('\\', '/').strip('/ ')
            parts = p.split('/')
            if len(parts) > 1:
                rel = '/'.join(parts[:-1])
            else:
                rel = parts[0]
        groups.setdefault(user, {}).setdefault(rel, []).append(f)
    return groups


def _candidate_extension(entry):
    filename = (entry.get('filename') or entry.get('fileName') or '').lower()
    ext = (entry.get('extension') or os.path.splitext(filename)[1]).lower().lstrip('.')
    return ext


def _candidate_bitrate(entry):
    for key in ('bitRate', 'bitrate', 'kbps', 'bitrate_kbps'):
        value = entry.get(key)
        if value not in (None, ''):
            try:
                return int(value)
            except (TypeError, ValueError):
                pass
    return 0


def _candidate_size(entry):
    size = entry.get('size')
    try:
        return int(size or 0)
    except (TypeError, ValueError):
        return 0


def _candidate_username(entry):
    return entry.get('username') or entry.get('user') or ''


def _candidate_search_id(entry):
    return entry.get('searchId') or ''


def slskd_search(artist, album):
    q = f"{artist} {album}".strip()
    headers = get_slskd_headers()
    search_id = str(uuid.uuid4())
    resp = requests.post(
        f"{SLSKD_BASE}/api/v0/searches",
        json={'id': search_id, 'searchText': q},
        headers=headers,
        timeout=15,
    )
    if resp.status_code >= 400:
        raise RuntimeError(f"slskd search request failed: {resp.status_code} {resp.text}")

    created = resp.json() if resp.content else {}
    search_id = created.get('id') or search_id
    deadline = datetime.utcnow() + timedelta(seconds=45)
    while datetime.utcnow() < deadline:
        poll = requests.get(
            f"{SLSKD_BASE}/api/v0/searches/{search_id}?includeResponses=true",
            headers=headers,
            timeout=15,
        )
        if poll.status_code == 404:
            time.sleep(2)
            continue
        poll.raise_for_status()
        payload = poll.json() if poll.content else {}
        files = _extract_files_from_search_results(payload)
        if files:
            return {'id': search_id, 'responses': payload.get('responses') if isinstance(payload, dict) else payload, 'files': files}
        time.sleep(2)
    raise RuntimeError(f"slskd search for '{q}' returned no results before timeout")


def choose_candidate(results):
    # New behavior: prefer a peer (username) that offers multiple files from a
    # single release (directory). Prefer FLAC-only groups, otherwise high-bitrate MP3.
    flattened = _extract_files_from_search_results(results)
    if not flattened:
        return None

    groups = _group_files_by_peer_and_release(flattened)
    # candidate selection: (peer, release) -> list of files
    best = None
    best_score = -1
    for user, releases in groups.items():
        for rel, files in releases.items():
            # Prefer one file per track: if multiple encodings exist for the same
            # track basename, pick FLAC over MP3. Build filtered list for scoring.
            seen = {}
            filtered = []
            for e in files:
                fn = (e.get('filename') or e.get('fileName') or '')
                base = os.path.splitext(os.path.basename(fn.replace('\\', '/')))[0].lower()
                cur = seen.get(base)
                ext = _candidate_extension(e)
                if cur is None:
                    seen[base] = e
                else:
                    # choose preference: flac > mp3(>=256) > others by size
                    cur_ext = _candidate_extension(cur)
                    # if either is flac, prefer flac
                    if 'flac' in ext and 'flac' not in cur_ext:
                        seen[base] = e
                    elif 'flac' in cur_ext and 'flac' not in ext:
                        pass
                    else:
                        # prefer mp3 with higher bitrate if comparing mp3s
                        cur_b = _candidate_bitrate(cur)
                        new_b = _candidate_bitrate(e)
                        if new_b > cur_b:
                            seen[base] = e
                        else:
                            # otherwise prefer larger size
                            if _candidate_size(e) > _candidate_size(cur):
                                seen[base] = e
            filtered = list(seen.values())
            # score by count, format preference, and bitrate
            count = len(filtered)
            score = count * 100
            flac_count = sum(1 for e in filtered if 'flac' in _candidate_extension(e) or '.flac' in (e.get('filename') or '').lower())
            mp3_256_count = sum(1 for e in filtered if (('mp3' in _candidate_extension(e) or '.mp3' in (e.get('filename') or '').lower()) and _candidate_bitrate(e) >= 256))
            score += flac_count * 50 + mp3_256_count * 20
            # prefer non-empty release key (grouping by folder) slightly
            if rel:
                score += 5
            if score > best_score:
                best_score = score
                # return the filtered files selection so we avoid mixing encodings
                best = (user, rel, filtered)

    # Return structured batch info when available
    if best:
        user, rel, files = best
        return {'username': user, 'release': rel, 'files': files}
    return None


def initiate_download(candidate, search_id=None):
    # candidate may be a structured batch (username, files)
    if isinstance(candidate, dict) and candidate.get('files'):
        username = candidate.get('username')
        files = candidate.get('files')
    else:
        username = _candidate_username(candidate) or candidate.get('username')
        files = [candidate]

    if not username or not files:
        return False

    payload = {
        'username': username,
        'files': [],
        'id': str(uuid.uuid4()),
        'searchId': search_id or (_candidate_search_id(files[0]) if files else None),
    }
    for f in files:
        payload['files'].append({'filename': f.get('filename') or f.get('fileName'), 'size': _candidate_size(f)})

    try:
        resp = requests.post(
            f"{SLSKD_BASE}/api/v0/transfers/downloads/batches",
            json=payload,
            headers=get_slskd_headers(),
            timeout=20,
        )
        if resp.status_code >= 400:
            app.logger.warning('slskd batch enqueue failed: %s %s', resp.status_code, resp.text)
            return False
        return True
    except Exception as e:
        app.logger.exception('initiate_download exception: %s', e)
        return False


def wait_for_file(query, timeout=300):
    # Poll MUSIC_DIR for a file whose filename contains all words from `query`.
    terms = [t.lower() for t in query.split() if t.strip()]
    if not terms:
        return None
    deadline = datetime.utcnow() + timedelta(seconds=timeout)
    while datetime.utcnow() < deadline:
        for root, dirs, files in os.walk(MUSIC_DIR):
            for fn in files:
                low = fn.lower()
                if all(t in low for t in terms):
                    return os.path.join(root, fn)
        time.sleep(5)
    return None


def wait_for_all_files(expected_files, timeout=600):
    """Wait until all expected_files (list of relative paths or filenames) exist under MUSIC_DIR."""
    normalized = [os.path.normpath(f).replace('\\', '/') for f in expected_files]
    deadline = datetime.utcnow() + timedelta(seconds=timeout)
    while datetime.utcnow() < deadline:
        found = []
        for ef in normalized:
            # check for exact filename match in any subdir
            ef_basename = os.path.basename(ef).lower()
            matched = False
            for root, dirs, files in os.walk(MUSIC_DIR):
                for fn in files:
                    if fn.lower() == ef_basename:
                        matched = True
                        break
                if matched:
                    break
            if matched:
                found.append(ef)
        if len(found) == len(normalized):
            # return list of full paths
            results = []
            for ef in normalized:
                ef_basename = os.path.basename(ef).lower()
                for root, dirs, files in os.walk(MUSIC_DIR):
                    for fn in files:
                        if fn.lower() == ef_basename:
                            results.append(os.path.join(root, fn))
                            break
                    if len(results) >= len(found):
                        break
            return results
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
            candidate = choose_candidate(results.get('files', [])) if isinstance(results, dict) else choose_candidate(results)
            if not candidate:
                mark_job(job_id, 'failed', error='no suitable candidate found')
                continue
            ok = initiate_download(candidate, search_id=results.get('id') if isinstance(results, dict) else None)
            if not ok:
                mark_job(job_id, 'failed', error='failed to initiate download')
                continue

            # If candidate is a batch (dict with 'files'), wait for all files.
            if isinstance(candidate, dict) and candidate.get('files'):
                expected = [f.get('filename') or f.get('fileName') for f in candidate.get('files')]
                mark_job(job_id, 'downloading', result=str({'expected_files': expected}))
                found_all = wait_for_all_files(expected, timeout=900)
                if found_all:
                    mark_job(job_id, 'completed', result=str(found_all))
                else:
                    mark_job(job_id, 'failed', error='download timeout or files not found')
            else:
                # single-file fallback
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


def get_job(job_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, line, artist, album, status, created_at, updated_at, result, error FROM jobs WHERE id = ?', (job_id,))
    r = c.fetchone()
    conn.close()
    if not r:
        return None

    raw_result = r[7]
    parsed = parse_result(raw_result)
    progress = None

    if isinstance(parsed, dict) and parsed.get('expected_files'):
        expected = parsed.get('expected_files') or []
        total = len(expected)
        found = 0
        expected_basenames = [os.path.basename(os.path.normpath(f)).lower() for f in expected]
        for root, dirs, files in os.walk(MUSIC_DIR):
            for fn in files:
                if fn.lower() in expected_basenames:
                    found += 1
        progress = f"{found}/{total}"
    else:
        try:
            if isinstance(raw_result, str) and "filename" in raw_result:
                import re
                matches = re.findall(r"filename'?:\s*'([^']+)'", raw_result)
                if matches:
                    expected = matches
                    total = len(expected)
                    expected_basenames = [os.path.basename(os.path.normpath(f)).lower() for f in expected]
                    found = 0
                    for root, dirs, files in os.walk(MUSIC_DIR):
                        for fn in files:
                            if fn.lower() in expected_basenames:
                                found += 1
                    progress = f"{found}/{total}"
        except Exception:
            pass

    job = {
        'id': r[0], 'line': r[1], 'artist': r[2], 'album': r[3], 'status': r[4],
        'created_at': r[5], 'updated_at': r[6], 'result': parsed if parsed is not None else r[7], 'error': r[8], 'progress': progress
    }
    return job


@app.route('/api/job/<int:job_id>')
def api_job(job_id):
    job = get_job(job_id)
    if not job:
        return jsonify({'error': 'not found'}), 404
    return jsonify(job)


@app.route('/progress/<int:job_id>')
def progress(job_id):
    job = get_job(job_id)
    if not job:
        return "Job not found", 404
    return render_template('progress.html', job=job)


# Ensure DB is initialized and worker thread runs when the module is loaded
init_db()
t = threading.Thread(target=worker_loop, daemon=True)
t.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
