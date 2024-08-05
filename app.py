from flask import Flask
from flask import render_template , request,redirect,url_for
import sqlite3 as sql
import random
from datetime import datetime

app = Flask(__name__)

#GLOBAL VARIABLES
ROW_ID=0
USER="User"
MSG="Welcome Admin"
MOVIE=""
VENUE=""
SHOW_NO=""
NO_OF_TICKETS=0
DATE=""
EMAIL_ID=""
TID=0
AMOUNT=0

@app.route("/")
def main():
    return render_template('index.html')


@app.route("/showAboutUs")
def showAboutUs():
    return render_template('aboutUs.html')


@app.route("/showNewUserPage/")
def showNewUserPage():
    return render_template('newUser.html')

@app.route('/signUp',methods = ['POST', 'GET'])
def signup():
   flag=False
   if request.method == 'POST':
      try:
         name = request.form['name']
         phno = request.form['phno']
         email = request.form['email']
         password = request.form['password']
         if not name or not phno  or not email  or not password :
            return render_template('newUser.html')
         else:
            with sql.connect("movie_database.db") as con:
               cur = con.cursor()
               cur.execute("INSERT INTO VISITOR (v_name,v_phno,v_email_id,v_password) VALUES (?,?,?,?)",(name,phno,email,password) )
               flag=True
               con.commit()
      except Exception as e:
         print(f"An error occurred: {e}")
         con.rollback()
      finally:
         if flag == True:
            return redirect("/showloginpage/")
         else:
            return redirect("/showNewUserPage/")
       
      
      

@app.route('/showloginpage/')
def cshowloginpage():
   return render_template("login.html")

@app.route('/login',methods = ['POST', 'GET'])
def login():
   flag=False
   
   if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']
      with sql.connect("movie_database.db") as con:
            cur = con.cursor()
            cur.execute("select v_email_id,v_password,v_name from visitor")
            rows=cur.fetchall()
            cur.execute("select name,password from admin")
            adetails=cur.fetchall()
            for adetail in adetails:
               dbemail=adetail[0]
               dbPass=adetail[1]
               if dbemail == email and dbPass == password:
                  global USER , EMAIL_ID 
                  USER="ADMIN"
                  return redirect("/adminDashboard/")
               else:
                  flag=False
            for row in rows:
               dbemail=row[0]
               dbPass=row[1]
               if dbemail == email and dbPass == password:
                  flag=True 
                  EMAIL_ID=dbemail
                  USER=row[2]

                  break
               else:
                  flag=False
   con.commit()
   if(flag==True):
      return redirect("/showmovies/")
   else:
      return redirect("/")
@app.route('/adminDashboard/showmovies/')
@app.route('/showmovies/')
def showmovies():
   with sql.connect("movie_database.db") as con:
      cur = con.cursor()
      cur.execute("select m_name,m_rating,m_language,m_synopsis from movie order by m_release desc")
      rows=cur.fetchall()
      return render_template("displayMovies.html",USER=USER,rows=rows)


@app.route('/showmovies/showBookTickets/')
def showBookTickets():
   movie = request.args.get('movie')
   current_date = datetime.today().strftime('%Y-%m-%d')
   with sql.connect("movie_database.db") as con:
      cur = con.cursor()
      cur.execute("select v_name from venue")
      vnames=cur.fetchall()
      return render_template("tickets.html",USER=USER,vnames=vnames, movie=movie, current_date=current_date)

@app.route('/checkAvail',methods = ['POST', 'GET'])
def availability():
   flag=False
   if request.method == 'POST':
        movie = request.form['movie']
        venue = request.form['venue']
        show_no = request.form['show_no']
        no_of_tickets = int(request.form['no_of_tickets'])
        date = request.form['date']
        
        venue=venue[2:-3].strip()

        # Store the values globally if needed
        global MOVIE, VENUE, SHOW_NO, NO_OF_TICKETS, DATE
        MOVIE = movie
        VENUE = venue
        SHOW_NO = show_no
        NO_OF_TICKETS = no_of_tickets
        DATE = date
        # Connect to the database
        with sql.connect("movie_database.db") as con:
            cur = con.cursor()
            
            # Retrieve venue capacity
            cur.execute("SELECT v_capacity FROM venue WHERE v_name = ?", (venue,))
            v_capacity = cur.fetchone()
            if v_capacity:
                v_capacity = int(v_capacity[0])  # Get the capacity as an integer
            else:
                return render_template("tickets.html", error="Venue not found.")
             
            # Calculate the available seats
            cur.execute("""
                SELECT COALESCE(SUM(no_of_tickets), 0) 
                FROM book_ticket 
                WHERE m_name = ? AND v_name = ? AND show_no = ? AND date = ?
                """, (movie, venue, show_no, date))
            booked_tickets = cur.fetchone()[0]  # Get the sum of booked tickets

            available_seats = v_capacity - booked_tickets
            
            # Check if there are enough available seats
            if available_seats >= no_of_tickets:
               return redirect(f"/payment/")
            else:
               return render_template("tickets.html", error="Not enough seats available.")
            
            con.commit()
   if(flag==True):
      return redirect("/showmovies/")
   else:
      return redirect("/")

@app.route('/payment/')
def pay():
   global NO_OF_TICKETS,USER,MOVIE,VENUE,SHOW_NO,NO_OF_TICKETS,DATE,EMAIL_ID,AMOUNT,TID
   cost=int(NO_OF_TICKETS)*15
   AMOUNT=cost
   tid=random.randint(1,1000)
   TID=tid
   return render_template('payment.html',cost=cost,USER=USER,movie=MOVIE,venue=VENUE,show_no=SHOW_NO,tickets=NO_OF_TICKETS,date=DATE,email=EMAIL_ID,tid=tid)

@app.route('/book',methods = ['POST', 'GET'])
def book():
   flag=False
   if request.method == 'POST':
      global MOVIE,VENUE,SHOW_NO,NO_OF_TICKETS,DATE,EMAIL_ID,TID,AMOUNT
      with sql.connect("movie_database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO BOOK_TICKET(NO_OF_TICKETS,M_NAME,SHOW_NO,DATE,V_NAME,V_EMAIL_ID) VALUES (?,?,?,?,?,?)",(NO_OF_TICKETS,MOVIE,SHOW_NO,DATE,VENUE,EMAIL_ID))
            print("insert into book_ticket success")
            cur.execute("INSERT INTO PAYMENT(V_EMAIL_ID,AMOUNT,TRANSACTION_ID) VALUES (?,?,?)",(EMAIL_ID,AMOUNT,TID))
            print("insert into PAYMENT success")
            flag=True
            
      con.commit()
   if(flag==True):
      return redirect(url_for('showmovies'))
   else:
      return redirect(url_for('showmovies'))

@app.route('/adminDashboard/')
def adminDashboard():
   global MSG
   return render_template("admin.html",MSG=MSG)

@app.route('/adminDashboard/addMovie/')
def showaddMovie():
   return render_template("addmovie.html")


@app.route('/addmovie',methods = ['POST', 'GET'])
def addmovie():
   flag=False
   if request.method == 'POST':
      try:
         name = request.form['name']
         rating = request.form['rating']
         release = request.form['release']
         language = request.form['language']
         synopsis = request.form['synopsis']
         if not name or not rating  or not release  or not language or not synopsis :
            return render_template('addmovie.html')
         else:
            with sql.connect("movie_database.db") as con:
               cur = con.cursor()
               cur.execute("INSERT INTO movie (m_name,m_rating,m_release,m_language,m_synopsis) VALUES (?,?,?,?,?)",(name,rating,release,language,synopsis) )
               flag=True
               con.commit()
      except:
         con.rollback()
      finally:
         if flag == True:
            return redirect("/adminDashboard/")
         else:
            return redirect("/adminDashboard/")


@app.route('/removeMovie/')
@app.route('/adminDashboard/removeMovie/')
def showremoveMovie():
   with sql.connect("movie_database.db") as con:
      cur = con.cursor()
      cur.execute("select m_name from movie")
      mnames=cur.fetchall()
      return render_template("removeMovie.html",mnames=mnames)

@app.route('/removeMovie',methods = ['POST', 'GET'])
def removemovie():
   flag=False
   if request.method == 'POST':
      try:
         name = request.form['movie']
         
         name=name[2:-3].strip()
         name=name
         with sql.connect("movie_database.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM movie WHERE m_name= ?",(name,))
            flag=True
            con.commit()
            con.close()
           
      except:
         con.rollback()
      finally:
         if flag == True:
            return redirect("/adminDashboard/")
         else:
            return redirect("/removeMovie/")

   
if __name__ == "__main__":
    app.run(debug=True)