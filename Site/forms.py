from flask_wtf import FlaskForm, RecaptchaField
from wtforms.fields import StringField, PasswordField, SubmitField, EmailField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired('Name Field is Required')])
    email = EmailField('Email', validators=[DataRequired('Email Field is Required'), Email('Email is InValid')])
    password = PasswordField('password',
                             validators=[DataRequired('Password is Required'),
                                         Length(min=6, message='Password is less than 6 character')])
    confirm = PasswordField('confirm', validators=[EqualTo('password', message='Password is not confirm')])
    recaptcha = RecaptchaField()


class SignInForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired('Email Field is Required'), Email('Email is InValid')])
    password = PasswordField('password',
                             validators=[DataRequired('Password is Required'),
                                         Length(min=6, message='Password is less than 6 character')])
    recaptcha = RecaptchaField()


class UpdateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired('Name Field is Required')])
    email = EmailField('Email', validators=[DataRequired('Email Field is Required'), Email('Email is InValid')])
    submit = SubmitField('Update')


class AddMugsForm(FlaskForm):
    title = StringField("title", validators=[DataRequired()], render_kw={'autofocus': True})
    img_url = StringField("img_url", validators=[DataRequired()])
    caption = StringField("caption", validators=[DataRequired()])
    price = DecimalField("price", validators=[DataRequired()])
    quantity = IntegerField("quantity", validators=[DataRequired()])
    submit = SubmitField()


class MakeAdminForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()], render_kw={'autofocus': True})
    submitadmin = SubmitField()
