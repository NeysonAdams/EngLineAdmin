import datetime
import json
import os
from flask import url_for, redirect,  request, abort
from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_security import current_user
from flask_admin.contrib import sqla
from flask_admin.form.upload import FileUploadField
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import PasswordField, ValidationError, SelectField
from flask_admin.form import Select2Field
import io
from PIL import Image
from markupsafe import Markup

from config import INPUTS_TYPES
from database.models import Billing
from mobile_api.aicomponent import text_to_speach, speach_to_text, generate_text

levels = {
            "Beginner": 1,
            "Elementary": 2,
            "Pre-Intermediate": 3,
            "Intermediate": 4,
            "Advanced": 5
        }
images_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'images'))
video_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'video'))
audio_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'audio'))
# Create customized model view class
class TableView(sqla.ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


    can_edit = True
    edit_modal = True
    create_modal = True
    can_export = True
    can_view_details = True
    details_modal = True


class UserView(TableView):
    column_editable_list = ['email', 'login', 'name']
    column_searchable_list = column_editable_list
    column_exclude_list = ['password']
    #form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list
    form_overrides = {
        'password': PasswordField
    }

class CourceView(TableView):

    def picture_validation(form, field):
        if field.data:
            try:
                filename = field.data.filename
                if filename[-4:] != '.jpg' and filename[-4:] != '.png' and filename[-4:] != '.gif':
                    raise ValidationError('file must be .jpg or .png or gif')

                f_name = f"img_c_t_{str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))}{filename[-4:]}"

                img_path = os.path.join(images_folder, f_name )
                field.data = field.data.stream.read()
                image = Image.open(io.BytesIO(field.data))
                image.save(img_path)
                field.data = url_for('static', filename=f"/images/{f_name}")
                # setattr(form._obj, 'img_url', url_for('static', filename=f"/images/{f_name}"))
            except:
                f_name = field.data


    def on_model_change(view, context, model, name):
        setattr(model, 'img_url', context.img_url.data)
        setattr(model, 'level', levels[context.level.data])
        if context.price.data:
            model.price = context.price.data.id
        model.reiting = 0

    def pic_formatter(self, context, model, name):
       return Markup('<img src="%s" width="100" height="50">' % model.img_url)

    form_columns = ['title', 'level', 'discription', 'price', 'img_url', 'is_buy', 'lenguage']

    column_labels = dict(id="ID", title='Title', discription="Discription", level='Level', price='Price',
                         img_url='Title Image', lenguage='Lenguage')

    form_extra_fields = {
        'level': SelectField('Level',
                            choices=['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced']),
        'lenguage': SelectField('Lenguage',
                             choices=['ru', 'uz']),
        'price': QuerySelectField('Price', query_factory=lambda: Billing.query.all(), allow_blank=True)
    }

    column_formatters = dict(img_url=pic_formatter)
    form_overrides = dict(img_url=FileUploadField)
    form_args = dict(img_url=dict(validators=[picture_validation]))

    column_editable_list = ['title']
    column_searchable_list = column_editable_list

class LessonView(TableView):
    def video_validation(form, field):
        if field.data:
            try:
                filename = field.data.filename
                allowed_extensions = {'.mp4', '.avi', '.mov', '.MOV'}
                if not any(filename.endswith(ext) for ext in allowed_extensions):
                    raise ValidationError('File must be .mp4 or .avi')
                field.data = field.data.stream.read()
                # Save the video file
                f_name = f"v{str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))}{filename[4:]}"
                video_path = os.path.join(video_folder, f_name)
                #video_path = f"/home/khamraeva/mysite/EngLineAdmin/static/video/{f_name}"
                with open(video_path, 'wb') as f:
                    f.write(field.data)
                field.data = url_for('static', filename=f"video/{f_name}")
                return url_for('static', filename=f"video/{f_name}")
            except:
                pass

    def on_model_change(view, context, model, name):
        setattr(model, 'video_link', context.video_link.data)

    def video_formatter(view, context, model, name):
        if model.video_link:
            return Markup(
                f'<video width="160" height="120" controls><source src="{model.video_link}" type="video/mp4"></video>'
            )
        return ""

    form_columns = ['lesson_name', 'video_link', 'lesson_description', 'presentation_link', 'slides_link', "cource", "exesizes"]

    column_labels = dict(id="ID", lesson_name='Title', lesson_description="Description", video_link='Video URL',
                         presentation_link='Presentation', slides_link='Slides', cource="Course")

    column_formatters = dict(video_link=video_formatter)
    form_overrides = dict(video_link=FileUploadField)
    form_args = dict(video_link=dict(validators=[video_validation], base_path=os.path.join("static", "video")))


    column_editable_list = ['lesson_name']
    column_searchable_list = column_editable_list

class VideoQuestionView (TableView):
    def video_validation(form, field):
        if field.data:
            try:
                filename = field.data.filename
                allowed_extensions = {'.mp4', '.avi', '.mov', '.MOV'}
                if not any(filename.endswith(ext) for ext in allowed_extensions):
                    raise ValidationError('File must be .mp4 or .avi')
                field.data = field.data.stream.read()
                # Save the video file
                f_name = f"video_e_t_{str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))}{filename[4:]}"
                video_path= os.path.join(video_folder, f_name)
                with open(video_path, 'wb') as f:
                    f.write(field.data)
                field.data = url_for('static', filename=f"video/{f_name}")
                return field.data
            except:
                pass

    def on_model_change(view, context, model, name):
        setattr(model, 'video_url', context.video_url.data)
        setattr(model, 'level', levels[context.level.data])

    def video_formatter(view, context, model, name):
        if model.video_url:
            return Markup(
                f'<video width="320" height="240" controls><source src="{model.video_url}" type="video/mp4"></video>')
        return ""

    form_columns = ['question', 'video_url', 'answer', 'level']
    column_labels = dict(question='Question', answer="Answer", video_url='Video URL',
                         level='Level')
    column_formatters = dict(video_url=video_formatter)
    form_overrides = dict(video_url=FileUploadField)
    form_args = dict(video_url=dict(validators=[video_validation], base_path=os.path.join("static", "video")))

    form_extra_fields = {
        'level': SelectField('Level',
                             choices=['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced'])
    }

    column_editable_list = ['question', 'level']
    column_searchable_list = column_editable_list

class AudioQuestionView(TableView):
    def audio_validation(form, field):
        if field.data:
            try:
                filename = field.data.filename
                allowed_extensions = {'.mp3', '.wav'}
                if not any(filename.endswith(ext) for ext in allowed_extensions):
                    raise ValidationError('Audio file must be .mp3 or .wav')
                f_name = f"audio_a_q_{str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))}{filename[-4:]}"
                field.data = field.data.stream.read()
                audio_path = os.path.join(audio_folder, f_name)
                with open(audio_path, 'wb') as f:
                    f.write(field.data)
                field.data = url_for('static', filename=f"audio/{f_name}")
                return url_for('static', filename=f"audio/{f_name}")
            except:
                pass

    def on_model_change(view, context, model, name):
        if context.audio_url.data:
            if not context.audio_query.data:
                filename=context.audio_url.data.split("/")[-1]
                audio_path = os.path.join(audio_folder, filename)
                with open(audio_path, 'rb') as f:
                    ai_response = speach_to_text(f)
                    setattr(model, 'audio_query', ai_response)

            setattr(model, 'audio_url', context.audio_url.data)

        if context.audio_query.data and not context.audio_url.data:
            f_name = f"audio_a_q_{str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))}.mp3"
            audio_path = os.path.join(audio_folder, f_name)
            audio = text_to_speach(context.audio_query.data)
            if context.audio_url.data:
                filename = context.data.filename
                if os.path.exists(os.path.join(audio_folder, filename)):
                    os.remove(os.path.join(audio_folder, filename))
            audio.stream_to_file(audio_path)
            setattr(model, 'audio_url', url_for('static', filename=f"audio/{f_name}"))


        setattr(model, 'level', levels[context.level.data])

    def audio_formatter(view, context, model, name):
        if model.audio_url:
            return Markup(f'<audio controls><source src="{model.audio_url}" type="audio/mpeg"></audio>')

        return ""

    form_columns = ['question', 'audio_query', 'audio_url', 'answer', 'level', 'isrecord']
    column_labels = dict(question='Question', audio_query='Query', answer="Answer", audio_url='Audio URL',
                         level='Level', isrecord='Recorded')
    column_formatters = dict(audio_url=audio_formatter)
    form_overrides = dict(audio_url=FileUploadField)

    form_args = dict(audio_url=dict(validators=[audio_validation], base_path=os.path.join("static","audio")))

    column_editable_list = ['question', 'level']
    column_searchable_list = column_editable_list

    form_extra_fields = {
        'level': SelectField('Level',
                             choices=['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced'])
    }

class InputQuestionView(TableView):
    form_columns = ['question', 'answer', 'level', 'type', 'isrecord']
    column_labels = dict(question='Question', answer="Answer", level='Level', type="Type", isrecord='Recorded')
    column_editable_list = ['question', 'level']
    column_searchable_list = column_editable_list

    def on_model_change(view, context, model, name):
        setattr(model, 'level', levels[context.level.data])

    form_extra_fields = {
        'level': SelectField('Level',
                             choices=['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced']),

        'type': SelectField('Type',
                             choices=INPUTS_TYPES)
    }

class TextTranslateView(TableView):
    form_columns = ['original_text', 'level', 'topic']
    column_labels = dict(original_text='original_text', level='Level', topic="Topic")

    def on_model_change(view, context, model, name):
        if not context.original_text.data:
            topic = context.topic.data
            if not topic:
                topic = "any"
                setattr(model, 'topic', topic)
            ai_response = generate_text(context.level.data, 120, topic)
            print(ai_response.choices[0].message.content)
            jobj = json.loads(ai_response.choices[0].message.content)
            setattr(model, 'original_text', jobj['original_text'])
        setattr(model, 'level', levels[context.level.data])

    form_extra_fields = {
        'level': SelectField('Level',
                             choices=['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced'])
    }


class ExesizeView (TableView):
    column_labels = dict(id="ID", lesson_name='Title', type='Type', level='Level', lesson="Lesson")
    form_columns = ['id','lesson_name', 'type', 'level','lesson', 'question', 'input', 'audio', 'video', 'words']

    def on_model_change(view, context, model, name):
        setattr(model, 'level', levels[context.level.data])

    form_extra_fields = {
        'type': SelectField('Type',
                            choices=['test_question', 'input_question', 'audio_question', 'video_question', 'words_question', 'record_question', 'translate_exesize']),
        'level': SelectField('Level',
                             choices=['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced'])
    }
    column_labels = dict(lesson_name='Lesson Name', type="Type", level='Level')
    column_editable_list = ['id','lesson_name','type']
    column_searchable_list = column_editable_list

class ExesizesView (TableView):
    def picture_validation(form, field):
        if field.data:
            try:
                filename = field.data.filename
                if filename[-4:] != '.jpg' and filename[-4:] != '.png' and filename[-4:] != '.gif':
                    raise ValidationError('file must be .jpg or .png or gif')

                f_name = f"img_e_l_t_{str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))}{filename[-4:]}"

                img_path = os.path.join(images_folder, f_name)
                field.data = field.data.stream.read()
                image = Image.open(io.BytesIO(field.data))
                image.save(img_path)
                field.data = url_for('static', filename=f"/images/{f_name}")
                # setattr(form._obj, 'img_url', url_for('static', filename=f"/images/{f_name}"))
            except:
                pass

    def on_model_change(view, context, model, name):
        setattr(model, 'img_url', context.img_url.data)
        setattr(model, 'level', levels[context.level.data])

    def pic_formatter(self, context, model, name):
        return Markup('<img src="%s" width="100" height="50">' % model.img_url)

    column_labels = dict(id="ID", name='Title', type='Type', lenguage="Lenguage",  img_url='Title Image', level="Level")

    form_columns = [ 'name', 'type', 'lenguage','img_url', "level", 'exesize']

    form_extra_fields = {
        'type': SelectField('Type',
                            choices=['situation', 'speach', 'audio', 'reading', 'writing', 'qualification']),
        'level': SelectField('Level',
                             choices=['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced']),
        'lenguage':SelectField('Level',
                             choices=['ru', 'uz']),
    }

    column_formatters = dict(img_url=pic_formatter)
    form_overrides = dict(img_url=FileUploadField)
    form_args = dict(img_url=dict(validators=[picture_validation]))

    column_labels = dict(name='Name', type="Type", exesize="List")
    column_editable_list = ['name', 'type']
    column_searchable_list = column_editable_list



class QuestionView(TableView):
    form_columns = ['question', 'var1', 'var2', 'var3','var4', 'right_var', 'var_dif']
    column_labels = dict(question='Question', var1='Variant(1)', var2='Variant(2)',
                         var3='Variant(3)', var4='Variant(4)',
                         right_var='Right Variant', var_dif='Dificulty')
    column_editable_list = ['question']
    column_searchable_list = column_editable_list

    def on_model_change(view, context, model, name):
        setattr(model, 'var_dif', levels[context.var_dif.data])

    form_extra_fields = {
        'var_dif': SelectField('Level',
                             choices=['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced'])
    }

class SubscriptionView(TableView):

    def picture_validation(form, field):
        if field.data:
            filename = field.data.filename
            if filename[-4:] != '.jpg' and filename[-4:] != '.png' and filename[-4:] != '.gif':
                raise ValidationError('file must be .jpg or .png or gif')

            f_name = f"img_s_t_{str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))}{filename[-4:]}"

            img_path = os.path.join(images_folder, f_name)
            field.data = field.data.stream.read()
            image = Image.open(io.BytesIO(field.data))
            image.save(img_path)
            field.data = url_for('static', filename=f"/images/{f_name}")
            # setattr(form._obj, 'img_url', url_for('static', filename=f"/images/{f_name}"))

    def on_model_change(view, context, model, name):
        setattr(model, 'img_url', context.img_url.data)


    def pic_formatter(view, context, model, name):
       return Markup('<img src="%s">' % model.image_source)


    form_columns = ['name', 'discription', 'price', 'is_active', 'img_url']
    column_labels = dict(name='Title', discription='Discription', price='Price',
                         is_active='Active', img_url='Image URL')

    column_formatters = dict(img_url=pic_formatter)
    form_overrides = dict(img_url=FileUploadField)
    form_args = dict(img_url=dict(validators=[picture_validation]))

    column_editable_list = ['name']
    column_searchable_list = column_editable_list

class BillingView(TableView):
    form_columns = ['name', 'type', 'amount']
    column_labels = dict(name='Title', type='Type', amount="Amount")

    form_extra_fields = {
        'type': SelectField('Type',
                            choices=['free', 'course', 'speaking_lesson', 'exercises']),
    }
    column_editable_list = ['name', 'type', 'amount']
    column_searchable_list = column_editable_list


class SpeackingLessonScheduller(TableView):
    form_columns = ["duration", "date", "telegram_contact_phone", "topic", "level"]
    column_labels = dict(duration='Duration', date='Date', telegram_contact_phon="Phone", topic="Topic", level="Level")

    form_extra_fields = {
        'duration': SelectField('Duration',
                             choices=[15, 30, 60]),
        'level': SelectField('Level',
                             choices=['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced'])
    }

    column_editable_list = ['topic', 'level', 'date']
    column_searchable_list = column_editable_list



# class WordView(TableView):
#     def audio_validation(form, field):
#         if field.data:
#             filename = field.data.filename
#             allowed_extensions = {'.mp3', '.wav'}
#             if not any(filename.endswith(ext) for ext in allowed_extensions):
#                 raise ValidationError('Audio file must be .mp3 or .wav')
#             field.data = field.data.stream.read()
#             audio_path = os.path.join("static/audio/", filename)
#             with open(audio_path, 'wb') as f:
#                 f.write(field.data)
#             form.audio_link.data = "static/audio/" + filename
#
#     def audio_formatter(view, context, model, name):
#         if model.audio_link:
#             return Markup(f'<audio controls><source src="{model.audio_link}" type="audio/mpeg"></audio>')
#         return ""
#
#     form_columns = ['word', 'translate', 'audio_url']
#     column_labels = dict(word='Word', translate='Translation', audio_url='Audio Url')
#
#     column_formatters = dict(audio_url=audio_formatter)
#     form_overrides = dict(audio_url=FileUploadField)
#     form_args = dict(audio_url=dict(validators=[audio_validation]))
#
#     column_editable_list = ['word']
#     column_searchable_list = column_editable_list



