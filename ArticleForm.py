from wtforms import Form,TextAreaField,PasswordField,validators,StringField

class ArticleForm(Form):
    title = StringField("Title",[validators.Length(min=4,max=800)])
    body = TextAreaField("Body",[validators.Length(min=4)])