
import json
import datetime
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#creating sqlite db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)



class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    availCash = db.Column(db.Integer)
    
    def __repr__(self):
        return (""+str(self.id) + " " + self.name + 
                ". Available cash is: "+ str(self.availCash))
  
 
@app.route("/accounts")
def getAccounts():
    accounts = Account.query.all()
    output = []
    for acc in accounts:
        accData = {"id":acc.id, "name":acc.name, "availCash":acc.availCash}
        output.append(accData)
    return {"accounts":output}


@app.route("/accounts", methods=["POST"])
def addAccount():
    acc = Account(name=request.json["name"], availCash=request.json["availCash"])
    db.session.add(acc)
    db.session.commit()
    return {"id":acc.id}


def addAccount2(newID, newName, newAvailCash):
    acc = Account(id = newID, name=newName, availCash=newAvailCash)
    db.session.add(acc)
    db.session.commit()
    return {"id":acc.id}


@app.route("/accounts/<id>", methods=["DELETE"])
def deleteAccount(id):
    acc = Account.query.get(id)
    db.session.delete(acc)
    db.session.commit()
    return {"it" : "works"}


def deleteAccount2(id):
    acc = Account.query.get(id)
    db.session.delete(acc)
    db.session.commit()
    return {"it is": "deleted"}



class Transaction3(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cashAmount = db.Column(db.Integer)
    sourceAccount  = db.Column(db.Integer) #id of account
    destinationAccount = db.Column(db.Integer)
    regTime = db.Column(db.String(120))
    success = db.Column(db.Boolean)
    
    def __repr__(self):
        return (""+str(id) + " " + str(self.cashAmount) + " from: "+
                str(self.sourceAccount) + " to: " + str(self.destinationAccount)
                +" "+str(self.regTime))


@app.route("/transactions")
def getTransactions():
    transactions = Transaction3.query.all()
    output = []
    for transaction in transactions:
        transactionData = {"id": transaction.id,
                           "cashAmount":transaction.cashAmount, 
                           "sourceAccount":transaction.sourceAccount,
                           "destinationAccount":transaction.destinationAccount,
                           "regTime":transaction.regTime,
                           "success":transaction.success}
        output.append(transactionData)
    return {"transactions":output}


@app.route("/transactions", methods=["POST"])
def addTransaction():
    sourceAccountID=request.json["sourceAccount"]
    cashAmount=request.json["cashAmount"]
    destinationAccountID=request.json["destinationAccount"]
    newSuccess = True
    newRegTime = str(datetime.datetime.now())
    
    #using get_or_404, if you try transaction with account that does not exist you get 404 error, 
    #could probably have just checked if account exists, if no -> newSuccess=False, then made 
    #transaction with that, but i thought it didnt make sense to have transaction between acounts
    #that doesnt exist
    sourceAccount = Account.query.get_or_404(sourceAccountID)
    destinationAccount = Account.query.get_or_404(destinationAccountID)
    
    #i assumed you still wanted the transaction to go through, without sending money and success = False
    if (sourceAccount.availCash < cashAmount):
        newSuccess=False
    
    trans = Transaction3(cashAmount=cashAmount, 
                        sourceAccount = sourceAccountID, 
                        destinationAccount=destinationAccountID,
                        regTime=newRegTime,
                        success=newSuccess)
    db.session.add(trans)
    db.session.commit()


    #code for output
    output ={"id": trans.id,
              "cashAmount":trans.cashAmount, 
              "sourceAccount":trans.sourceAccount,
              "destinationAccount":trans.destinationAccount,
              "regTime":trans.regTime,
               "success":trans.success}
    
    #Bemerkning:
    #innser jo her at accountnavn ikke er frivillig lenger, kan fikses med å enten lagre accountnavn
    #variabelen, kan også bruke accountnavn til å søke (siden det er jo unikt)
    
    #if we have enough money, to decide if 200 or 400
    if (sourceAccount.availCash >= cashAmount):
        #removing money from sourceaccount
        newAccountName="account"+str(sourceAccountID)
        newAccountMoney = int(sourceAccount.availCash) - cashAmount
        deleteAccount2(sourceAccountID)
        addAccount2(sourceAccountID,newAccountName , newAccountMoney)
        
        #adding money to destinationaccount
        newAccountName ="account"+str(destinationAccountID)
        newAccountMoney=int(destinationAccount.availCash)+cashAmount
        deleteAccount2(destinationAccountID)
        addAccount2(destinationAccountID, newAccountName, newAccountMoney)
    
        return {200 : output}
    return {400 :output}


@app.route("/transactions/<id>", methods=["DELETE"])
def deleteTransaction(id):
    #retrieve the account object
    trans = Transaction3.query.get(id)
    db.session.delete(trans)
    db.session.commit()
    return {"Deleted transaction: " : id}

















"""
IGNORE THIS:

#plan:
    lage to classes: accountModel, transactionModel
    -> hardkod inn noen accountModels
    legge inn alle verdiene deres (vurder om type til de har noe å si)
    pass på det med 200 og 400 response
    endre databasenavnet til data2 kanskje?
    
    etter overføring av penger, return availableCash til begge kontoene så du kan 
    sjekke at alt gikk greit
    
    pass på rare tilfeller (negativ balance f.eks)
    
    
    

#TODO

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cashAmount = db.Column(db.Integer)
    sourceAccount  = db.Column(db.Integer) #id of account
    destinationAccount = db.Column(db.Integer)
    #regTime = db.Column(db.String(120))
    #success = db.Column(db.Boolean)
    def __repr__(self):
        return (""+str(id) + " " + str(self.cashAmount) + " from: "+
                str(self.sourceAccount) + " to: " + str(self.destinationAccount))


@app.route("/transactions")
def getTransactions():
    transactions = Transaction.query.all()
    output = []
    for transaction in transactions:
        transactionData = {"id": transaction.id,
                           "cashAmount":transaction.cashAmount, 
                           "sourceAccount":transaction.sourceAccount,
                           "destinationAccount":transaction.destinationAccount}
        output.append(transactionData)
    return {"transactions":output}

@app.route("/transactions", methods=["POST"])
def addTransaction():
    sourceAccountID=request.json["sourceAccount"]
    cashAmount=request.json["cashAmount"]
    destinationAccountID=request.json["destinationAccount"]
    #success = True
    #newRegTime = "now"#str(datetime.datetime.now())
    trans = Transaction(cashAmount=cashAmount, 
                        sourceAccount = sourceAccountID, 
                        destinationAccount=destinationAccountID)
    db.session.add(trans)
    db.session.commit()

    #validation
    sourceAccount = Account.query.get_or_404(sourceAccountID)
    destinationAccount = Account.query.get_or_404(destinationAccountID)
    #check accounts are there
    #use get 404
    
    #chcek that there is enough money, still add transaction to transaction table
    if (sourceAccount.availCash < cashAmount):
        return "You do not have high enough cash balance ", 400 #see 400 in powershell
    
    
    
    #removing money from sourceAccount
    
    newAccountName="account"+str(sourceAccountID)
    newAccountMoney = int(sourceAccount.availCash) - cashAmount
    deleteAccount2(sourceAccountID)
    addAccount2(sourceAccountID,newAccountName , newAccountMoney)
    
    #adding money
    
    newAccountName ="account"+str(destinationAccountID)
    newAccountMoney=int(destinationAccount.availCash)+cashAmount
    deleteAccount2(destinationAccountID)
    addAccount2(destinationAccountID, newAccountName, newAccountMoney)
    
    return {"id":trans.id}

@app.route("/transactions/<id>", methods=["DELETE"])
def deleteTransaction(id):
    #retrieve the account object
    trans = Transaction.query.get(id)
    db.session.delete(trans)
    db.session.commit()
    return {"it" : "works"}















@app.route("/drinks/<id>", methods=["DELETE"])
def deleteDrink(id):
    drink = Drink.query.get(id)
    if drink is None:
        return {"error":"not found"}
    db.session.delete(drink)
    db.session.commit()
    return {"message":"yayeet"}


@app.route("/accounts", methods=["POST"])
def removeMoney(cashAmount, sourceAccountID):
    #spør inputen vi legger inn
    #cashAmount = request.json["cashAmount"]
    account = Account.query.get_or_404(sourceAccountID)
    newCashAmount = account.availCash < cashAmount
    if (newCashAmount <0):
        return {"error" : "not enough money"}
    account = Account(name = account.name, cashAmount=newCashAmount)
    return {"newMoney is: " : newCashAmount}
    
   



@app.route("/drinks/<id>")
def getDrink(id):
    drink = Drink.query.get_or_404(id)
    #kan måtte bruke jsonify hvis du ikke jobber med en dictonary
    return {"name":drink.name, "description":drink.description}



@app.route("/drinks", methods=["POST"])
def add_drink():
    drink = Drink(name=request.json["name"], description=request.json["description"])
    db.session.add(drink)
    db.session.commit()
    return {"id":drink.id}  

@app.route("/drinks")
def getDrinks():
    drinks = Drink.query.all()
    output = []
    for drink in drinks:
        drinkData = {"name":drink.name, "description":drink.description}
        output.append(drinkData)
        
    
    return {"drinks":output}

def removeMoney(accountID, cashAmount):
    #remove money from account
def addMoney(accountID, cashAmount):
 

@app.route("/drinks/<id>")
def getDrink(id):
    drink = Drink.query.get_or_404(id)
    #kan måtte bruke jsonify hvis du ikke jobber med en dictonary
    return {"name":drink.name, "description":drink.description}


@app.route("/")
def index():
    return "Hello"



class Drink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120))
    
    def __repr__(self):
        return ("" + self.name+ " - "+ self.description)
    
@app.route("/drinks", methods=["POST"])
def add_drink():
    drink = Drink(name=request.json["name"], description=request.json["description"])
    db.session.add(drink)
    db.session.commit()
    return {"id":drink.id}   



@app.route("/drinks")
def getDrinks():
    drinks = Drink.query.all()
    output = []
    for drink in drinks:
        drinkData = {"name":drink.name, "description":drink.description}
        output.append(drinkData)
        
    
    return {"drinks":output}
"""