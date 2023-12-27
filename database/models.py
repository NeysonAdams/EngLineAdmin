from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user

from datetime import datetime, date
import random
import string

db = SQLAlchemy()

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

user_cources_pased = db.Table(
    'user_cources_pased',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('cource_id', db.Integer(), db.ForeignKey('cource.id'))
)

user_cources_in_progress = db.Table(
    'user_cources_in_progress',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('cource_id', db.Integer(), db.ForeignKey('cource.id'))
)

exec_in_lesson = db.Table(
    'exec_in_lesson',
    db.Column('lesson_id', db.Integer(), db.ForeignKey('lesson.id')),
    db.Column('exesizes', db.Integer(), db.ForeignKey('exesize.id'))
)

user_dictionary = db.Table(
    'user_dictionary',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('word_id', db.Integer(), db.ForeignKey('englishword.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(255))
    facebook_id = db.Column(db.String(255))
    img_url = db.Column(db.String(255))
    phone_number = db.Column(db.String(255))
    name = db.Column(db.String(255), nullable=False)
    login = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))
    level = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    fs_uniquifier = db.Column(db.String(64), unique=True)

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    cources_pased = db.relationship('Cource', secondary=user_cources_pased,
                                 backref=db.backref('cource_passed', lazy='dynamic'))

    cources_in_progress = db.relationship('Cource', secondary=user_cources_in_progress,
                                    backref=db.backref('cource_inprogress', lazy='dynamic'))

    dictionary = db.relationship('Englishword', secondary=user_dictionary,
                                    backref=db.backref('user_dictionary', lazy='dynamic'))

    def __str__(self):
        return self.email

    @property
    def serialize(self):
        return {
            "id": self.id,
            "google_id": self.google_id,
            "facebook_id": self.facebook_id,
            "name": self.name,
            "login": self.login,
            "email": self.email,
            "level": self.level,
            "img_url": self.img_url,
        }

    def auth_setialization(self, token, refresh_token):
        return {
            "id": self.id,
            "google_id": self.google_id,
            "facebook_id": self.facebook_id,
            "name": self.name,
            "login": self.login,
            "email": self.email,
            "level": self.level,
            "img_url": self.img_url,
            "access_token": token,
            "refresh_token": refresh_token
        }

class Cource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    level = db.Column(db.String(255))
    discription = db.Column(db.String(255))
    price = db.Column(db.String(255))
    img_url = db.Column(db.String(255))
    is_buy = db.Column(db.Boolean())

    lessons = db.relationship('Lesson', backref='author', lazy=True)

    def __repr__(self):
        return self.title

    @property
    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "level": self.level,
            "discription": self.discription,
            "price": self.price,
            "img_url": self.img_url,
            "lessons": [i.serialize for i in self.lessons]
        }


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    lesson_name = db.Column(db.String(255))
    video_link = db.Column(db.String(255))
    lesson_description = db.Column(db.String(255))
    presentation_link = db.Column(db.String(255))
    slides_link = db.Column(db.String(255))

    cource_id = db.Column(db.Integer, db.ForeignKey('cource.id'), nullable=False)
    cource = db.relationship('Cource', backref=db.backref('lesson_coure', lazy='dynamic'))
    exesizes = db.relationship('Exesize', secondary=exec_in_lesson,
                            backref=db.backref('exec', lazy='dynamic'))

    def __repr__(self):
        return f"Name : {self.lesson_name}, Course : {self.cource.title})"

    @property
    def serialize(self):
        return {
            "id": self.id,
            "lesson_name": self.lesson_name,
            "video_link": self.video_link,
            "lesson_description": self.lesson_description,
            "presentation_link": self.presentation_link,
            "slides_link": self.slides_link,
            "exesizes" : [i.serialize for i in self.exesizes]
        }

words_in_exes = db.Table(
    'words_in_exes',
    db.Column('exesize_id', db.Integer(), db.ForeignKey('exesize.id')),
    db.Column('englishword_id', db.Integer(), db.ForeignKey('englishword.id'))
)

class Exesize(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    lesson_name = db.Column(db.String(255))
    type = db.Column(db.String(255))
    level =db.Column(db.Integer, nullable=False)

    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=True)
    questions_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=True)
    input_id = db.Column(db.Integer, db.ForeignKey('inputquestion.id'), nullable=True)
    audio_id = db.Column(db.Integer, db.ForeignKey('audioquestion.id'), nullable=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videoquestion.id'), nullable=True)

    lesson = db.relationship('Lesson', backref=db.backref('exec', lazy='dynamic'))
    question = db.relationship('Question', backref=db.backref('eq', lazy='dynamic'))
    input = db.relationship('Inputquestion', backref=db.backref('ei', lazy='dynamic'))
    audio = db.relationship('Audioquestion', backref=db.backref('ea', lazy='dynamic'))
    video = db.relationship('Videoquestion', backref=db.backref('ev', lazy='dynamic'))

    words = db.relationship('Englishword', secondary=words_in_exes,
                               backref=db.backref('exec', lazy='dynamic'))

    def __repr__(self):
        return f"Name : {self.lesson_name}, Type : {self.type})"

    @property
    def serialize(self):
        return {
            "id": self.id,
            "lesson_name": self.lesson_name,
            "type": self.type,
            "video_url": self.video_url,
            "question": self.question.serialize_lesson,
            "inputquestion":self.input.serialize,
            "audio": self.audio.serialize,
            "video": self.video.serialize,
            "words": [w.serialize for w in self.words]
        }

class Videoquestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255))
    video_url=db.Column(db.String(255))
    answer = db.Column(db.String(255))
    level = db.Column(db.Integer)

    exesize = db.relationship('Exesize', backref='vexesize', lazy=True)

    def __repr__(self):
        return f"({self.level}){self.question})"

    @property
    def serialize(self):
        return {
            "id": self.id,
            "question": self.question,
            "video_url": self.video_url,
            "level": self.level
        }

class Audioquestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255))
    audio_url=db.Column(db.String(255))
    answer = db.Column(db.String(255))
    level = db.Column(db.Integer)

    exesize = db.relationship('Exesize', backref='aexesize', lazy=True)

    def __repr__(self):
        return f"({self.level}){self.question})"

    @property
    def serialize(self):
        return {
            "id": self.id,
            "question": self.question,
            "audio_url": self.audio_url,
            "level": self.level
        }

class Inputquestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255))
    answer = db.Column(db.String(255))
    level = db.Column(db.Integer)

    exesize = db.relationship('Exesize', backref='iexesize', lazy=True)

    def __repr__(self):
        return f"({self.level}){self.question})"

    @property
    def serialize(self):
        return {
            "id": self.id,
            "question": self.question,
            "level": self.level
        }


class Question (db.Model):
    id = db.Column(db.Integer, primary_key=True)

    question = db.Column(db.String(255))
    var1 = db.Column(db.String(255))
    var2 = db.Column(db.String(255))
    var3 = db.Column(db.String(255))
    var4 = db.Column(db.String(255))

    right_var = db.Column(db.Integer)
    var_dif = db.Column(db.Integer)

    exesize = db.relationship('Exesize', backref='exesize', lazy=True)

    def __repr__(self):
        return f"({self.var_dif}){self.question})"

    @property
    def serialize(self):
        return {
            "id": self.id,
            "question": self.question,
            "var1": self.var1,
            "var2": self.var2,
            "var3": self.var3,
            "var4": self.var4,
            "right_var": self.right_var,
            "var_dif": self.var_dif
        }

    @property
    def serialize_lesson(self):
        return {
            "id": self.id,
            "question": self.question,
            "test_answers": [self.var1,
                             self.var2,
                             self.var3,
                             self.var4],
            "right_var": self.right_var,
            "var_dif": self.var_dif
        }

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    discription = db.Column(db.String(255))
    price = db.Column(db.String(255))
    is_active = db.Column(db.Boolean())
    img_url = db.Column(db.String(255))

    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "discription": self.discription,
            "is_active": self.is_active,
            "img_url": self.img_url
        }


dictionaty_releations = db.Table(
    'dictionaty_releations',
    db.Column('dictionary_id', db.Integer, db.ForeignKey('dictionary.id')),
    db.Column('englishword_id', db.Integer, db.ForeignKey('englishword.id'))
)



class Englishword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255), unique=True, nullable=False)

    translate = db.relationship('Russianword', backref='words', lazy=True)

    def __repr__(self):
        return self.word

    @property
    def serialize(self):
        return {
            "id": self.id,
            "word": self.word,
            "translate": [i.serialize for i in self.translate]
        }

class Russianword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255), unique=True, nullable=False)
    englishWord_id = db.Column(db.Integer, db.ForeignKey('englishword.id'), nullable=True)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "word": self.word
        }

class Dictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name=db.Column(db.String(255), unique=True, nullable=False)

    words = db.relationship('Englishword', secondary=dictionaty_releations,
                            backref=db.backref('dictionary', lazy='dynamic'),
                            primaryjoin=(dictionaty_releations.c.dictionary_id == id),
                            secondaryjoin=(dictionaty_releations.c.englishword_id == Englishword.id),
                            lazy='dynamic')

    def serialize(self, page, page_length):

        word_lens = []
        is_last_page=False

        for i in range(page-1, page*page_length):
            if i>= len(self.words):
                is_last_page=True
                break
            word_lens.append(self.words[i].serialize)


        return {
            "name": self.name,
            "words": word_lens,
            "is_last_page": is_last_page
        }




