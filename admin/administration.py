from flask_admin import Admin
from flask import Blueprint, render_template
from .views import TableView, UserView, CourceView, LessonView, ExesizeView, QuestionView, SubscriptionView, TextTranslateView
from .views import VideoQuestionView, BillingView, AudioQuestionView, InputQuestionView, ExesizesView, SpeackingLessonScheduller
from database.models import Role, Billing, User, Cource, Lesson, Exesize, Question, Subscription, Videoquestion, Audioquestion, Inputquestion, Exesesizes, LessonSchedler, TranslationQuestion

admin_blueprint = Blueprint('admin_blueprint', __name__)

@admin_blueprint.route('/')
def index():
    return render_template('index.html')

class Administration:
    def __init__(self, admin:Admin, db, app):
        self.admin = admin
        self.db = db
        self.app = app

    def initialize(self):
        self.admin.add_view(TableView(Role, self.db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Роли"))
        self.admin.add_view(UserView(User, self.db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Пользователи"))

        self.admin.add_view(CourceView(Cource, self.db.session, menu_icon_type='fa', menu_icon_value='fa-balance-scale',
                                name="Курсы"))

        self.admin.add_view(
            LessonView(Lesson, self.db.session, menu_icon_type='fa', menu_icon_value='fa-gears', name="Уроки"))

        self.admin.add_view(
            ExesizesView(Exesesizes, self.db.session, menu_icon_type='fa', menu_icon_value='fa-location-arrow',
                        name="Список Заданий"))

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
            SpeackingLessonScheduller(LessonSchedler, self.db.session, menu_icon_type='fa', menu_icon_value='fa-location-arrow',
                             name="Разговорный урок"))

        self.admin.add_view(
            SubscriptionView(Subscription, self.db.session, menu_icon_type='fa', menu_icon_value='fa-location-arrow', name="Subscriptions"))


