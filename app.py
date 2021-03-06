from flask import session, redirect, url_for, request, render_template, flash
from conf import *
from models import *
from util import *
from processing import process_log


@app.route('/')
def index():
    if 'me' in session:
        user = User.query.filter_by(uri=session['me']).first()
        servers = Server.query.all()
        return render_template('index.html', user=user, servers=servers)
    else:
        return render_template('index.html')


@app.route('/server-accounts', methods=['POST'])
def server_account_new():
    user = User.query.filter_by(uri=session['me']).first_or_404()
    server = Server.query.get(int(request.form['server_id']))
    account = UserOnServer(
        name=request.form['name'],
        auto_pub_threshold=num_or(request.form['auto_pub_threshold']),
        user=user,
        server=server
    )
    db.session.add(account)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/server-accounts/<int:account_id>', methods=['POST'])
def server_account_edit(account_id):
    account = UserOnServer.query.get_or_404(account_id)
    if 'delete' in request.args:
        db.session.delete(account)
    else:
        account.name = request.form['name']
        account.auto_pub_threshold = num_or(request.form['auto_pub_threshold'])
        account.server = Server.query.get_or_404(request.form['server_id'])
        db.session.add(account)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/upload-log', methods=['POST'])
def upload_log():
    user = User.query.filter_by(uri=session['me']).first_or_404()
    result = process_log(request.files['file'].read().decode('utf-8'), user)
    if result.status_code >= 300:
        reason = 'Something might be wrong with your server.'
        if result.status_code == 401:
            reason = 'Looks like you need to sign out and sign in again.'
        body = '%s %s\n' % (result.status_code, result.reason)
        body += '\n'.join(['%s: %s' % x for x in result.headers.items()])
        body += '\n\n' + result.text
        flash('Unfortunately, posting did not succeed! %s Response from your server: <pre>%s</pre>' % (reason, body))
    else:
        flash('Successfully <a href="%s">posted</a>!' % result.headers.get('Location'))
    return redirect(url_for('index'))

@app.route('/login')
def login():
    return micropub.authorize(me=request.args.get('me'), scope='post')

@app.route('/logout')
def logout():
    session['me'] = None
    return redirect(url_for('index'))

@app.route('/micropub-callback')
@micropub.authorized_handler
def micropub_callback(resp):
    session['me'] = resp.me
    user = User.query.filter_by(uri=resp.me).first()
    if user:
        user.micropub_uri = resp.micropub_endpoint
        user.access_token = resp.access_token
        db.session.add(user)
    else:
        db.session.add(User(uri=resp.me, micropub_uri=resp.micropub_endpoint, access_token=resp.access_token))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/test-login')
def test_login():
    if not app.debug:
        return 'sorry ;)'
    session['me'] = me = request.args.get('me')
    user = User.query.filter_by(uri=me).first()
    if not user:
        db.session.add(User(uri=me, micropub_uri=request.args.get('micropub_endpoint'), access_token=request.args.get('access_token')))
        db.session.commit()
    return redirect(url_for('index'))
