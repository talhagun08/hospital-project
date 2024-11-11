import json
from flask import Flask, request, jsonify
import datetime
import hashlib
import sqlite3

app = Flask(__name__)

# TOKEN CONTROL
def token_control(token):
    database = sqlite3.connect('C:\Databases\hospital.db3')
    cursor = database.cursor()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    token_var = cursor.execute("SELECT * FROM TOKEN WHERE TOKEN=:token AND CAST(strftime('%s', TIMER) AS integer) >= CAST(strftime('%s', :current_time) AS integer)",
                              {"token":token,"current_time":current_time}).fetchone()
    if (token_var is not None):
        timer = (datetime.datetime.now() + datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE TOKEN SET TIMER=:timer WHERE ID=:id",{"timer":timer, "id":int(token_var[0])})
        database.commit()
        database.close()
        return True
    else:
        database.close()
        return False

# LOGIN

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    user_name = data["user_name"]
    user_password = data["user_password"]
    try:
        database = sqlite3.connect('C:\Databases\hospital.db3')
        cursor = database.cursor()
        session = cursor.execute('SELECT * FROM USER WHERE USER_NAME=:user_name AND USER_PASSWORD=:user_password',
                               {"user_name": user_name, "user_password": user_password}).fetchone()

        if (session is not None):
            token_ham = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(session[0]) + session[1] + session[2]
            token = hashlib.md5(token_ham.encode()).hexdigest()
            timer = (datetime.datetime.now() + datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                'INSERT INTO TOKEN (TOKEN,USER_NAME,TIMER) VALUES (:token,:user_name,:timer)',
                {"token": token, "user_name": int(session[0]), "timer": timer})
            database.commit()
            database.close()
            return {"Result": token}
        else:
            database.close()
            return {"sonuc": "Başarısız"}, 403

    except Exception as e:
        return {"hata": str(e)}, 500




# ADD USER
@app.route('/api/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    user_name=data["user_name"]
    user_password = data["user_password"]
    try:
        database = sqlite3.connect('C:\Databases\hospital.db3')
        cursor= database.cursor()
        cursor.execute('INSERT INTO USER (USER_NAME, USER_PASSWORD) VALUES (?,?)',(user_name, user_password))
        database.commit()
        database.close()
        return {"Result": "Successfuly Added"},201
    except Exception as e:
        return {"Error": str(e)},500

#------------------------------------------------------------------------------------------------------------------------------------------



# ADD PATIENT
@app.route('/api/add_patient', methods =["POST"])
def add_patiance():
    data = request.get_json()
    patient_name = data["patient_name"]
    patient_city = data["patient_city"]
    patient_id_number = data["patient_id_number"]
    token = data["token"]
    if(token_control(token)==True):

        try:
            database = sqlite3.connect('C:\Databases\hospital.db3')
            cursor = database.cursor()
            cursor.execute('INSERT INTO PATIENT (PATIENT_NAME, PATIENT_CITY, PATIENT_ID_NUMBER) VALUES (?, ?, ?)', (patient_name, patient_city, patient_id_number))
            database.commit()
            database.close()
            return {"Result":"Successfuly added."}, 201
        except Exception as e:
            return {"Error": str(e)}, 500

    else:
        return {"Result": "Unauthorized Access"}

# LIST PATIENT
@app.route('/api/list_patient', methods=["POST"])
def list_patiance():
    data = request.get_json()
    token = data["token"]
    if (token_control(token)==True):
        try:
            database = sqlite3.connect('C:\Databases\hospital.db3')
            database.row_factory = sqlite3.Row
            cursor = database.cursor()
            datas = cursor.execute("SELECT * FROM PATIENT ").fetchall()
            database.commit()
            database.close()
            result =  json.dumps([dict(ix) for ix in datas ], ensure_ascii=False)
            return result, 201
        except Exception as e:
            return {"hata": str(e)}, 500
    else:
        return {'Result':"Unauthorized Access"}
# EDIT PATIENT
@app.route('/api/edit_patient', methods = ['POST'])
def edit_patient():
    data = request.get_json()
    patient_id = data["patient_id"]
    patient_name = data["patient_name"]
    patient_city = data["patient_city"]
    patient_id_number = data["patient_id_number"]
    token = data["token"]
    if (token_control(token)== True):
        try:
            database = sqlite3.connect('C:\Databases\hospital.db3')
            cursor = database.cursor()
            cursor.execute('UPDATE PATIENT SET PATIENT_NAME=:patient_name, PATIENT_CITY=:patient_city, PATIENT_ID_NUMBER=:patient_id_number WHERE PATIENT_ID=:patient_id', {"patient_name":patient_name, "patient_city":patient_city, "patient_id_number":patient_id_number, "patient_id":str(id)})
            database.commit()
            database.close()
            return {"Result":"Successfuly Updated"},201
        except Exception as e:
            return {"Error": str(e)},500
    else:
        return {"Result": "Unauthorized Access"}



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=2500)
