from wtforms import Form,TextAreaField,PasswordField,validators,StringField

class RegisterUserForm(Form):
    name = StringField("Name",[validators.Length(min=4,max=50)])
    username = StringField("Username",[validators.Length(min=4,max=50)])
    email = StringField("Email",[validators.Length(min=4,max=100)])
    password = PasswordField("Password",[validators.Length(min=6),
    validators.DataRequired(),
    validators.EqualTo("confirm","Password does not match with confirm password.")])
    confirm = PasswordField("Confirm Password")