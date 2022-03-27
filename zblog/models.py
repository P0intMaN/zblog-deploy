from zblog import db
from datetime import datetime
from flask_login import UserMixin
from zblog import login
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

user_bookmarks_table = db.Table('user_posts',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
    )

user_likes_table = db.Table('user_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

tags_table = db.Table('post_tags',
    db.Column('tags_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(128), nullable=False)
    bookmarked_posts = db.relationship('Post', secondary=user_bookmarks_table, backref='bookmarked_by')
    liked_posts = db.relationship('Post', secondary=user_likes_table, backref='liked_by')

    def __repr__(self):
        return(f'<User: {self.email}>')

    def hash_and_set_password(self, password):
        self.password = generate_password_hash(password)

    def check_hashed_password(self, password):
        return check_password_hash(self.password, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    post_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    #likes = db.Column(db.Integer, default=0)
    meta = db.relationship('PostMeta', backref='post', cascade="all, delete", uselist=False)

    def __repr__(self):
        return(f'<Post: {self.title}>')

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(20))
    posts = db.relationship('Post', secondary=tags_table, backref='tags_associated')

    def __repr__(self):
        return(f'<Tag: {self.tag_name}>')

class PostMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(150))
    likes = db.Column(db.Integer, default=0)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
