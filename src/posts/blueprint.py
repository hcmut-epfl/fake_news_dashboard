import json
import pandas as pd
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    Response
)
from flask_security import login_required
from src.ml.medical_classifier import MedicalClassifier
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
        medical_classifier = MedicalClassifier()
        text = request.form.get('text')
        url = request.form.get('url')
        time = request.form.get('time')
        comments_count = request.form.get('comments_count')
        reactions_count = request.form.get('reactions_count')
        shares_count = request.form.get('shares_count')
        comments = request.form.get('comments')
        true_news = request.form.get('true_news')
        true_news = (true_news == 'y') if isinstance(true_news, str) else true_news
        claim_info = request.form.get('claim_info')
        medical_news = medical_classifier.predict([text])[0] == 1
        group_name = request.form.get('group_name')
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
                claim_info=claim_info,
                medical_news=medical_news,
                group_name=group_name
            )
            db.session.add(post)
            db.session.commit()
            success = True
            message = 'Add post successfully'
        except Exception as e:
            print("Cannot add new post to the database.")
            print(e)
            success = False
            message = 'Cannot add new post to the database'
        
        # return redirect(url_for('posts.post_create', success=success, message=message))

    return render_template('html/post_create.html', form=form, success=success, message=message)

@posts.route('/')
def posts_list():
    q = request.args.get('q')
    filter_title = list()
    
    groups = db.session.query(Post.group_name).group_by(Post.group_name).order_by(Post.group_name).all()
    groups = [g[0] for g in groups]

    if q:
        posts = Post.query.filter(Post.text.contains(q))
    else:
        posts = Post.query.order_by(Post.time.desc())

    posts = Post.query

    filter = request.args.get('filter')
    if filter == "medical":
        posts = posts.filter(Post.medical_news == True)
        filter_title.append("Medical")
    elif filter == "non_medical":
        posts = posts.filter(Post.medical_news == False)
        filter_title.append("Not Medical")
    else:
        filter = ''
    
    type = request.args.get('type')
    if type == "fake":
        posts = posts.filter(Post.claim_info != '').filter(Post.true_news == False)
        filter_title.append("Fake")
    elif type == "true":
        posts = posts.filter(Post.claim_info != '').filter(Post.true_news == True)
        filter_title.append("True")
    else:
        type = ''

    group = request.args.get('group')
    if group:
        posts = posts.filter(Post.group_name == group)
        filter_title.append(group)
    else:
        group = ''

    filter_title = ', '.join(filter_title) if len(filter_title) > 0 else "All"

    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1 
    
    pages = posts.paginate(page=page, per_page=10)

    return render_template(
        'html/posts.html',
        posts=posts,
        pages=pages,
        filter=filter,
        groups=groups,
        group=group,
        type=type,
        filter_title=filter_title
    )

@posts.route('/stats')
def get_statistics():
    groups = db.session.query(Post.group_name).group_by(Post.group_name).order_by(Post.group_name).all()
    groups = [g[0] for g in groups]

    # Collect main statistics
    main_stats = dict()
    main_stats['medical_count'] = Post.query.filter(Post.medical_news == True).count()
    main_stats['non_medical_count'] = Post.query.filter(Post.medical_news == False).count()
    main_stats['true_count'] = Post.query.filter(Post.claim_info != '').filter(Post.true_news == True).count()
    main_stats['fake_count'] = Post.query.filter(Post.claim_info != '').filter(Post.true_news == False).count()
    main_stats['unverified_count'] = Post.query.filter(Post.claim_info == '').count()

    group_stats = []
    for group in groups:
        g = dict()
        g_posts = Post.query.filter(Post.group_name == group)
        g['name'] = group
        g['medical_count'] = g_posts.filter(Post.medical_news == True).count()
        g['non_medical_count'] = g_posts.filter(Post.medical_news == False).count()
        g['true_count'] = g_posts.filter(Post.claim_info != '').filter(Post.true_news == True).count()
        g['fake_count'] = g_posts.filter(Post.claim_info != '').filter(Post.true_news == False).count()
        g['unverified_count'] = g_posts.filter(Post.claim_info == '').count()
        group_stats.append(g)

    return render_template('html/statistics.html', main_stats=main_stats, group_stats=group_stats)

@posts.route('/<id>')
def post_detail(id):
    q = request.args.get('q')
    print("q:",q)
    if q:
        full_url = url_for('posts.posts_list', **request.args)
        return redirect(full_url)

    post = Post.query.filter(Post.id==id).first_or_404()
    return render_template('html/post_detail.html', post=post)

@posts.route('/edit_<id>', methods=['POST','GET'])
@login_required
def post_update(id):
    post = Post.query.filter(Post.id==id).first_or_404()
    if request.method == 'POST':
        form = PostForm(formdata=request.form, obj=post)
        form.populate_obj(post)
        db.session.commit()
        return redirect(f'fakenews/{id}')
    form = PostForm(obj=post)
    return render_template('html/edit.html', post=post, form=form)

@posts.route('/batch_upload', methods=['POST', 'GET'])
@login_required
def post_batch_upload():
    success = False
    message = ''
    if request.method == 'POST':
        try:
            # Encoding the file
            fp = request.files['file']
            bytes = fp.read()
            uni = bytes.decode('utf-8')
            d = json.loads(uni)

            fl = request.files['label']
            labels = pd.read_csv(fl)
            print(labels)

            model = MedicalClassifier()
            group_name = request.form.get('group_name')
            
            for post in d:
                post_dict = dict()
                post_dict['text'] = post['text']
                post_dict['url'] = post['post_url']
                post_dict['time'] = post['time']
                post_dict['reactions_count'] = post['info']['reaction_count']
                post_dict['comments_count'] = post['info']['comments']
                post_dict['shares_count'] = post['info']['shares']
                post_dict['comments'] = post['comments_full']

                temp_label = labels[labels['post_id'] == post['post_id']]
                if len(temp_label) > 0:
                    post_dict['medical_news'] = temp_label.iloc[0]
                else:
                    post_dict['medical_news'] = model.predict([post_dict['text']])[0] == 1
                post_dict['true_news'] = False
                post_dict['claim_info'] = ''
                post_dict['group_name'] = group_name.title()
                post = Post(**post_dict)
                db.session.add(post)
        except Exception as e:
            print(e)
            message = 'Fail during import.'
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            message = "Cannot add new post to the database."
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
    df = df[df['medical_news'] & (df['claim_info'] != '')].drop(['medical_news'], axis=1)
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
    df = df[df['medical_news'] & (df['claim_info'] != '')].drop(['medical_news'], axis=1)
    json_content = df.to_json(orient='records')
    response = Response(u'\uFEFF'.encode('utf-8') + bytes(json_content, 'utf-8'), mimetype='text/json')
    response.headers.set("Content-Disposition",
                        "attachment",
                        filename='news.json')
    return response