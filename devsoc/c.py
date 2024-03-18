from flask import Flask, render_template, request, jsonify,session
from pymongo import MongoClient
from bson import ObjectId
app = Flask(__name__)
app.secret_key = 'abc'
# Assuming MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['eats']
collection_food=db['food_data']
collection_user=db['userdata']
collection_ngo=db['ngodata']


@app.route("/food_sell")
def index():
    return render_template("restaurant.html")

@app.route("/ngo")
def ngo():
    return render_template("ngo.html")
@app.route("/ngopost",methods=["POST"])
def ngopost():
    if session.get("id"):
        ngoname = request.form.get("ngoname")
        contactperson = request.form.get("contactperson")
        phone = request.form.get("phone")
        email = request.form.get("email")
        foodneed = request.form.get("foodneed")
        data={
            'ngoname':ngoname,
            'contactperson':contactperson,
            'phone':phone,
            'email':email,
            'foodneed':foodneed
        }
        user_id = session.get("id")   # Example user ID
        latitude = request.args.get("latitude")  # Access latitude from form data
        longitude = request.args.get("longitude")
        data['location'] = [latitude, longitude]
        data["userdata"]=user_id
        collection_ngo.insert_one(data)
        return jsonify({"message":"successful"})
    else:
        return jsonify({"message":"unsuccessful"})

    
@app.route("/submit_form", methods=["POST"])
def submit_form():
    if(session.get("id")):
        names = request.form.getlist("name_item[]")
        quantities = request.form.getlist("quantity[]")
        prices = request.form.getlist("price[]")
        expirydates = request.form.getlist("expirydate[]")
        descriptions = request.form.getlist("description[]")

        user_id = session.get("id")  # Example user ID
        latitude = request.args.get("latitude")  # Access latitude from form data
        longitude = request.args.get("longitude")  # Access longitude from form data

        data = {
            'userdata': user_id,
            'items': []
        }

        for name, quantity, price, expirydate, description in zip(names, quantities, prices, expirydates, descriptions):
            item = {
                'itemname': name,
                'quantity': quantity,
                'price': price,
                'expirydate': expirydate,
                'description': description
            }
            data['items'].append(item)

        data['location'] = [latitude, longitude]

        # collection_food = db["food_data"]
        collection_food.insert_one(data)

        return jsonify({"message": "successfully"})
    else:
        return jsonify({"message":"unsuccessful"})
@app.route("/map")
def map():
    document_food=collection_food.find()
    
    it=list(document_food)
    # print(it)
    for i in it:
        i["_id"]=str(i["_id"])
        document_user=collection_user.find_one({"_id":ObjectId(i["userdata"])})
        i['userdata']=document_user["username"]
        i['number']=document_user['number']
    print(it)

    document_ngo=collection_ngo.find()
    itngo=list(document_ngo)
    for i in itngo:
        i["_id"]=str(i["_id"])
        document_user=collection_user.find_one({"_id":ObjectId(i["userdata"])})
        i['userdata']=document_user["username"]
        i['number']=document_user['number']
    print(itngo)
    return render_template("order.html",item=it,itemngo=itngo)
  
@app.route("/login")
def login():
    return render_template('login.html')
@app.route("/signup")
def signup():
    return render_template('signup.html')
@app.route("/signup",methods=["POST"])
def signuppost():
    name=request.form.get("name")
    uname=request.form.get("uname")
    mail=request.form.get("mail")
    phone=request.form.get("phone")
    userpassword=request.form.get("userpassword")
    
    
    data={
        "name":name,
        "username":uname,
        "number":phone,
        "password":userpassword,
        "email":mail

    }
    collection_user.insert_one(data)
    return render_template('login.html')
@app.route('/')
def ind():
    if(session.get("id")):
        doc=collection_user.find({"_id":ObjectId(session.get("id"))})
        return render_template("index.html")
    return 
@app.route('/signout')
def signout():
    session.pop("id")
    return render_template("index.html")
@app.route("/login",methods=["POST"])
def loginpost():
    email=request.form.get("mail")
    
    userpassword=request.form.get("userpassword")
    print(email+userpassword)
    
    data={
        "email":email,
        "password":userpassword

    }
    
    doc=collection_user.find_one(data)
    print(doc)
    if doc:
        session["id"]=str(doc["_id"])
        print(str(doc["_id"]))
        print(session.get("id"))
    return jsonify("successful")

if __name__ == "__main__":
    app.run(debug=True)
