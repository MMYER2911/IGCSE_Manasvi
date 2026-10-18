"""Single-family preview access, not a multi-user parent/student account system."""
import secrets
import threading
import time
from collections import OrderedDict
from datetime import timedelta
from flask import abort, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


def init_access(app):
    password = app.config.pop('ACCESS_PASSWORD', None)
    if app.config['HOSTED'] and (not password or len(password) < 16):
        raise RuntimeError('Set TUTOR_PASSWORD to a private passphrase of at least 16 characters in the hosting settings before deployment.')
    enabled = bool(password)
    app.config['ACCESS_ENABLED'] = enabled
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)
    password_hash = generate_password_hash(password) if enabled else None
    # Restart/credential rotation invalidates prior authentication. Use one worker.
    auth_version = secrets.token_hex(32)
    failures = OrderedDict()
    lock = threading.Lock()

    @app.before_request
    def require_login():
        if not enabled or request.endpoint in ('login', 'static', 'health'):
            return
        if not secrets.compare_digest(session.get('auth_version', ''), auth_version):
            return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if not enabled:
            return redirect(url_for('home'))
        error = None
        if request.method == 'POST':
            # Trust only the connected peer, never a client-supplied forwarded IP.
            # The single-worker preview uses a bounded in-memory attempt limiter.
            peer = request.remote_addr or 'unknown'
            now = time.monotonic()
            with lock:
                attempts = [t for t in failures.pop(peer, []) if now-t < 60]
                if len(attempts) >= 5:
                    failures[peer] = attempts
                    abort(429, 'Too many attempts. Wait one minute before trying again.')
                failures[peer] = attempts + [now]
                while len(failures) > 1024:
                    failures.popitem(last=False)
            supplied = request.form.get('password', '')
            if len(supplied) <= 1024 and check_password_hash(password_hash, supplied):
                with lock:
                    failures.pop(peer, None)
                session.clear()
                session['auth_version'] = auth_version
                session['csrf'] = secrets.token_hex(24)
                session.permanent = True
                return redirect(url_for('home'))
            error = 'Incorrect passphrase. Please try again.'
        return render_template('login.html', error=error)

    @app.route('/logout', methods=['POST'])
    def logout():
        session.clear()
        return redirect(url_for('login'))
