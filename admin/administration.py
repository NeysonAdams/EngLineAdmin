from flask_admin import Admin
from flask import Blueprint, render_template
from .views import TableView, UserView, CourceView, LessonView, ExesizeView, QuestionView, SubscriptionView
from .views import VideoQuestionView, BillingView, AudioQuestionView, InputQuestionView, ExesizesView
from database.models import Role, Billing, User, Cource, Lesson, Exesize, Question, Subscription, Videoquestion, Audioquestion, Inputquestion, Exesesizes

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
        self.admin.add_view(TableView(Role, self.db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Roles"))
        self.admin.add_view(UserView(User, self.db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Users"))

        self.admin.add_view(CourceView(Cource, self.db.session, menu_icon_type='fa', menu_icon_value='fa-balance-scale',
                                name="Courses"))

        self.admin.add_view(
            LessonView(Lesson, self.db.session, menu_icon_type='fa', menu_icon_value='fa-gears', name="Lessons"))

        self.admin.add_view(
            ExesizesView(Exesesizes, self.db.session, menu_icon_type='fa', menu_icon_value='fa-location-arrow',
                        name="Execizes List"))

        self.admin.add_view(
            ExesizeView(Exesize, self.db.session, menu_icon_type='fa', menu_icon_value='fa-location-arrow', name="Exesizes"))

        self.admin.add_view(
            QuestionView(Question, self.db.session, menu_icon_type='fa', menu_icon_value='fa-envelope-open-o', name="Questions"))

        self.admin.add_view(
            VideoQuestionView(Videoquestion, self.db.session, menu_icon_type='fa', menu_icon_value='fa-envelope-open-o',
                         name="Video Questions"))
        self.admin.add_view(
            AudioQuestionView(Audioquestion, self.db.session, menu_icon_type='fa', menu_icon_value='fa-envelope-open-o',
                         name="Audio Questions"))
        self.admin.add_view(
            InputQuestionView(Inputquestion, self.db.session, menu_icon_type='fa', menu_icon_value='fa-envelope-open-o',
                         name="Input Questions"))

        self.admin.add_view(
            BillingView(Billing, self.db.session, menu_icon_type='fa', menu_icon_value='fa-location-arrow',
                             name="Billing"))

        self.admin.add_view(
            SubscriptionView(Subscription, self.db.session, menu_icon_type='fa', menu_icon_value='fa-location-arrow', name="Subscriptions"))


