from flask_admin import Admin
from flask import Blueprint, render_template
from .views import TableView, UserView, CourceView, LessonView, ExesizeView, QuestionView, SubscriptionView, TextTranslateView, WordsExecizeView, DictionaryView, QuestDescriptionView
from .views import VideoQuestionView, BillingView, AudioQuestionView, InputQuestionView, ExesizesView, SpeackingLessonScheduller, PromoView, ChatTopicView, LevelView, QuestView, TheoryView, FrazesView
from database.models import Role, Promo, Billing, User, Cource, Lesson, Exesize, Question, Subscription, Videoquestion, Audioquestion, Inputquestion, Quests, Exesesizes, LessonSchedler, TranslationQuestion, Chattopic, Wordexecesize, Wordslink, Levels, Theory, Frazes
from database.models import QuestDescription

admin_blueprint = Blueprint('admin_blueprint', __name__)

@admin_blueprint.route('/')
@admin_blueprint.route('/eula')
@admin_blueprint.route('/policy')
def index():
    return render_template('index.html')

@admin_blueprint.route('/<lang>')
@admin_blueprint.route('/<lang>/eula')
@admin_blueprint.route('/<lang>/policy')
def indexlang(lang):
    return render_template('index.html')

@admin_blueprint.route('/admin')
def admin():
    return render_template('admin.html')

class Administration:
    def __init__(self, admin:Admin, db, app):
        self.admin = admin
        self.db = db
        self.app = app

    def initialize(self):
        self.admin.add_view(TableView(Role, self.db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Роли"))
        self.admin.add_view(UserView(User, self.db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Пользователи"))



        self.admin.add_view(
            LevelView(Levels, self.db.session, menu_icon_type='fa', menu_icon_value='fa-rocket',
                      name="Уровни"))

        self.admin.add_view(
            ExesizesView(Exesesizes, self.db.session, menu_icon_type='fa', menu_icon_value='fa-location-arrow',
                        name="Пакеты Заданий"))

        self.admin.add_view(
            ExesizeView(Exesize, self.db.session, menu_icon_type='fa', menu_icon_value='fa-location-arrow', name="Задания"))

        self.admin.add_view(
            QuestionView(Question, self.db.session, menu_icon_type='fa', menu_icon_value='fa-envelope-open-o', name="Вопросы"))

        self.admin.add_view(
            VideoQuestionView(Videoquestion, self.db.session, menu_icon_type='fa', menu_icon_value='fa-envelope-open-o',
                         name="Видео Вопрос"))
        self.admin.add_view(
            AudioQuestionView(Audioquestion, self.db.session, menu_icon_type='fa', menu_icon_value='fa-envelope-open-o',
                         name="Аудио Вопросс"))
        self.admin.add_view(
            InputQuestionView(Inputquestion, self.db.session, menu_icon_type='fa', menu_icon_value='fa-envelope-open-o',
                         name="Письменный Вопрос"))

        self.admin.add_view(
            TextTranslateView(TranslationQuestion, self.db.session, menu_icon_type='fa', menu_icon_value='fa-envelope-open-o',
                         name="Текста для перевода"))

        self.admin.add_view(
            BillingView(Billing, self.db.session, menu_icon_type='fa', menu_icon_value='fa-location-arrow',
                             name="Биллинг"))
        self.admin.add_view(
            QuestView(Quests, self.db.session, menu_icon_type='fa', menu_icon_value='fa-question',
                             name="Квесты "))

        self.admin.add_view(
            QuestDescriptionView(QuestDescription, self.db.session, menu_icon_type='fa', menu_icon_value='fa-question',
                      name="Квесты Описание"))

        self.admin.add_view(TheoryView(Theory, self.db.session, menu_icon_type='fa', menu_icon_value='fa-balance-scale',
                               name="Фразы Дня"))

        self.admin.add_view(
           FrazesView(Frazes, self.db.session, menu_icon_type='fa', menu_icon_value='fa-gears', name="Фразы"))


        self.admin.add_view(
            WordsExecizeView(Wordexecesize, self.db.session, menu_icon_type='fa', menu_icon_value='fa-list',
                             name="Слова Пары"))

        self.admin.add_view(
            DictionaryView(Wordslink, self.db.session, menu_icon_type='fa', menu_icon_value='fa-buysellads',
                             name="Словарь"))

        self.admin.add_view(
            SubscriptionView(Subscription, self.db.session, menu_icon_type='fa', menu_icon_value='fa-address-card',
                             name="Подписки"))

        self.admin.add_view(
            PromoView(Promo, self.db.session, menu_icon_type='fa', menu_icon_value='fa-qrcode',
                             name="Промокод"))



        #self.admin.add_view(
        #    ChatTopicView(Chattopic, self.db.session, menu_icon_type='fa', menu_icon_value='fa-weixin',
        #              name="Чат Комнаты"))


