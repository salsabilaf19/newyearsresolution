from flask import Flask, render_template, request, jsonify, url_for, redirect, session
from pymongo import MongoClient
import bcrypt


client = MongoClient('mongodb+srv://test:sparta@cluster0.1wag9ha.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta
records = db.users

app = Flask(__name__)

@app.route('/', methods=['post', 'get'])
def home():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            records.insert_one(user_input)
            
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
   
            return render_template('logged_in.html', email=new_email)
    return render_template('index.html')

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

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)