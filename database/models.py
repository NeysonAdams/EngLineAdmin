from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import TypeDecorator, String
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user

from datetime import datetime, date
import random
import string
from sqlalchemy.dialects.postgresql import ARRAY

from config import ENG_LEVELS
from mobile_api.aicomponent import generate_text
import json

db = SQLAlchemy()

# Define models
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

promo_users = db.Table('promo_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('promo_id', db.Integer, db.ForeignKey('promo.id'), primary_key=True)
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

users_exec_stat = db.Table(
    'users_exec_stat',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('exesizes', db.Integer(), db.ForeignKey('exesize.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)

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
    experiance = db.Column(db.Integer)
    current_level = db.Column(db.Integer)

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    cources_pased = db.relationship('Cource', secondary=user_cources_pased,
                                 backref=db.backref('cource_passed', lazy='dynamic'))

    cources_in_progress = db.relationship('Cource', secondary=user_cources_in_progress,
                                    backref=db.backref('cource_inprogress', lazy='dynamic'))

    dictionary = db.relationship('Englishword', secondary=user_dictionary,
                                    backref=db.backref('user_dictionary', lazy='dynamic'))

    payment = db.relationship('Payments', backref='payment_user', lazy=True)

    speach_lesson = db.relationship('LessonSchedler', backref='schedler_user', lazy=True)

    subscription = db.relationship('Subscription', backref='user_subscription', uselist=False)

    def __str__(self):
        return self.email

    # Serialization methods
    @property
    def admin_serialize(self):
        return {
            "id": self.id,
            "google_id": self.google_id,
            "facebook_id": self.facebook_id,
            "name": self.name,
            "login": self.login,
            "email": self.email,
            "level": self.level,
            "img_url": self.img_url,
            "phone_number": self.phone_number,
        }

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

    def auth_serialization(self, token, refresh_token, subscription, isRegistrated=True):
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
            "refresh_token": refresh_token,
            "isRegistrated": isRegistrated,
            "subscription": {} if not subscription else subscription.serialize
        }

class UserStatistic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    days = db.Column(db.Integer)
    hours = db.Column(db.Integer)
    words = db.Column(db.String)
    exesizes = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def serialize(self):
        words = str(self.words)
        words = words.split(',')
        ex = str(self.exesizes)
        ex = ex.split(',')
        return {
            "days":self.days,
            "hours":self.hours,
            "words":len(words),
            "exesizes":len(ex)
        }

class Cource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    level = db.Column(db.String(255))
    discription = db.Column(db.String(255))
    img_url = db.Column(db.String(255))
    is_buy = db.Column(db.Boolean())
    reiting = db.Column(db.Float, nullable=False)
    lenguage = db.Column(db.String(255))

    lessons = db.relationship('Lesson', backref='author', lazy=True)

    price = db.Column(db.Integer, db.ForeignKey('billing.id'), nullable=False)

    def __repr__(self):
        return self.title + " :: " + self.lenguage


    def serialize(self, user):

        billing = Billing.query.filter(Billing.id==self.price).first()

        return {
            "id": self.id,
            "title": self.title,
            "level": self.level,
            "discription": self.discription,
            "price": billing.serialize,
            "img_url": self.img_url,
            "is_buy":self in user.cources_in_progress,
            "reiting":self.reiting,
            "lessons": [i.serialize for i in self.lessons]
        }


    def data(self, user):

        billing = Billing.query.filter(Billing.id==self.price).first()
        return {
            "id": self.id,
            "title": self.title,
            "level": self.level,
            "discription": self.discription,
            "price": billing.serialize,
            "img_url": self.img_url,
            "is_buy":self in user.cources_in_progress,
            "reiting":self.reiting
        }

    def serialize_header(self, user):

        billing = Billing.query.filter(Billing.id==self.price).first()
        return {
            "id": self.id,
            "title": self.title,
            "level": self.level,
            "price": billing.serialize,
            "img_url": self.img_url,
            "is_buy":self in user.cources_in_progress,
            "reiting":self.reiting,
            "count": len(self.lessons)
        }

    def serialize_lesons(self, user):
        billing = Billing.query.filter(Billing.id==self.price).first()
        return {
            "id": self.id,
            "title": self.title,
            "level": self.level,
            "discription": self.discription,
            "price": billing.serialize,
            "img_url": self.img_url,
            "is_buy":self in user.cources_in_progress,
            "reiting":self.reiting,
            "lessons": [i.serialize_title for i in self.lessons]
        }


class Cstat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.Integer, nullable=False)

    cource_id = db.Column(db.Integer, db.ForeignKey('cource.id'), nullable=False)
    user_id =  db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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


    def serialize_score(self, score):
        return {
            "id": self.id,
            "lesson_name": self.lesson_name,
            "video_link": self.video_link,
            "lesson_description": self.lesson_description,
            "presentation_link": self.presentation_link,
            "slides_link": self.slides_link,
            "exesizes" : [i.serialize for i in self.exesizes],
            "score":score,
        }

    @property
    def serialize(self):
        return {
            "id": self.id,
            "lesson_name": self.lesson_name,
            "video_link": self.video_link,
            "lesson_description": self.lesson_description,
            "presentation_link": self.presentation_link,
            "slides_link": self.slides_link,
            "exesizes": [i.serialize for i in self.exesizes]
        }

    @property
    def serialize_title(self):
        return {
            "id": self.id,
            "lesson_name": self.lesson_name
        }

words_in_exes = db.Table(
    'words_in_exes',
    db.Column('exesize_id', db.Integer(), db.ForeignKey('exesize.id')),
    db.Column('englishword_id', db.Integer(), db.ForeignKey('englishword.id'))
)

exesizes_table = db.Table(
    'exesizes_table',
    db.Column('exesesizes_id', db.Integer(), db.ForeignKey('exesesizes.id'), primary_key=True),
    db.Column('exesize_id', db.Integer(), db.ForeignKey('exesize.id'), primary_key=True)
)

class Exesesizes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    img_url = db.Column(db.String(255))
    type = db.Column(db.String(255))
    lenguage = db.Column(db.String(255))
    level = db.Column(db.Integer)
    exesize =db.relationship('Exesize', secondary=exesizes_table,
                               backref=db.backref('exesize_list', lazy='dynamic'))

    def serialize(self, subscription):
        return {
            "id": self.id,
            "name": self.name,
            'img_link': self.img_url,
            'type':self.type,
            'level':self.level,
            "exesize": [i.serialize for i in self.exesize],
            "subscription": {} if not subscription else subscription.serialize

        }

    @property
    def serialize_header(self):
        return {
            "id": self.id,
            "name": self.name,
            'img_link': self.img_url,
            'type': self.type,
            'level': self.level,
            'count': len(self.exesize)
        }

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

    word_ex_id = db.Column(db.Integer, db.ForeignKey('wordexecesize.id'), nullable=True)
    wordexecesize = db.relationship('Wordexecesize', backref='wexesizes')

    lesson = db.relationship('Lesson', backref=db.backref('exec', lazy='dynamic'))
    question = db.relationship('Question', backref=db.backref('eq', lazy='dynamic'))
    input = db.relationship('Inputquestion', backref=db.backref('ei', lazy='dynamic'))
    audio = db.relationship('Audioquestion', backref=db.backref('ea', lazy='dynamic'))
    video = db.relationship('Videoquestion', backref=db.backref('ev', lazy='dynamic'))
    translation = db.Column(db.Integer, nullable=True)

    words = db.relationship('Englishword', secondary=words_in_exes,
                               backref=db.backref('exec', lazy='dynamic'))

    def __repr__(self):
        return f"{self.id} ::Name : {self.lesson_name}, Type : {self.type})"

    @property
    def serialize(self):
        type = self.type
        if self.type == "record_question":
            if self.input is not None:
                type = "input_question"
            if self.audio is not None:
                type = "audio_question"
            if self.video is not None:
                type = "video_question"

        if type =="test_question":
            return {
            "id": self.id,
            "lesson_name": self.lesson_name,
            "type": type,
            "question": self.question.serialize_lesson if self.question is not None else None
            }
        if type == "input_question":
            return {
                "id": self.id,
                "lesson_name": self.lesson_name,
                "type": type,
                "inputquestion":self.input.serialize if self.input is not None else None
            }
        if type == "audio_question":
            return {
                "id": self.id,
                "lesson_name": self.lesson_name,
                "type": type,
                "audio": self.audio.serialize if self.audio is not None else None
            }
        if type == "video_question":
            return {
                "id": self.id,
                "lesson_name": self.lesson_name,
                "type": type,
                "video": self.video.serialize if self.video is not None else None
            }
        if type == "words_question":
            return {
                "id": self.id,
                "lesson_name": self.lesson_name,
                "type": type,
                "words": [w.serialize for w in self.words]
            }
        if type == "word_pair_exesize":
            return{
                "id": self.id,
                "word_ex": self.wordexecesize.serialize,
                "type": type
            }
        if type == "translate_exesize":
            if not self.translation:
                translate_exec = TranslationQuestion()

                ai_responce = generate_text(120, ENG_LEVELS[self.level])
                json_object = json.load(ai_responce.choices[0].message.content)
                translate_exec.level = self.level;
                translate_exec.topic = "any"
                translate_exec.original_text = json_object["original_text"]

                db.session.add(translate_exec)

                self.translation = translate_exec.id
                db.session.commit()
            else:
                translate_exec = TranslationQuestion().query.filter_by(id=self.translation).first()




            return {
                "id": self.id,
                "lesson_name": self.lesson_name,
                "type": type,
                "translation": translate_exec.serialize
            }

    @property
    def serialize_only_id(self):
        return {
            "id": self.id
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
    audio_query=db.Column(db.String(1000))
    audio_url=db.Column(db.String(255))
    answer = db.Column(db.String(255))
    level = db.Column(db.Integer)
    isrecord = db.Column(db.Boolean)

    exesize = db.relationship('Exesize', backref='aexesize', lazy=True)

    def __repr__(self):
        return f"({self.level}){self.question})"

    @property
    def serialize(self):
        return {
            "id": self.id,
            "question": self.question,
            "audio_url": self.audio_url,
            "level": self.level,
            "isrecord": self.isrecord

        }

class TranslationQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.String(50000))
    level = db.Column(db.Integer)
    topic=db.Column(db.String(255))

    @property
    def serialize(self):
        return {
            "original_text":self.original_text,
            "level":self.level,
            "topic":self.topic
        }

class Inputquestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255))
    answer = db.Column(db.String(255))
    level = db.Column(db.Integer)
    type = db.Column(db.String(255))
    isrecord = db.Column(db.Boolean)

    exesize = db.relationship('Exesize', backref='iexesize', lazy=True)

    def __repr__(self):
        return f"({self.level}){self.question})"

    @property
    def serialize(self):
        return {
            "id": self.id,
            "question": self.question,
            "level": self.level,
            "answer":self.answer,
            "type": self.type,
            "isrecord":self.isrecord
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
    type = db.Column(db.String(255))  # Убедитесь, что это поле существует
    is_active = db.Column(db.Boolean)
    code = db.Column(db.String(255))
    expiration_date = db.Column(db.DateTime)
    paymentdata = db.Column(db.String(2255))
    status = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)  # Используем 'users.id'

    @property
    def serialize(self):
        return {
            "id": self.id,
            "code": self.code,
            "status":self.status,
            "is_active": self.is_active,
            "type": self.type
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

class Billing (db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    type = db.Column(db.String(255))
    amount = db.Column(db.Integer)

    payment = db.relationship('Payments', backref='p_billing', lazy=True)

    cource = db.relationship('Cource', backref='c_billing', lazy=True)

    def __repr__(self):
        return f"{self.id} : {self.type} : {self.amount}"

    @property
    def serialize(self):
        return {
           "id": self.id,
            "name": self.name,
            "type": self.type,
            "amount": self.amount
        }

class Payments (db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    billing = db.Column(db.Integer, db.ForeignKey('billing.id'), nullable=False)


class LessonSchedler(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    duration = db.Column(db.Integer)
    date = db.Column(db.DateTime())
    telegram_contact_phone = db.Column(db.String(255))
    topic = db.Column(db.String(255))
    level = db.Column(db.String(255))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Reiting(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    lesson_id = db.Column(db.Integer)

    @property
    def serialize(self):
        return {
           "score": self.score,
        }

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    lesson_id = db.Column(db.Integer)

    comment = db.Column(db.String(2000))

    @property
    def serialize(self):
        user = User.query.filter_by(id=self.user_id).first()
        return {
            "userName": user.name,
            "comment": self.comment
        }

class Promo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(255), unique=True)
    type = db.Column(db.String(255))
    max_count = db.Column(db.Integer, nullable=False)
    current_count = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean())
    users = db.relationship('User', secondary=promo_users, backref=db.backref('promo_users', lazy='dynamic'))


class Devices(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    udid = db.Column(db.String(255))
    email = db.Column(db.String(255))


class Chattopic(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(2555))
    img_url = db.Column(db.String(255))


    chat = db.relationship('Chat', backref='chat_topic', lazy=True)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "img_url" : self.img_url
        }

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    chat_data = db.Column(db.String)

    topic = db.Column(db.Integer, db.ForeignKey('chattopic.id'), nullable=False)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "chat_data": json.loads(self.chat_data),
            "topic": self.topic.serialize
        }

words_execesizes_list = db.Table('words_execesizes_list',
    db.Column('wordexecesize_id', db.Integer, db.ForeignKey('wordexecesize.id'), primary_key=True),
    db.Column('wordslink_id', db.Integer, db.ForeignKey('wordslink.id'), primary_key=True)
)

class Wordslink(db.Model):
    __tablename__ = 'wordslink'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    eng_word = db.Column(db.String(255))
    rus_word = db.Column(db.String(255))
    uzb_word = db.Column(db.String(255))

    def __repr__(self):
        return f"{self.id} : {self.eng_word} : {self.rus_word} : {self.uzb_word}"

    @property
    def serialize(self):
        return {
            "eng": self.eng_word,
            "rus": self.rus_word,
            "uzb": self.uzb_word
        }

class Wordexecesize(db.Model):
    __tablename__ = 'wordexecesize'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    wordslink = db.relationship('Wordslink', secondary=words_execesizes_list, backref=db.backref('wordslink', lazy='dynamic'))

    def __repr__(self):
        return f"{self.name}"

    @property
    def serialize(self):
        return {
            "words": [w.serialize for w in self.wordslink]
        }


levelvs_exesizes = db.Table('levelvs_exesizes',
    db.Column('levels_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('exesesizes_id', db.Integer(), db.ForeignKey('exesesizes.id'), primary_key=True),
)

class Levels(db.Model):
    __tablename__ = 'levels'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    exesizes_link = db.relationship('Exesesizes', secondary=levelvs_exesizes, backref=db.backref('exesesizes', lazy='dynamic'))

    def __repr__(self):
        return f"{self.id}"

    @property
    def serialize(self):
        return {
            "id": self.id,
            "exesizes": [w.serialize for w in self.exesizes_link]
        }