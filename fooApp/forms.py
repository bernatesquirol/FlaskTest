from wtforms import Form, PasswordField, SubmitField, TextAreaField, FloatField, TextField
from wtforms.validators import NumberRange, required


class ProductForm(Form):
    name = TextField('Name', [required()])
    description = TextAreaField('Description')
    price = FloatField('Price', [NumberRange(0.00), required()])

    submit = SubmitField('Save')


class LoginForm(Form):
    """Render HTML input for user login form.

    Authentication (i.e. password verification) happens in the view function.
    """
    username = TextField('Username', [required()])
    password = PasswordField('Password', [required()])
