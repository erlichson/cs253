from bottle import route,run,get,post, response, view, redirect, request, debug, template

from pymongo import Connection

import cgi
import re
import datetime

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
    
@route('/')
def index():
    connection = Connection("mongodb://production:10gen@staff.mongohq.com:10038/erlichson")

    db = connection.erlichson
    students = db.students

    student = students.find_one()
    return '<b>Hello %s!</b>' % student['name']

@route('/blog')
def blog_index():
    connection = Connection("mongodb://production:10gen@staff.mongohq.com:10038/erlichson")
    db = connection.erlichson
    posts = db.posts

    cur = posts.find().sort('date', direction=-1).limit(10)
    l=[]
    for post in cur:
        l.append({'title':post['title'], 'content':post['post'], 'post_date':post['date']})
    return template('blog_template', dict(myposts=l))

        


@get("/blog/post/<permalink>")
@view('entry_template')
def show_post(permalink="notfound"):
    connection = Connection("mongodb://production:10gen@staff.mongohq.com:10038/erlichson")
    db = connection.erlichson
    posts = db.posts

    permalink = cgi.escape(permalink)

    print "about to quer on permalink = ", permalink
    post = posts.find_one({'permalink':permalink})
    if post == None:
        redirect("/blog/post_not_found")
    
    print "date of entry is ", post['date']

    return dict(mdate=post['date'],title=post['title'], content=post['post'])
        
    
@get("/blog/post_not_found")
def post_not_found():
    return "Sorry, post not found"


# how new posts get made
@get('/blog/newpost')
@view('newpost_template')
def get_newpost():
    return dict(subject="", content="",errors="")

@post('/blog/newpost')
def post_newpost():
    title = request.forms.get("subject")
    post = request.forms.get("content")
    
    if (title == "" or post == ""):
        errors="Post must contain a title and blog entry"
        return template("newpost_template", dict(subject=cgi.escape(title, quote=True), 
                                                 content=cgi.escape(post, quote=True), errors=errors))
    
    # looks like a good entry
    permalink=insert_entry(title, post)

    # now redirect to the blog permalink
    redirect("/blog/post/" + permalink)

debug(True)
run(host='ec2-174-129-129-215.compute-1.amazonaws.com', port=8082)

