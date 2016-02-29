import sqlite3
from flask import g, Flask
import helper

app = Flask(__name__)

database_file = 'database.db'

# instancing from Storage class, which takes care about logged users
storage = helper.Storage()

socket_pool = helper.SocketPool()

stats_info = helper.StatsInfo()

def connect_db():
    rv = sqlite3.connect(database_file)
    # rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()

    return g.sqlite_db

@app.teardown_appcontext
def close_db():
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def _create_database_structure():
    schema_file = 'database.schema'

    db = get_db()
    with app.open_resource(schema_file, mode='r') as f:
        db.cursor().executescript(f.read())

def sign_up_user(d):
    try:
        data = (d['email'], d['password'], d['firstname'], d['familyname'], d['gender'], d['city'], d['country'])
    except:
        return {"success": False, "message": "Form data missing or incorrect type."}

    try:
        db = get_db()
        c = db.cursor()
    except:
        return {"success": False, "message": "Database problems."}

    try:
        c.execute("INSERT INTO User VALUES (?, ?, ?, ?, ?, ?, ?)", data)
        db.commit()
    except:
        return {"success": False, "message": "User already exists."}

    notify_all_users()

    return {"success": True, "message": "Successfully created a new user."}


def sign_in_user(d):
    data = (d['email'], d['password'])
    client_public_key = int(d['public_key'])

    try:
        db = get_db()
        c = db.cursor()
    except:
        return {"success": False, "message": "Database problems."}

    c.execute("SELECT COUNT(*) FROM User WHERE Email=? AND Password=?", data)
    if c.fetchone()[0] == 1:
        server_public_key = helper.compute_public_key()

        secret_key = helper.compute_secret_key(client_public_key,
                                               server_public_key['secret_variable'])

        token = helper.generate_random_token()
        storage.add_user(token, d['email'], secret_key)
        
        return {"success": True, "message": "Successfully signed in.",
                "data": token, "key": server_public_key['public_key']}

    return {"success": False, "message": "Wrong username or password."}


def sign_out_user(m):
    if 'forced' in m['data']:
        d = m['data']
        helper.log('forced')
        helper.log(d)
    else:
        d = m['data']
        h = m['hash']
        helper.log('not forced')
        helper.log(d)
        helper.log(h)

        if not helper.is_legid(d, h):
            return {"success": False, "message": "You're not autorized to see this."}


    token = d['token']
    helper.log(token)
    try:
        if d['forced']:
            forced = True
        else:
            forced = False
    except:
        forced = False

    if storage.is_token_presented(token):
        email = storage.get_user_email(token)
        storage.remove_user(token)
        if not forced:
            socket_pool.remove_socket(email)
        
        notify_all_users()

        return {"success": True, "message": "Successfully signed out."}


    return {"success": False, "message": "You are not signed in."}

def change_password(m):
    d = m['data']
    h = m['hash']

    if not helper.is_legid(d, h):
        return {"success": False, "message": "You're not autorized to see this."}

    token = d['token']
    old_pass = d['old_password']
    new_pass = d['new_password']

    email = storage.get_user_email(token)

    if not email:
        return {"success": False, "message": "You are not logged in."}

    try:
        db = get_db()
        c = db.cursor()
    except:
        return {"success": False, "message": "Database problems."}

    c.execute("SELECT COUNT(*) FROM User WHERE Email=? AND Password=?",
                                                         (email, old_pass))
    # there is such user with such password
    if c.fetchone()[0] == 1:
        c.execute("UPDATE User SET Password=? WHERE Email=? AND Password=?",
                                            (new_pass, email, old_pass))
        db.commit()
        return {"success": True, "message": "Password changed."}
    
    return {"success": False, "message": "Wrong password."}

def get_user_data_by_email(d):
    # d = m['data']
    # h = m['hash']

    # if not helper.is_legid(d, h):
    #     return {"success": False, "message": "You're not autorized to see this."}

    token = d['token']
    email = d['email']

    if not storage.is_token_presented(token):
        return {"success": False, "message": "You are not signed in."}

    try:
        db = get_db()
        c = db.cursor()
    except:
        return {"success": False, "message": "Database problems."}

    c.execute("SELECT * FROM User WHERE Email=?", (email,))

    match = c.fetchone()
    if not match:
        return {"success": False, "message": "No such user."}

    data = {'email': match[0], 'firstname': match[2], 'familyname': match[3], 
            'gender': match[4], 'city': match[5], 'country': match[6]}

    return {"success": True, "message": "User data retrieved.", "data": data}

def get_user_data_by_token(d):
    # d = m['data']
    # h = m['hash']

    # if not helper.is_legid(d, h):
    #     return {"success": False, "message": "You're not autorized to see this."}

    token = d['token']

    email = storage.get_user_email(token)

    return get_user_data_by_email({'token': token, 'email': email})

def post_message(m):
    d = m['data']
    h = m['hash']

    if not helper.is_legid(d, h):
        return {"success": False, "message": "You're not autorized to see this."}

    token = d['token']
    message = d['message']
    to_email = d['email']

    from_email = storage.get_user_email(token)
    if not from_email:
        return {"success": False, "message": "You are not signed in."}

    try:
        db = get_db()
        c = db.cursor()
    except:
        return {"success": False, "message": "Database problems."}

    c.execute("SELECT COUNT(*) FROM User WHERE Email=?", (to_email, ))
    if c.fetchone()[0] != 1:
        return {"success": False, "message": "No such user."}


    c.execute('INSERT INTO Message(To_email, From_email, Content) VALUES (?, ?, ?)',
                                                    (to_email, from_email, message))
    db.commit()


    token_of_receiver = storage.get_token_by_email(to_email)
    if token_of_receiver:
        notify_user(token_of_receiver[0])

    return {"success": True, "message": "Message posted"}

def get_user_messages_by_email(m, local=False):
    # local means this this query is from internal source and there is
    # no need to check legitimacy of user
    if not local:
        d = m['data']
        h = m['hash']

        if not helper.is_legid(d, h):
            return {"success": False, "message": "You're not autorized to see this."}
    else:
        d = m

    token = d['token']
    email = d['email']

    if not storage.get_user_email(token):
        return {"success": False, "message": "You are not signed in."}

    try:
        db = get_db()
        c = db.cursor()
    except:
        return {"success": False, "message": "Database problems."}

    c.execute("SELECT COUNT(*) FROM User WHERE Email=?", (email, ))
    if c.fetchone()[0] != 1:
        return {"success": False, "message": "No such user."}

    c.execute("SELECT * FROM Message WHERE To_email=?", (email, ))
    match = map(lambda x: {'writer': x[2], 'content': x[3]}, c.fetchall())

    return {"success": True, "message": "User messages retrieved.", "data": match}

def get_user_messages_by_token(m, local=False):
    if local:
        d = m
    else:
        d = m['data']
        h = m['hash']

        if not helper.is_legid(d, h):
            return {"success": False, "message": "You're not autorized to see this."}

    token = d['token']

    email = storage.get_user_email(token)

    return get_user_messages_by_email({'token': token, 'email': email}, True)

def notify_user(token):
    data = collect_information(token)
    stats_info.notify_by_token(token, data)

def notify_all_users():
    helper.log('starting notifying each one')

    tokens = stats_info.all_subscribers()
    helper.log(tokens)
    for t in tokens:
        data = collect_information(t)
        helper.log(data)
        stats_info.notify_by_token(t, data)
    helper.log('notified already')

def collect_information(token):
    registered = _get_number_of_registered_users()
    
    posts = get_user_messages_by_token({'token': token}, True)
    if posts['success']:
        num_posts = len(posts['data'])
    else:
        num_posts = None
    
    online = socket_pool.size()

    all_posts = _get_number_of_all_posts()

    return {'all_users': registered, 'online': online, 'posts': num_posts,
            'all_posts': all_posts}

def _get_number_of_registered_users():
    db = get_db()
    c = db.cursor()

    c.execute("SELECT COUNT(*) FROM User")
    
    return c.fetchone()[0]

def _get_number_of_all_posts():
    db = get_db()
    c = db.cursor()

    c.execute("SELECT COUNT(*) FROM Message")

    return c.fetchone()[0]