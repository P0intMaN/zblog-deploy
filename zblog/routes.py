from flask import render_template, flash, redirect, url_for, request, jsonify
from sqlalchemy import func
from zblog import app, db
from zblog.forms_template import RegForm, LoginForm, AddTagForm, RemovePostForm, ConfigurePostForm
from zblog.models import User, Post, Tag, PostMeta
from flask_login import login_required, login_user, current_user, logout_user
from werkzeug.urls import url_parse

@app.route('/') 
def home():
    title = 'Home'

    post_list = Post.query.order_by(Post.post_date.desc()).all()
    latest_post = post_list.pop(0)
    first_post = post_list[len(post_list)-1]
    popular_posts = PostMeta.query.order_by(PostMeta.likes.desc()).all()
    tags = Tag.query.all()

    return render_template('home_template.html', title=title, posts=post_list, latest_post=latest_post, first_post=first_post, popular_posts=popular_posts, tags=tags)

@app.route('/tags') 
def tags():
    title = 'Tags'
    tags = Tag.query.all()

    return render_template('tags_template.html', tags=tags, title=title)

@app.route('/profile')
@login_required 
def profile():
    title = 'Profile'
    user = current_user

    return render_template('profile_page_template.html', title=title, user=user)

@app.route('/admin', methods=['GET', 'POST']) 
def admin():
    title = 'Admin Page'

    user = current_user
    if user.email != 'admin@zblog.com':
        return '<h1>Unauthorized Access</h1>', 401

    form1 = AddTagForm()
    form2 = RemovePostForm()
    form3 = ConfigurePostForm()

    if form1.identifier.data == 'FORM1' and form1.validate_on_submit():
            tag = Tag.query.filter(func.lower(Tag.tag_name)==func.lower(form1.new_tag_name.data)).first()

            if tag:
                flash('Tag Already Exists! 🤕', 'danger')
            else:
                new_tag = form1.new_tag_name.data.lower()
                add_tag = Tag(tag_name=new_tag)
                db.session.add(add_tag)
                db.session.commit()

                flash('Tag Successfully Added! ✔️', 'success')

    elif form2.identifier.data == 'FORM2' and form2.validate_on_submit():
        post = Post.query.filter(func.lower(Post.title)==func.lower(form2.title.data)).first()
        
        if post:
            db.session.delete(post)
            db.session.commit()
            flash('Removed Post Succesfully! ✔️', 'success')
        else:
            flash('No Such Post Exists! 🤕', 'danger')
    
    elif form3.identifier.data == 'FORM3' and form3.validate_on_submit():
        post = Post.query.filter(func.lower(Post.title)==func.lower(form3.post_title.data)).first()
        if post:
            flash('A Post Already Exists! 🤕', 'danger')
        
        tag_list = form3.tags.data.split(',')
        existing_tag_objects = Tag.query.all()
        existing_tags = [tag.tag_name for tag in existing_tag_objects]
        found_tag = False
        wrong_tags = []
        for tag in tag_list:
            if tag not in existing_tags:
                wrong_tags.append(tag)
                found_tag = True
        
        if wrong_tags:
            flash(f'Hmm.. Seems Like There Are Some New Tags: {wrong_tags}. Maybe Consider Adding Them First? 🤔', 'danger')

        if not post and not found_tag:
            p_title = form3.post_title.data.lower()
            p_url = '-'.join(p_title.split(' '))

            post_obj = Post(title=p_title)
            post_url = PostMeta(url=p_url, post=post_obj)

            db.session.add_all([post_obj,post_url])
            db.session.commit()
            

            for tag in tag_list:
                tag_obj = Tag.query.filter_by(tag_name=tag).first()
                tag_obj.posts.append(post_obj)
            db.session.commit()

            flash('Configuration Added Successfully! ✔️', 'success')

    return render_template('admin_template.html', title=title, form1=form1, form2=form2, form3=form3)
    
@app.route('/join', methods=['GET','POST']) 
def join():
    title = 'Join Community'

    # instantiating the form class
    form = RegForm()

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            flash('This email is already in use! Maybe try logging in? 🤖', 'danger')
        
        else:
            new_user = User(username=form.username.data, email=form.email.data)
            new_user.hash_and_set_password(form.password.data)
            print(new_user.password)
            db.session.add(new_user)
            db.session.commit()

            flash('You are all set! Login to continue!', 'success')

            return redirect(url_for('login'))
        
    return render_template('register_template.html', title=title, form=form)
    
@app.route('/login', methods=['GET', 'POST']) 
def login():
    title = 'Login'

    # instantiating the form class
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None or not user.check_hashed_password(form.password.data):
            flash('Snap! Login Unsuccessful 😬', 'danger')
        
        else:
            flash('Thank you for joining us! You have unlocked the ability to bookmark and like the posts 🔥', 'success')
            login_user(user, remember=form.rem_me.data)
            next_page = request.args.get('next')

            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            
            return redirect(next_page)

    return render_template('login_template.html', title=title, form=form)

@app.route('/tags/<tagname>')
def tag(tagname):
    title = f'Blogs for {tagname.capitalize()}'
    tag = Tag.query.filter_by(tag_name=tagname).first()
    posts = tag.posts
    return render_template('tag_page_template.html', title=title, tagname=tagname, posts=posts)

@app.route('/blog/<url_slug>')
def blog(url_slug):
    post_meta = PostMeta.query.filter_by(url=url_slug).first()
    post = post_meta.post
    tags = post.tags_associated
    likes = post.meta.likes
    user = current_user

    title = post.title.lower()
    return render_template(f'{url_slug}.html', title=title, post=post, likes=likes, tags=tags, user=user)

@app.route('/logout')
def logout():
    logout_user()
    flash('You are now logged out!', 'primary')
    return redirect(url_for('home'))

@app.route('/remove_like/<post_title>')
def remove_like(post_title):
    post = Post.query.filter(func.lower(Post.title)==func.lower(post_title)).first()
    user = current_user

    post.meta.likes -=1
    post.liked_by.remove(user)
    db.session.commit()

    return jsonify(post.meta.likes)

@app.route('/add_like/<post_title>')
def add_like(post_title):
    post = Post.query.filter(func.lower(Post.title)==func.lower(post_title)).first()
    user = current_user

    post.liked_by.append(user)
    post.meta.likes +=1
    db.session.commit()

    return jsonify(post.meta.likes)

@app.route('/remove_bookmark/<post_title>')
def remove_bookmark(post_title):
    post = Post.query.filter(func.lower(Post.title)==func.lower(post_title)).first()
    user = current_user

    post.bookmarked_by.remove(user)
    db.session.commit()

    return 'OK', 200

@app.route('/add_bookmark/<post_title>')
def add_bookmark(post_title):
    post = Post.query.filter(func.lower(Post.title)==func.lower(post_title)).first()
    user = current_user

    post.bookmarked_by.append(user)
    db.session.commit()

    return 'OK', 200
