import cgi
import re
import hmac


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
    # looks good
    return True


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
