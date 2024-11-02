from flask import Flask, url_for
from flask_security import Security, SQLAlchemyUserDatastore
import asyncio
from flask_security.utils import hash_password
import flask_admin
from flask_admin import helpers as admin_helpers
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import datetime
from flask_cors import CORS

from database.models import Role, User, db, Question, Dictionary, Englishword, Russianword, Inputquestion

from mobile_api.authorization import auth as auth_blueprint
from admin.administration import admin_blueprint, Administration
from mobile_api.cources import cources_bluepprint
from others import others_blue_print
from mobile_api.fileloader import file_loader_bluerpint
from mobile_api.exesize import exesize_blueprint
from mobile_api.statistics import statistic_blueprint
from mobile_api.payment import payment_blueprint
from mobile_api.video_streamimg import video_stram_blueprint
from mobile_api.profile import profile
from mobile_api.subscription import subscription_blueprint, subscriptionUpdate
from mobile_api.chat import chat_blueprint
from mobile_api.analyticks import analytiks_blueprint
from mobile_api.levels import level_blueprint
from mobile_api.quests import quests_blueprint
from mobile_api.theory import theory_blueprint
from mobile_api.frazes import fraze_blueprint

import json

app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
admin = flask_admin.Admin(
    app,
    'AdministrationPanel',
    base_template='my_master.html',
    template_mode='bootstrap4',
)

app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(cources_bluepprint)
app.register_blueprint(others_blue_print)
app.register_blueprint(file_loader_bluerpint)
app.register_blueprint(exesize_blueprint)
app.register_blueprint(statistic_blueprint)
app.register_blueprint(payment_blueprint)
app.register_blueprint(video_stram_blueprint)
app.register_blueprint(profile)
app.register_blueprint(subscription_blueprint)
app.register_blueprint(chat_blueprint)
app.register_blueprint(analytiks_blueprint)
app.register_blueprint(level_blueprint)
app.register_blueprint(quests_blueprint)
app.register_blueprint(theory_blueprint)
app.register_blueprint(fraze_blueprint)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

admin_panel = Administration(admin, db, app)
admin_panel.initialize()

levels = {
    "Beginner":1,
    "Elementary":2,
    "Pre-Intermediate":3,
    "Intermediate":4,
    "Pre-Advanced":5,
    "Advanced":6
}
async def scheduled_task():
    subscriptionUpdate(app)

async def scheduler():
    while True:
        # Запуск задачи каждый день в 10:00 по времени сервера
        now = datetime.datetime.now()
        target_time = now.replace(hour=10, minute=0, second=0, microsecond=0)

        # Если текущее время больше целевого, сдвигаем на следующий день
        if now > target_time:
            target_time += datetime.timedelta(days=1)

        # Вычисляем, сколько осталось до 10:00
        wait_time = (target_time - now).total_seconds()

        # Ждем до целевого времени
        await asyncio.sleep(wait_time)

        # Выполняем задачу
        await scheduled_task()

@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

def add_words():
    with app.app_context():
        dict_files = ['bisnes_eng.json', 'comp_eng.json', 'economic_eng.json', 'short_eng.json']
        dict_name = ['Busines', 'Computers', 'Econimic', 'Short']
        i = 0

        for file in dict_files:

            dict_db = Dictionary(id=i, name=dict_name[i])
            db.session.add(dict_db)
            db.session.commit()
            with open(f'instance/{file}', 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)

                for w in data:
                    word = Englishword.query.filter_by(word=w['word']).first()
                    if not word:
                        word = Englishword(word=w['word'])
                        db.session.add(word)
                    for tr in w['translate']:
                        t_word = Russianword.query.filter_by(word=tr).first()
                        if not t_word:
                            t_word = Russianword(word=tr)
                            t_word.englishWord_id = word.id
                            db.session.add(t_word)
                    dict_db.words.append(word)
                db.session.commit()
            i=i+1

def add_questions():
    with app.app_context():
        with open('instance/questions.json', 'r') as json_file:
            data = json.load(json_file)

            for q in data["questions"]:
                question = Question(
                    question=q['question'],
                    var1=q['var1'],
                    var2=q['var2'],
                    var3=q['var3'],
                    var4=q['var4'],
                    right_var=q['right_var'],
                    var_dif=q['var_dif']
                )

                db.session.add(question)
            db.session.commit()

def test_build():
    with app.app_context():
        db.create_all()
        with open('instance/inputs.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

            for q in data["questions"]:
                iquestion = Inputquestion(
                    question=q['question'],
                    answer=q['answer'],
                    level=levels[q['level']]
                )
                db.session.add(iquestion)
            db.session.commit()

def creat_db():
    with app.app_context():
        db.create_all()
def build_sample_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        test_user = user_datastore.create_user(
            name='Admin',
            login='admin',
            email='admin@mail.ru',
            password=hash_password('admin'),
            roles=[user_role, super_user_role]
        )

        db.session.commit()