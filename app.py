from flask import Flask, render_template, request, jsonify,session, redirect,url_for
from pymongo import MongoClient
import bcrypt

client = MongoClient('mongodb+srv://test:sparta@cluster0.1wag9ha.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta
records = db.users

app = Flask(__name__)
app.secret_key = "testing"

# jadi ini rute untuk ke new year nya
# @app.route('/halamanlogin')
# def home():
#    return render_template('login.html')

@app.route("/SaveTarget", methods=["POST"])
def save_target():
    target_receive = request.form["target_give"]
    date_receive = request.form["date_give"]

    count = db.newyearsresolution.count_documents({})
    num = count + 1
    doc = {
        'num':num,
        'target': target_receive,
        'date': date_receive,
        'done': 0
    }
    db.newyearsresolution.insert_one(doc)
    return jsonify({'msg':'Data saved!'})


@app.route("/delete", methods=["POST"])
def delete_target():
    num_receive = request.form['num_give']
    db.newyearsresolution.delete_one({'num': int(num_receive)})
    return jsonify({'msg': 'deleted or completed target !'})

    
@app.route("/TargetDone", methods=["POST"])
def bucket_done():
    num_receive = request.form["num_give"]
    db.newyearsresolution.update_one(
        {'num': int(num_receive)},
        {'$set': {'done': 1}}
    )
    return jsonify({'msg': 'Target done!'})

@app.route("/CancelDone", methods=["POST"])
def cancel_done():
    num_receive = request.form["num_give"]
    db.newyearsresolution.update_one(
        {'num': int(num_receive)},
        {'$set': {'done': 0}}
    )
    return jsonify({'msg': 'Target done!'})

@app.route("/update", methods=["POST"])
def update_target():
    num_receive = request.form['num_give']
    target_receive = request.form['target_give']
    date_receive = request.form['date_give']
    db.newyearsresolution.update_one(
        {'num': int(num_receive)},
        {'$set': {
            'target': target_receive,
            'date': date_receive
            }}
    )
    return jsonify({'msg': 'Update success!'})

@app.route("/target", methods=["GET"])
def target_get():
    target_list = list(db.newyearsresolution.find({},{'_id':False}))
    return jsonify({'targets':target_list})


# nah ini tuh bentrok sama yang route new years resolution, makanya ku kasih /1
@app.route("/regist", methods=['post', 'get'])
def index():
    message = ''
    #if method post in index
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        #if found in database showcase that it's found 
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There is already a user using that name'
            return render_template('index1.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index1.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index1.html', message=message)
        else:
            #hash the password and encode it
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            #assing them in a dictionary in key value pairs
            user_input = {'name': user, 'email': email, 'password': hashed}
            #insert it in the record collection
            records.insert_one(user_input)
            
            #find the new created account and its email
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            #if registered redirect to logged in as the registered user
            
            # NAH DISINI ITU HARUSNYA SETTING KE NEWYEARSRESOLUTION(INDEX.HTML)
            return render_template('logged_in.html', email=new_email)
    return render_template('index1.html')

@app.route("/", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            #encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('index.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("login.html")
    else:
        return render_template('login.html')


if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)