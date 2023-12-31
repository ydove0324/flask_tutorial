import functools

from flask import (Flask,Blueprint,g,render_template,request,url_for,flash,redirect)

from werkzeug.exceptions import abort

from flaskr.db import get_db

from flaskr.auth import login_required

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html',posts=posts)


@bp.route("/create", methods = ('GET','POST'))
@login_required
def create():
    print(request.method)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        if not title:
            error = 'Title is required. '

        if error is None:
            db = get_db()
            db.execute(
                'INSERT INTO post (title,body,author_id)'
                ' VALUES (?,?,?)',
                (title,body,g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
        flash(error)
    return render_template('blog/create.html')

def get_post(id):
    db = get_db()
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()
    if post is None:
        abort(404,f"{id} is Invalid")
    elif post["author_id"] != g.user['id']:
        abort(403)
    return post

@bp.route("/<int:id>/update",methods=("GET","POST"))
@login_required
def update(id):
    post = get_post(id)
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        error = None
        if title is None:
            error = "Title is required"
        if error is None:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template("blog/update.html",post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))