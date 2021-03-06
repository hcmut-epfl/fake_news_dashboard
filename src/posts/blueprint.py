from argparse import Namespace
import json
from bson import ObjectId
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
from src.posts.forms import PostForm
from src.app import db
import unidecode
 
def remove_accent(text):
    return unidecode.unidecode(text)

posts = Blueprint(
    'posts',
    __name__,
    template_folder='templates',
    static_folder='./static'
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
        page_id = request.form.get('page_id')
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
                page_id=page_id
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
    if q is not None:
        q = remove_accent(q)
    filter_title = list()
    
    groups = db.fbpost.distinct('page_id')
    all_filters = {}

    if q:
        all_filters["text"] = {"$regex": q}

    filter = request.args.get('filter')
    if filter == "medical":
        filter_title.append("Medical")
        all_filters["is_medical"] = True
    elif filter == "non_medical":
        filter_title.append("Not Medical")
        all_filters["is_medical"] = False
    else:
        filter = ''
    
    type = request.args.get('type')
    if type == "fake":
        filter_title.append("Fake")
        all_filters["is_fakenew"] = True
    elif type == "true":
        filter_title.append("True")
        all_filters["is_fakenew"] = False
    elif type == "unverified":
        all_filters["is_fakenew"] = {"$exists": False}
        type = 'unverified'
    else:
        type = ''

    group = request.args.get('group')
    if group:
        filter_title.append(group)
        all_filters["page_id"] = group
    else:
        group = ''

    filter_title = ', '.join(filter_title) if len(filter_title) > 0 else "All"

    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1 

    p_count = int(db.fbpost.count_documents(all_filters) / 10)
    if page <= 4 or page >= p_count - 3:
        iter_pages = [1, 2, 3, 4, 5, None, p_count - 4, p_count - 3, p_count - 2, p_count - 1, p_count]
    else:
        iter_pages = [1, None, page - 2, page - 1, page, page + 1, page + 2, None, p_count - 1, p_count]
    pages = Namespace(
        has_prev=(page > 1),
        has_next=(page != p_count),
        iter_pages=iter_pages,
    )
    print(all_filters)
    posts = list(db.fbpost.aggregate([
            { "$match": all_filters },
            { "$sort": {"is_verify_fakenew": -1}},
            { "$skip": 10 * page },  # No. of documents to skip (Should be `0` for Page - 1)
            { "$limit": 12 }  # No. of documents to be displayed on your webpage
        ]))

    return render_template(
        'html/posts.html',
        posts=posts,
        pages=pages,
        cur_page=page,
        filter=filter,
        groups=groups,
        group=group,
        type=type,
        filter_title=filter_title
    )

@posts.route('/stats')
def get_statistics():

    groups = db.fbpost.distinct('page_id')
    
    main_stats = {
        'medical_news_count': db.fbpost.count_documents({'is_medical': True, 'type_post': {'$nin': [0, 2]}}),
        'confirmed_medical_count': db.fbpost.count_documents({'is_medical': True, 'type_post': {'$exists': True, '$eq': 1}}),
        'medical_count': db.fbpost.count_documents({'is_medical': True}),
        'total_post_crawled': db.fbpost.count_documents({}),
        'true_count': db.fbpost.count_documents({'is_medical': True, 'is_fakenew': False, 'type_post': {'$nin': [0, 2]}}),
        'fake_count': db.fbpost.count_documents({'is_medical': True, 'is_fakenew': True, 'type_post': {'$nin': [0, 2]}}),
        'verified_count': db.fbpost.count_documents({
                'is_medical': True,
                'is_fakenew': {"$exists": True},
                'is_verify_fakenew': True,
                'type_post': {'$nin': [0, 2]}
            })
    }
    group_stats = list()
    
    for group in groups:
        gd = {
            'name': group,
            'medical_count': db.fbpost.count_documents({'page_id': group, 'is_medical': True, 'type_post': {'$nin': [0, 2]}}),
            'true_count': db.fbpost.count_documents({'page_id': group, 'is_medical': True, 'is_fakenew': False, 'type_post': {'$nin': [0, 2]}}),
            'fake_count': db.fbpost.count_documents({'page_id': group, 'is_medical': True, 'is_fakenew': True, 'type_post': {'$nin': [0, 2]}}),
            'verified_count': db.fbpost.count_documents({
                'page_id': group,
                'is_medical': True,
                'is_fakenew': {"$exists": True},
                'is_verify_fakenew': True,
                'type_post': {'$nin': [0, 2]}
            })
        }
        group_stats.append(gd)

    return render_template('html/statistics.html', main_stats=main_stats, group_stats=group_stats)

@posts.route('/<id>')
def post_detail(id):
    q = request.args.get('q')
    print("q:",q)
    if q:
        full_url = url_for('posts.posts_list', **request.args)
        return redirect(full_url)
    if id == 'favicon.ico':
        return render_template('index.html')
    oid = ObjectId(id)
    post = db.fbpost.find_one({"_id": oid})
    next_id = f'{(int(id, 16) + 1):x}'
    comments = list(db.fbcmt.find({"post_id": post["post_id"]}))

    return render_template('html/post_detail.html', post=post, comments=comments, next_id=next_id)

@posts.route('/edit_<id>', methods=['POST','GET'])
@login_required
def post_update(id):
    oid = ObjectId(id)
    post = db.fbpost.find_one({"_id": oid})
    print(post)
    if request.method == 'POST':
        form = PostForm(obj=post)
        form.populate_obj(post)
        print(post)
        return redirect(f'/{id}')
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

            labels = None
            try:
                fl = request.files['label']
                labels = pd.read_csv(fl)
            except:
                pass

            model = MedicalClassifier()
            page_id = request.form.get('page_id')
            
            for post in d:
                post_dict = dict()
                post_dict['text'] = post['text']
                post_dict['url'] = post['post_url']
                post_dict['time'] = post['info']['time']
                post_dict['reactions_count'] = post['info']['reaction_count']
                post_dict['comments_count'] = post['info']['comments']
                post_dict['shares_count'] = post['info']['shares']
                post_dict['comments'] = post['comments_full']

                if labels is not None and 'post_id' in post and 'post_id' in labels.columns:
                    temp_label = labels[labels['post_id'] == post['post_id']]
                else:
                    temp_label = []
                if len(temp_label) > 0:
                    post_dict['medical_news'] = temp_label.iloc[0]
                else:
                    post_dict['medical_news'] = model.predict([post_dict['text']])[0] == 1

                post_dict['true_news'] = False
                post_dict['claim_info'] = ''
                post_dict['page_id'] = page_id.title()
                post = Post(**post_dict)
                db.session.add(post)
        except Exception as e:
            message = 'Fail during import.'
            raise(e)
        try:
            db.session.commit()
            success = True
            message = 'Successfully uploaded!'
        except Exception as e:
            message = "Cannot add new post to the database."
            raise(e)
            
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


@posts.route('/label_medical', methods=['GET', 'POST'])
def medical_label():
    if request.method == 'POST':
        multi_dict = request.form
        for key in multi_dict:
            fact, id = key.split('_')
            oid = ObjectId(id)
            try:
                result = db.fbpost.update_one(
                    {"_id": oid},
                    { "$set": { 
                            "is_medical": (fact == 'true'),
                            "is_verify": True
                        }
                    }
                )
            except Exception as e:
                raise(e)
    posts = db.fbpost.aggregate([
            { "$match": {"is_verify": {"$ne": True}} },
            { "$sample": {"size": 50} }  # No. of documents to be displayed on your webpage
        ])
    return render_template('html/label_medical.html', posts=posts)

@posts.route('/label_question', methods=['GET', 'POST'])
def question_label():
    if request.method == 'POST':
        multi_dict = request.form
        for key in multi_dict:
            fact, id = key.split('_')
            oid = ObjectId(id)
            try:
                result = db.fbpost.update_one(
                    {"_id": oid},
                    { "$set": { 
                            "type_post": 1 if (fact == 'true') else 0,
                            "is_verify_type_post": True
                        }
                    }
                )
                print(db.post.find_one({"_id": oid}))
            except Exception as e:
                raise(e)
    posts = db.fbpost.aggregate([
            { "$match": {"is_verify_type_post": {"$ne": True}, "is_medical": True} },
            { "$sample": {"size": 50} }  # No. of documents to be displayed on your webpage
        ])
    return render_template('html/label_question.html', posts=posts)

@posts.route('/label_true_fake', methods=['GET', 'POST'])
def true_fake_label():
    if request.method == 'POST':
        multi_dict = request.form
        print(multi_dict)
        for key in multi_dict:
            fact, id = key.split('_')
            oid = ObjectId(id)
            try:
                result = db.fbpost.update_one(
                    {"_id": oid},
                    { "$set": { 
                            "is_fakenew":  (fact == 'false'),
                            "is_verify_fakenew": True
                        }
                    }
                )
                post = db.fbpost.find_one({"_id": oid})
            except Exception as e:
                raise(e)
    posts = db.fbpost.aggregate([
            { "$match": {"is_verify_fakenew": {"$ne": True}, "is_medical": True, "type_post": 1}},
            { "$sample": {"size": 50} }  # No. of documents to be displayed on your webpage
        ])
    return render_template('html/label_true_fake.html', posts=posts)