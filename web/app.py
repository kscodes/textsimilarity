from flask import Flask,jsonify, request
from flask_restful import Api,Resource
from pymongo import MongoClient
import bcrypt
import spacy

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://db:27017')
db = client.SimDB #similarity database
users=db['Users']

def isPresentUser(username):
    if users.find({"Username" : username}).count() == 0 :
        return False
    else:
        return True



class Register(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        if isPresentUser(username):
            retDict = {
                "status" : 301,
                "msg" : "Invalid Username"
            }
            return jsonify(retDict)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'),bcrypt.gensalt())

        users.insert({
            "Username":username,
            "Password": hashed_pw,
            "Tokens" : 6
        })

        retDict = {
            "status" : 200,
            "msg" : "Signup Succesful"
        }

        return jsonify(retDict)

def verifyPw(username,password):
    hashed_pw = users.find({
        "Username" : username
    })[0]["Pas  sword"]

    if bcrypt.hashpw(password.encode('utf8'),hashed_pw)==hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    return users.find({
        "Username":username
    })[0]["Tokens"]

class Check(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData['username']
        password = postedData['password']
        text1 = postedData['text1']
        text2 = postedData['text2']

        if not isPresentUser(username):
            retDict ={
            "status" : 301,
            "msg" : "Invalid username"
            }
            return jsonify(retDict)

        chk_passwd = verifyPw(username,password)

        if not chk_passwd :
            retDict = {
                "status" : 302,
                "msg" : "Invalid password"
            }
            return jsonify(retDict)

        curr_tokens = countTokens(username)

        if curr_tokens <=0 :
            retDict ={
                "status" : 303,
                "msg" : "Please refill tokens"
            }
            return jsonify(retiDict)

        users.update({
            "Username":username,
        },{
          "$set":{
                "Tokens" : curr_tokens-1
           }
        })

        nlp = spacy.load('en_core_web_sm')#loading the model

        text1 = nlp(text1)
        text2 = nlp(text2)

        ratio = text1.similarity(text2)

        retDict = {
            "status" : 200,
            "equivalency/similarity" : ratio,
            "msg" : "Similarity score calculated succesfully"
        }
        return jsonify(retDict)

class Refill(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData['username']
        password = postedData['admin_passwd']
        refill_amt = postedData['refill_amt']

        if not isPresentUser(username):
            retDict = {
                "status" : 301,
                "msg" : "Invalid Username"
            }
            return jsonify(retDict)

        correct_pw = "911jacob"
        if not password == correct_pw:
            retDict = {
                "status" : 304,
                "msg" : "Invalid Admin Password"
            }
            return jsonify(retDict)

        curr_tokens = countTokens(username)
        users.update({
            "Username" : username
        },{
            "$set" : {
                "Tokens" : curr_tokens + refill_amt
            }
        })

        retDict = {
            "status" : 200,
            "msg" : "Refill succesful"
        }
        return jsonify(retJson)

api.add_resource(Register,'/register')
api.add_resource(Check,'/check')
api.add_resource(Refill,'/refill')

if __name__=="__main__":
    app.run(host='0.0.0.0')
