import json
import pandas as pd
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    send_file,
    Response
)
from flask_security import login_required
from src.model.post import Post
from src.posts.forms import PostForm
from src.app import db

posts = Blueprint(
    'posts',
    __name__,
    template_folder='templates'
)

@posts.route('/create', methods=['POST', 'GET'])
@login_required
def post_create():
    form = PostForm()
    success = False
    message = ''
    if request.method == 'POST':
        text = request.form.get('text')
        url = request.form.get('url')
        time = request.form.get('time')
        comments_count = request.form.get('comments_count')
        reactions_count = request.form.get('reactions_count')
        shares_count = request.form.get('shares_count')
        comments = request.form.get('comments')
        true_news = request.form.get('true_news')
        claim_info = request.form.get('claim_info')

        try:
            post = Post(
                text=text,
                url=url,
                time=time,
                comments_count=comments_count,
                reactions_count=reactions_count,
                shares_count=shares_count,
                comments=comments,
                true_news=true_news,
                claim_info=claim_info
            )
            db.session.add(post)
            db.session.commit()
        except:
            print("Cannot add new post to the database.")
        
        success = True
        message = 'Add post successfully'
        
        return redirect(url_for('posts.post_create'))

    return render_template('html/post_create.html', form=form, success=success, message=message)

@posts.route('/')
def posts_list():
    q = request.args.get('q')
    print("q:",q)
    if q:
        posts = Post.query.filter(Post.text.contains(q) |
                Post.shortened_text.contains(q))
    else:
        posts = Post.query.order_by(Post.time.desc())

    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1 
    
    pages = posts.paginate(page=page, per_page=10)

    return render_template('html/posts.html', posts=posts, pages=pages)

@posts.route('/<id>')
def post_detail(id):
    q = request.args.get('q')
    print("q:",q)
    if q:
        full_url = url_for('posts.posts_list', **request.args)
        return redirect(full_url)

    post = Post.query.filter(Post.id==id).first_or_404()
    return render_template('html/post_detail.html', post=post)

@posts.route('/<id>/edit', methods=['POST','GET'])
@login_required
def post_update(id):
    post = Post.query.filter(Post.id==id).first_or_404()
    if request.method == 'POST':
        form = PostForm(formdata=request.form, obj=post)
        form.populate_obj(post)
        db.session.commit()
        return redirect(url_for('posts.post_detail', id=post.id))
    form = PostForm(obj=post)
    return render_template('html/edit.html', post=post, form=form)

@posts.route('/batch_upload', methods=['POST', 'GET'])
@login_required
def post_batch_upload():
    success = False
    message = ''
    if request.method == 'POST':
        f = request.files['file']
        bytes = f.read()
        uni = bytes.decode('utf-8')
        d = json.loads(uni)
        for post in d:
            post_dict = dict()
            post_dict['text'] = post['text']
            post_dict['url'] = post['post_url']
            post_dict['time'] = post['time']
            post_dict['reactions_count'] = post['info']['reaction_count']
            post_dict['comments_count'] = post['info']['comments']
            post_dict['shares_count'] = post['info']['shares']
            post_dict['comments'] = post['comments_full']
            post_dict['true_news'] = None
            post_dict['claim_info'] = ''
            try:
                post = Post(**post_dict)
                db.session.add(post)
                db.session.commit()
            except:
                print("Cannot add new post to the database.")
        success = True
        message = 'Successfully uploaded!'
            
    return render_template('html/post_batch_upload.html', success=success, message=message)

@posts.route('/export', methods=['GET'])
@login_required
def export():
    return render_template('html/export.html')

@posts.route('/export/csv', methods=['GET'])
@login_required
def export_csv():
    posts = Post.query.all()
    post_dict = [p.__dict__ for p in posts]
    df = pd.DataFrame(post_dict).drop(['_sa_instance_state', 'shortened_text'], axis=1)
    csv_content = df.to_csv(index=False)
    response = Response(u'\uFEFF'.encode('utf-8') + bytes(csv_content, 'utf-8'), mimetype='text/csv')
    response.headers.set("Content-Disposition",
                        "attachment",
                        filename='news.csv')
    return response

@posts.route('/export/json', methods=['GET'])
@login_required
def export_json():
    posts = Post.query.all()
    post_dict = [p.__dict__ for p in posts]
    df = pd.DataFrame(post_dict).drop(['_sa_instance_state', 'shortened_text'], axis=1)
    json_content = df.to_json(orient='records')
    response = Response(u'\uFEFF'.encode('utf-8') + bytes(json_content, 'utf-8'), mimetype='text/json')
    response.headers.set("Content-Disposition",
                        "attachment",
                        filename='news.json')
    return response