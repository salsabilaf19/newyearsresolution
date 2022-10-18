from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.1wag9ha.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

app = Flask(__name__)

@app.route('/')
def home():
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
        'date': date_receive
    }
    db.newyearsresolution.insert_one(doc)
    return jsonify({'msg':'Data saved!'})

@app.route("/delete", methods=["POST"])
def delete_bucket():
    num_receive = request.form['num_give']
    db.newyearsresolution.delete_one({'num': int(num_receive)})
    return jsonify({'msg': 'delete done!'})
    
@app.route("/bucket/done", methods=["POST"])
def bucket_done():
    num_receive = request.form["num_give"]
    db.newyearsresolution.update_one(
        {'num': int(num_receive)},
        {'$set': {'done': 1}}
    )
    return jsonify({'msg': 'Update done!'})

@app.route("/target", methods=["GET"])
def target_get():
    target_list = list(db.newyearsresolution.find({},{'_id':False}))
    return jsonify({'targets':target_list})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)