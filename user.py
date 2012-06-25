import cgi
import re
import hmac
import random
import string
import hashlib
from pymongo import Connection, errors

# makes a little salt
def make_salt():
    salt = ""
    for i in range(5):
        salt = salt + random.choice(string.ascii_letters)
    return salt


# implement the function make_pw_hash(name, pw) that returns a hashed password 
# of the format: 
# HASH(pw + salt),salt
# use sha256

def make_pw_hash(pw):
    salt = make_salt();
    return hashlib.sha256(pw + salt).hexdigest()+","+ salt


# validates that the user information is valid, return True of False 
# and fills in the error codes
def validate_signup(username, password, verify, email, errors):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PASS_RE = re.compile(r"^.{3,20}$")
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

    errors['username_error']  = ""
    errors['password_error'] = ""
    errors['verify_error'] = ""
    errors['email_error'] = ""
    

    if not USER_RE.match(username):
        errors['username_error']  = "invalid username. try just letters and numbers"
        return False

    if not PASS_RE.match(password):
        errors['password_error'] = "invalid password."
        return False
    if password != verify:
        errors['verify_error'] = "password must match"
        return False
    if email != "":
        if not EMAIL_RE.match(email):
            errors['email_error'] = "invalid email address"
            return False
    return True

# creates a new user in the database
def newuser(username, password, email):
    password_hash = make_pw_hash(password)

    user = {'username':username, 'password':password_hash}
    if (email != ""):
        user['email'] = email


    connection = Connection("mongodb://production:10gen@staff.mongohq.com:10038/erlichson")
    db = connection.erlichson
    users = db.users
    counters = db.counters

    # let's get ourselves a UID
    
    uid_counter = counters.find_and_modify(query={'type':'uid'}, update={'$inc':{'value':1}})

    user['uid'] = uid_counter['value']

    try:
        db.users.insert(user, safe=True)
    except OperationFailure:
        print "oops, mongo error"
        return None
    except DuplicateKeyError as e:
        return None

    return user['uid']

def uid_to_username(uid):
    connection = Connection("mongodb://production:10gen@staff.mongohq.com:10038/erlichson")
    db = connection.erlichson
    users = db.users
    
    user = users.find_one({'uid':int(uid)})

    return user['username']
    


# Implement the hash_str function to use HMAC and our SECRET instead of md5
SECRET = 'verysecret'
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

# call this to hash a cookie value
def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

# call this to make sure that the cookie is still secure
def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val
