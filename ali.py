
from datetime import date, time
from flask import Flask, flash
from flask import jsonify, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flaskext.mysql import MySQL
from pymysql import cursors
from werkzeug.datastructures import *

# Mysql Connection
mysql = MySQL()

app = Flask(__name__)


# Uplaod Images and Documents Folder
UPLOAD_FOLDER = '//static//userData'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# mysql config
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = ''
# app.config["MYSQL_DATABASE_DB"] = "doctorproject"
app.config["MYSQL_DATABASE_DB"] = "coin"
app.config["MYSQL_DATABASE_HOST"] = "localhost"
mysql.init_app(app)
app.secret_key = '123456789'

########## user authentication ############



@app.route('/login', methods=["GET","POST"])
def loginn():
    if session.get("username"):
        return redirect(url_for("home"))
    else:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            print(username,password)
            conn = mysql.connect()
            cur = conn.cursor()
            cur.execute(" select * from user where user_name=%s;",[username])
            data = cur.fetchone()
            cur.close()
            conn.close()
            if data != None:
                if data[3] == password:
                    session["username"] = data[2]
                    session["user_id"] = data[0]
                    #session["status"] = data[4]
                    return redirect(url_for("home"))
                
                else:
                    session["error"] = "password doesn't match."
                    return redirect(url_for("loginn"))
            else:
                session["error"] = "user not exist."
                error = ""
                if session.get("error"):
                    error = session.get("error")
                
                
                return redirect(url_for("loginn"))
        else:
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)

            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)
            return render_template("login.html", error=error)



@app.route("/logout",methods=["GET","POST"])
def logout():
    session.pop("username", None)
    return redirect(url_for("loginn"))


@app.route('/home', methods =["POST", "GET"])
def home():
    return render_template("dashboard.html")


@app.route("/buy",methods=["GET","POST"])
def buy():
    if request.method == "POST":
        date = request.form.get("date")
        coin = request.form.get("coin")
        quantity = request.form.get("quantity")
        coin_value = request.form.get("coin_value")
        purchasing_time = request.form.get("purchasing_time")
        purchasing_timee = purchasing_time.split(":")[0]
        if int(purchasing_timee) <= 12:
            purchasing_time = str(purchasing_time) + " " + "am"
            print(purchasing_time)
        else:
            purchasing_time = str(purchasing_time) + " " + "pm"
            print(purchasing_time)

        con = mysql.connect()
        cur = con.cursor()
        cur.execute(""" insert into buy (date,coin,quantity,coin_value, time) values(%s,%s,%s,%s,%s) ;""",[date,coin,quantity,coin_value,purchasing_time])
        con.commit()
        con.close()
        cur.close()
        return redirect("/buy")
    else:
        status = session.get("status")
        con = mysql.connect()
        cur = con.cursor()
        cur.execute(""" select * from buy ;""")
        data = cur.fetchall()
        con.close()
        cur.close()
        if status == "super_admin":
            header = ["S.NO","BUYING DATE","BUYING TIME","QUANTITY","COIN VALUE","COIN","EDIT","DELETE"]
        else:
            header = ["S.NO","BUYING DATE","BUYING TIME","QUANTITY","COIN VALUE","COIN"]


        return render_template("buy.html",data=data,header=header,status=status)


@app.route("/buy-edit",methods=["GET","POST"])
def buyEdit():
    if request.method == "POST":
        sno = request.form.get("sno")
        coin = request.form.get("coin")
        date = request.form.get("date")
        quantity = request.form.get("quantity")
        coin_value = request.form.get("coin_value")
        purchasing_time = request.form.get("purchasing_time")
        con = mysql.connect()
        cur = con.cursor()
        cur.execute(""" update buy SET date=%s,coin=%s,quantity=%s,coin_value=%s,time=%s where sno=%s;""",[date,coin,quantity,coin_value,purchasing_time,sno])
        con.commit()
        con.close()
        cur.close()
        return redirect("/buy")
    else:
        user_id = request.args.get("id")
        con = mysql.connect()
        cur = con.cursor()
        cur.execute(""" select * from buy where sno=%s ;""",[user_id])
        data = cur.fetchone()
        data2 = data[2]
        data2 = data2.split(" ")[0]
        print(data2)
        con.close()
        cur.close()
        print(data)
        return render_template("edit-buy.html",data2=data,data3=data2)


@app.route("/buy-delete")
def buyDelete():
    user_id = request.args.get("id")
    con = mysql.connect()
    cur = con.cursor()
    cur.execute(""" delete from buy where sno=%s""",[user_id])
    con.commit()
    cur.close()
    con.close()
    return redirect("/buy")




@app.route("/sell-add",methods=["GET","POST"])
def sellAdd():
    if request.method == "POST":
        date = request.form.get("date")
        coin = request.form.get("coin")
        quantity = request.form.get("quantity")
        coin_value = request.form.get("coin_value")
        purchasing_time = request.form.get("purchasing_time")
        purchasing_timee = purchasing_time.split(":")[0]
        if int(purchasing_timee) <= 12:
            purchasing_time = str(purchasing_time) + " " + "am"
            print(purchasing_time)
        else:
            purchasing_time = str(purchasing_time) + " " + "pm"
            print(purchasing_time)
        con = mysql.connect()
        cur = con.cursor()
        cur.execute(""" insert into sell (date,coin,quantity,coin_value,time) values(%s,%s,%s,%s,%s)""",[date,coin,quantity,coin_value,purchasing_time])
        con.commit()
        con.close()
        cur.close()
        return redirect("/sell-add")
    else:
        status = session.get("status")
        if status == "super_admin":
            header = ["S.NO","DATE","COIN","QUANTITY","COIN VALUE","SELLING TIME","EDIT","DELETE"]
        else:
            header = ["S.NO","DATE","COIN","QUANTITY","COIN VALUE","SELLING TIME"]

        con = mysql.connect()
        cur = con.cursor()
        cur.execute(""" select * from sell ;""")
        data = cur.fetchall()
        return render_template("sell-add.html",header=header,data=data,status=status)



@app.route("/sell-edit",methods=["GET","POST"])
def sellEdit():
    if request.method == "POST":
        sno = request.form.get("sno")
        date = request.form.get("date")
        coin = request.form.get("coin")
        quantity = request.form.get("quantity")
        coin_value = request.form.get("coin_value")
        purchasing_time = request.form.get("purchasing_time")
        purchasing_timee = purchasing_time.split(":")[0]
        if int(purchasing_timee) <= 12:
            purchasing_time = str(purchasing_time) + " " + "am"
            print(purchasing_time)
        else:
            purchasing_time = str(purchasing_time) + " " + "pm"
            print(purchasing_time)
        con = mysql.connect()
        cur = con.cursor()
        cur.execute(""" update sell set date=%s,coin=%s,quantity=%s,coin_value=%s,time=%s where sno=%s;""",[date,coin,quantity,coin_value,purchasing_time,sno])
        con.commit()
        con.close()
        cur.close()
        return redirect("/sell-add")
    else:
        user_id = request.args.get("id")
        con = mysql.connect()
        cur = con.cursor()
        cur.execute(" select * from sell where sno=%s;",[user_id])
        data = cur.fetchone()
        return render_template("sell-edit.html",data2=data)



@app.route("/sell-delete")
def sellDelete():
    user_id = request.args.get("id")
    con = mysql.connect()
    cur = con.cursor()
    cur.execute(""" delete from sell where sno=%s""",[user_id])
    con.commit()
    con.close()
    cur.close()
    return redirect("/sell-add")


@app.route("/from-to")
def fromTo():
    status = request.args.get("sell")
    if status == "sell":
        header = ["S.NO","DATE","COIN","QUANTITY","COIN VALUE","SELLING TIME","EDIT","DELETE"]
        fromm = request.args.get("fromm")
        too = request.args.get("too")
        too = request.args.get("too")
        con = mysql.connect()
        cur = con.cursor()
        cur.execute(""" SELECT * FROM sell WHERE date BETWEEN %s AND %s """,[fromm,too])
        data = cur.fetchall()
        print(data)
        cur.close()
        con.close()
        return render_template("from-to2.html",data=data,header=header)
    

    else:
        header = ["S.NO","BUYING DATE","BUYING TIME","QUANTITY","COIN VALUE","EDIT","DELETE"]
        fromm = request.args.get("fromm")
        too = request.args.get("too")
        con = mysql.connect()
        cur = con.cursor()
        cur.execute(""" SELECT * FROM buy WHERE date BETWEEN %s AND %s """,[fromm,too])
        data = cur.fetchall()
        print(data)
        cur.close()
        con.close()
        return render_template("from-to.html",data=data,header=header)


@app.route("/both-tables")
def bothTable():
    header2 = ["S.NO"," DATE","BUYING TIME","QUANTITY","COIN VALUE","COIN"]
    header = ["S.NO","DATE","COIN","QUANTITY","COIN VALUE","SELLING TIME"]
    con = mysql.connect()
    cur = con.cursor()
    cur.execute(""" select * from sell """)
    table1 = cur.fetchall()
    cur.execute(""" select * from buy """)
    table2 = cur.fetchall()
    con.close()
    cur.close()
    return render_template("both-table.html",header=header,data=table1,header2=header2,data2=table2)


if __name__=="__main__":
    app.run(debug=True, port=5008)