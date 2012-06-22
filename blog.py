import bottle

from pymongo import Connection

import cgi
import re
import datetime
import random
import hmac
import user

# inserts the blog entry and returns a permalink for the entry
def insert_entry(title, post):
    print "inserting blog entry", title, post

    connection = Connection("mongodb://production:10gen@staff.mongohq.com:10038/erlichson")
    db = connection.erlichson
    posts = db.posts

    exp = re.compile('\W') # match anything not alphanumeric
    whitespace = re.compile('\s')
    temp_title = whitespace.sub("_",title)
    permalink = exp.sub('', temp_title)

    post = {"title": title, 
            "post": post, 
            "permalink":permalink, 
            "date": datetime.datetime.utcnow()}

    posts.insert(post)

    return permalink
    
@bottle.route('/')
def index():
    connection = Connection("mongodb://production:10gen@staff.mongohq.com:10038/erlichson")

    db = connection.erlichson
    students = db.students

    student = students.find_one()
    return '<b>Hello %s!</b>' % student['name']

@bottle.route('/blog')
def blog_index():
    connection = Connection("mongodb://production:10gen@staff.mongohq.com:10038/erlichson")
    db = connection.erlichson
    posts = db.posts

    cur = posts.find().sort('date', direction=-1).limit(10)
    l=[]
    for post in cur:
        l.append({'title':post['title'], 'content':post['post'], 'post_date':post['date'], 'permalink':post['permalink']})
    return bottle.template('blog_template', dict(myposts=l))


@bottle.get("/blog/post/<permalink>")
@bottle.view('entry_template')
def show_post(permalink="notfound"):
    connection = Connection("mongodb://production:10gen@staff.mongohq.com:10038/erlichson")
    db = connection.erlichson
    posts = db.posts

    permalink = cgi.escape(permalink)

    print "about to quer on permalink = ", permalink
    post = posts.find_one({'permalink':permalink})
    if post == None:
        bottle.redirect("/blog/post_not_found")
    
    print "date of entry is ", post['date']

    return dict(mdate=post['date'],title=post['title'], content=post['post'])
        
    
@bottle.get("/blog/post_not_found")
def post_not_found():
    return "Sorry, post not found"


# how new posts bottle.get made
@bottle.get('/blog/newpost')
@bottle.view('newpost_template')
def get_newpost():
    return dict(subject="", content="",errors="")

@bottle.post('/blog/newpost')
def post_newpost():
    title = bottle.request.forms.get("subject")
    post = bottle.request.forms.get("content")
    
    if (title == "" or post == ""):
        errors="Post must contain a title and blog entry"
        return bottle.template("newpost_bottle.template", dict(subject=cgi.escape(title, quote=True), 
                                                 content=cgi.escape(post, quote=True), errors=errors))
    
    # looks like a good entry
    permalink=insert_entry(title, post)

    # now bottle.redirect to the blog permalink
    bottle.redirect("/blog/post/" + permalink)


@bottle.get('/blog/signup')
def present_signup():
    return bottle.template("signup", 
                           dict(username="", password="", 
                                password_error="", 
                                email="", username_error="", email_error="",
                                verify_error =""))

@bottle.post('/blog/signup')
def process_signup():
    email = bottle.request.forms.get("email")
    username = bottle.request.forms.get("username")
    password = bottle.request.forms.get("password")
    verify = bottle.request.forms.get("verify")

    # set these up in case we have an error case
    errors = {'username':cgi.escape(username), 'email':cgi.escape(email)}
    if (user.validate_signup(username, password, verify, email, errors)):
        #user.newuser(username, password, email)
        cookie= user.make_secure_val(username)
        bottle.response.set_cookie("username",cookie)
        bottle.redirect("/blog/welcome")
    else:
        return bottle.template("signup", errors)

    
@bottle.get("/blog/welcome")
def present_welcome():
    # check for a cookie, if present, then extract value

    cookie = bottle.request.get_cookie("username")

    username = user.check_secure_val(cookie)

    if (username == None):
        username = "Stranger"
    
    return bottle.template("welcome", {'username':username})


bottle.debug(True)
#bottle.run(host='ec2-174-129-129-215.compute-1.amazonaws.com', port=8082)
bottle.run(host='localhost', port=8082)


