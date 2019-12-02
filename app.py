from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
# from data import Get_articles
from passlib.hash import sha256_crypt
from RegisterUserForm import RegisterUserForm
from ArticleForm import ArticleForm
from database import SelectRecordsFromDatabase,InsertRecords,DeleteRecords
from functools import wraps

app = Flask(__name__)
# articles = Get_articles()  # file driven implementation

# Check User is logged in or not
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('logged_in' in session):
            return f(*args, **kwargs)
        else:
            flash("Unauthorized login",'danger')
            return redirect(url_for("UserLogin"))
    return wrap

# Home Page
@app.route("/")
def Index():
    return render_template('home.html')

# About Page
@app.route("/about")
def About():
    return render_template("about.html")

# Display All Articles
@app.route("/articles")
@is_logged_in
def Articles():
    getAllArticlesQry = "SELECT id, title, author, body, create_date FROM articles"
    articles = SelectRecordsFromDatabase(getAllArticlesQry)
    # app.logger.debug(articles)
    if (len(articles) > 0):
        return render_template("articles.html",articles=articles)

# Display Single Article
@app.route("/article/<string:id>")
@is_logged_in
def Article(id):
    getArticleByIdQry = "SELECT id, title, author, body, create_date FROM articles WHERE id = {}".format(id)
    article = SelectRecordsFromDatabase(getArticleByIdQry)
    # app.logger.debug(article)
    return render_template("article.html",article=article[0])


# Register
@app.route("/register",methods=['GET','POST'])
def Register():
    form = RegisterUserForm(request.form)
    if (request.method == "POST" and form.validate()):
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        # Insert records in database
        qry = "INSERT INTO userDetails (name, username, email, password) VALUES ('{0}','{1}','{2}','{3}')".format(name,username,email,password)
        InsertRecords(qry)
        flash('You are now registered and can log in', 'success')
        return redirect(url_for("Index"))
    return render_template("register.html",form=form)

# Login Implement
@app.route("/login",methods=["GET","POST"])
def UserLogin():
    if (request.method == "POST"):
        # get username password from form
        # query database using the username  and get that password.
        # match candidate password and database password.
        # if matches then redirect to index and store in session
        username = request.form['username']
        password_candidate = request.form['password']
        qryGetUser = "SELECT * FROM userDetails WHERE username = '{0}'".format(username)
        result = SelectRecordsFromDatabase(qryGetUser)
        if (len(result) > 0):
            password_db = result[0]['password']
            name = result[0]['name']
            if (sha256_crypt.verify(password_candidate,password_db)):
                session['logged_in'] = True
                session['username'] = username
                session['name'] = name
                # app.logger.debug("Name {}".format(name))
                # app.logger.debug("Password matched.")
                flash("Logged In Successfully",'success')
                return redirect(url_for("Index")) # Will change with dashboard url later
            else:
                # app.logger.debug("Wrong Password.")
                error = "Please enter correct password"
                return render_template("login.html",error=error)
        else:
            # app.logger.debug("User not exists.")
            error = "User not exists.Please enter correct username."
            return render_template("login.html",error=error)
    return render_template("login.html")

#  Logout
@app.route("/logout")
@is_logged_in
def Logout():
    session.clear()
    return redirect(url_for("UserLogin"))

# Dashboard
@app.route("/dashboard")
@is_logged_in
def Dashboard():
    getAllArticlesQry = "SELECT id, title, author, body, create_date FROM articles"
    articles = SelectRecordsFromDatabase(getAllArticlesQry)
    # app.logger.debug(articles)
    return render_template("dashboard.html",articles=articles)

# Add Article
@app.route("/add_article", methods=['GET','POST'])
@is_logged_in
def Add_Article():
    form = ArticleForm(request.form)

    if (request.method == "POST" and form.validate()):
        title = form.title.data
        body = form.body.data
        body = body.replace("'","''") # for escape char of string in  sql server 
        artilceInsertQuery = "INSERT INTO articles (title, author, body) VALUES ('{0}','{1}','{2}')".format(title,session['name'],body)
        # app.logger.debug(artilceInsertQuery)
        InsertRecords(artilceInsertQuery)
        flash("Article created!",'success')
        return redirect(url_for("Dashboard"))
    return render_template("add_article.html",form=form)

# Edit Article
@app.route("/edit_article/<string:id>", methods=['GET','POST'])
@is_logged_in
def Edit_Article(id):
    form = ArticleForm(request.form)
    getArticleById = "SELECT id, title, author, body, create_date FROM articles WHERE id = {0}".format(id)
    article = SelectRecordsFromDatabase(getArticleById)[0]
    
    # Fill the form 
    form.title.data = article['title']
    form.body.data = article['body']

    if (request.method == "POST" and form.validate()):
        title = request.form['title']
        body = request.form['body']
        body = body.replace("'","''")  # for escape char of string in sql server 
        artilceUpdateQuery = "UPDATE articles SET title = '{0}', author = '{1}', body = '{2}' WHERE id = {3}".format(title,session['name'],body,id)
        # app.logger.debug(artilceUpdateQuery)
        InsertRecords(artilceUpdateQuery)
        flash("Article Edited Successfully!",'success')
        return redirect(url_for("Dashboard"))
    return render_template("edit_article.html",form=form)

# Delete Article 
@app.route("/delete_article/<string:id>",methods=['POST'])
@is_logged_in
def Delete_Article(id):
    deleteArticleQry = "DELETE FROM articles WHERE id = {0} AND author = '{1}'".format(id,session['name'])
    app.logger.debug(deleteArticleQry)
    affectedRows = DeleteRecords(deleteArticleQry)
    if (affectedRows != 0):
        flash("Article Deleted Successfully",'success')
        return redirect(url_for("Dashboard"))
    else:
        flash("You do not have the authority to detele this article",'danger')
        return redirect(url_for("Dashboard"))
    


if (__name__ == "__main__"):
    app.secret_key = "youwillnotabletoguess"
    app.run(debug=True,port=5050,host='0.0.0.0')