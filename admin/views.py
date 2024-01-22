import datetime
import os
from flask import url_for, redirect,  request, abort
from flask_security import current_user
from flask_admin.contrib import sqla
from flask_admin.form.upload import FileUploadField
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import PasswordField, ValidationError, SelectField
import io
from PIL import Image
from markupsafe import Markup

levels = {
            "Beginner": 1,
            "Elementary": 2,
            "Pre-Intermediate": 3,
            "Intermediate": 4,
            "Advanced": 5
        }

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

                img_path = os.path.join("static/images/", f_name )
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

    def pic_formatter(self, context, model, name):
       return Markup('<img src="%s" width="100" height="50">' % model.img_url)

    form_columns = ['title', 'level', 'discription', 'price', 'img_url', 'is_buy']

    column_labels = dict(id="ID", title='Title', discription="Discription", level='Level', price='Price',
                         img_url='Title Image')

    form_extra_fields = {
        'level': SelectField('Level',
                            choices=['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced'])
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
                allowed_extensions = {'.mp4', '.avi', '.mov'}
                if not any(filename.endswith(ext) for ext in allowed_extensions):
                    raise ValidationError('File must be .mp4 or .avi')
                field.data = field.data.stream.read()
                # Save the video file
                f_name = f"v{str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))}{filename[4:]}"
                video_folder = os.path.join("video", f_name)
                video_path = os.path.join("static", video_folder)
                print(video_path)
                with open(video_path, 'wb') as f:
                    f.write(field.data)
                field.data = url_for('static', filename=f"video/{f_name}")
                return field.data
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
                allowed_extensions = {'.mp4', '.avi', '.mov'}
                if not any(filename.endswith(ext) for ext in allowed_extensions):
                    raise ValidationError('File must be .mp4 or .avi')
                field.data = field.data.stream.read()
                # Save the video file
                f_name = f"video_e_t_{str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))}{filename[4:]}"
                video_folder = os.path.join("video", f_name)
                video_path= os.path.join("static", video_folder)
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
            filename = field.data.filename
            allowed_extensions = {'.mp3', '.wav'}
            if not any(filename.endswith(ext) for ext in allowed_extensions):
                raise ValidationError('Audio file must be .mp3 or .wav')
            f_name = f"audio_a_q_{str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))}{filename[-4:]}"
            field.data = field.data.stream.read()
            audio_path = os.path.join("static", "audio", f_name)
            with open(audio_path, 'wb') as f:
                f.write(field.data)
            field.data = url_for('static', filename=f"audio/{f_name}")
            return url_for('static', filename=f"audio/{f_name}")

    def on_model_change(view, context, model, name):
        setattr(model, 'audio_url', context.audio_url.data)
        setattr(model, 'level', levels[context.level.data])

    def audio_formatter(view, context, model, name):
        if model.audio_url:
            return Markup(f'<audio controls><source src="{model.audio_url}" type="audio/mpeg"></audio>')
        return ""

    form_columns = ['question', 'audio_url', 'answer', 'level']
    column_labels = dict(question='Question', answer="Answer", audio_url='Audio URL',
                         level='Level')
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
    form_columns = ['question', 'answer', 'level']
    column_labels = dict(question='Question', answer="Answer", level='Level')
    column_editable_list = ['question', 'level']
    column_searchable_list = column_editable_list

    def on_model_change(view, context, model, name):
        setattr(model, 'level', levels[context.level.data])

    form_extra_fields = {
        'level': SelectField('Level',
                             choices=['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced'])
    }

class ExesizeView (TableView):

    form_columns = ['lesson_name', 'type', 'level','lesson', 'question', 'input', 'audio', 'video', 'words']

    def on_model_change(view, context, model, name):
        setattr(model, 'level', levels[context.level.data])

    form_extra_fields = {
        'type': SelectField('Type',
                            choices=['test_question', 'input_question', 'audio_question', 'video_question', 'words_question', 'record_question']),
        'level': SelectField('Level',
                             choices=['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced'])
    }
    column_labels = dict(lesson_name='Lesson Name', type="Type", level='Level')
    column_editable_list = ['lesson_name','type']
    column_searchable_list = column_editable_list



class QuestionView(TableView):
    form_columns = ['question', 'var1', 'var2', 'var3','var4', 'right_var', 'var_dif']
    column_labels = dict(question='Question', var1='Variant(1)', var2='Variant(2)',
                         var3='Variant(3)', var4='Variant(4)',
                         right_var='Right Variant', var_dif='Dificulty')
    column_editable_list = ['question']
    column_searchable_list = column_editable_list

    def on_model_change(view, context, model, name):
        setattr(model, 'level', levels[context.level.data])

    form_extra_fields = {
        'level': SelectField('Level',
                             choices=['Beginner', 'Elementary', 'Pre-Intermediate', 'Intermediate', 'Advanced'])
    }

class SubscriptionView(TableView):

    def picture_validation(form, field):
        if field.data:
            filename = field.data.filename
            if filename[-4:] != '.jpg' and filename[-4:] != '.png' and filename[-4:] != '.gif':
                raise ValidationError('file must be .jpg or .png or gif')

            f_name = f"img_s_t_{str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))}{filename[-4:]}"

            img_path = os.path.join("static/images/", f_name)
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



