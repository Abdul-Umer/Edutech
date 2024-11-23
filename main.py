from flask import Flask, flash, render_template, redirect, session, request,url_for,send_from_directory
from flask_mysqldb import MySQL
from models import db, Video, Course 
import json
import stripe
app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']='your_password'
app.config['MYSQL_DB'] = 'freelance'


# Initialize MySQL
mysql = MySQL(app)
# Set a secret key for session management
app.secret_key = 'supersecretkey'

@app.route('/')
def hello():
    return render_template('base.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/results/<int:score>')
def result(score):
    if score < 50:
        return render_template('fail.html', score=score)
    else:
        return render_template('pass.html', score=score)



@app.route('/food/<string:dish>')
def nonveg(dish):
    res = ''
    menu = {
        'butter_chckn': 650,
        'chckn_bryni': 799,
        'mutton_mandi': 650
    }
    
    if dish in menu:
        res = 'Already Exists'
    else:
        menu[dish] = 999
        res = 'Added Successfully!'
    print(menu)
    return render_template('view_food.html', menu=menu)

# Correcting the 'methods' part
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # Fetch data from form
        username = request.form['username']
        password = request.form['password']

        # Create cursor to interact with the database
        cur = mysql.connection.cursor()

        # Query the database for the user
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        # Close the cursor
        cur.close()

        # If user exists, check the password
        if user:
            db_username = user[1]  # Assuming username is the second field in the table
            db_password = user[3]  # Assuming password is the fourth field in the table

            if password == db_password:
                # Password matches, log the user in
                session['username'] = db_username
                return render_template('success.html', username=db_username)
            else:
                # Password doesn't match
                msg = "Invalid credentials"
                print(msg)
                return render_template('fail.html', msg=msg)
        else:
            # User doesn't exist
            msg = "User not found"
            return render_template('login.html', msg=msg)
    
    # For GET request, render the login page
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username',None)
    return render_template('login.html')

@app.route('/profile')
def profile():
    score=78
    if 'username' in session:
        username=session['username']
        return render_template('profile.html',name=username,score=score)
    else:
        msg="Login First"
        return render_template('login.html',msg=msg)

@app.route('/courses',methods=['GET'])
def courses():
    return render_template('course.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        # Fetch form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate passwords
        if password == confirm_password:
            # Store password as plain text (not recommended)
            # Create a cursor object to interact with the database
            cur = mysql.connection.cursor()

            # Insert the user into the 'users' table
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                        (username, email, password))

            # Commit the transaction
            mysql.connection.commit()

            # Close the cursor
            cur.close()

            # Redirect to login or home page after successful registration
            return redirect(url_for('login'))
        else:
            # In case passwords don't match, simply return to the register page
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/users/getall')
def user_data():
    cur = mysql.connection.cursor()
    cur.execute('select * from users')
    result=cur.fetchall()
    if len(result)>0:
        return json.dumps(result)
    else:
        return 'No Data Found'
@app.route('/courses/addcourse', methods=['POST', 'GET'])
def addcourse():
    cur = mysql.connection.cursor()
    
    # This fetches all courses but seems unnecessary if you're only inserting.
    cur.execute('SELECT * FROM course')
    result = cur.fetchall()
    print(result)
    
    # Assuming you're getting the course details from a form
    
    if request.method == 'POST':
        cid = request.form['cid']
        cname = request.form['cname']
        fees = request.form['fees']
        instructor = request.form['instructor']

        # Use placeholders to avoid SQL injection       
        cur.execute("INSERT INTO course (cid, cname, fees, instructor) VALUES (%s, %s, %s, %s)", (cid, cname, fees, instructor))
        mysql.connection.commit()
        return "Course Added Successfully!"

    return render_template('add_course.html', course=result)
@app.route('/courses/editcourse/<int:cid>', methods=['POST', 'GET'])
def edit_course(cid):
    cur = mysql.connection.cursor()

    # If POST request, handle the form submission to update the course
    if request.method == 'POST':
        cname = request.form['cname']
        fees = request.form['fees']
        instructor = request.form['instructor']

        cur.execute('UPDATE course SET cname=%s, fees=%s, instructor=%s WHERE cid=%s', (cname, fees, instructor, cid))
        mysql.connection.commit()
        return "Changes Done!"
    
    # If GET request, fetch the course details for the form
    cur.execute('SELECT * FROM course WHERE cid = %s', (cid,))
    course = cur.fetchone()  # Fetch one course by its ID
    cur.close()

    if course:
        return render_template('edit_course.html', course=course)
    else:
        return "Course not found", 404
    
@app.route('/courses/deletecourse/<int:cid>', methods=['POST', 'GET'])
def delete_course(cid):
    cur = mysql.connection.cursor()

    # Handle POST request - delete course
    if request.method == 'POST':
        cur.execute('DELETE FROM course WHERE cid = %s', (cid,))
        mysql.connection.commit()
        cur.close()
        return f"Course with ID {cid} Deleted Successfully"

    # Handle GET request - show confirmation page
    cur.execute('SELECT * FROM course WHERE cid = %s', (cid,))
    course = cur.fetchone()
    cur.close()

    # Check if course exists
    if course:
        return render_template('delete_course.html', course=course)
    else:
        return "Course not found", 404


@app.route('/courses/viewcourselist', methods=['GET'])
def view_course_list():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM course')
    courses = cur.fetchall()  # Fetch all courses
    cur.close()
    
    return render_template('view_course_list.html', courses=courses)

@app.route('/course',methods=['GET'])
def view_course(cid):
    course = Course.query.get_or_404(cid)
    videos = Video.query.filter_by(cid=cid).all()
    
    return render_template('view_course.html', course=course, videos=videos)


#from models import db, Video, Course  # Import your models
from werkzeug.utils import secure_filename
import os

os.makedirs('uploads', exist_ok=True)
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/add_video', methods=['GET', 'POST'])
def add_video():
    if request.method == 'POST':
        # Check if the form contains the file
        if 'video' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['video']
        
        # If no file is selected
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        # If the file is valid, save it
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Video added successfully!')
            return redirect(url_for('add_video'))
    
    return render_template('add_video.html')
    
    # Rest of your code

@app.route('/view_videos')
def view_videos():
    # Get a list of video files from the uploads directory
    video_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith(('.mp4', '.mov', '.avi'))]
    return render_template('view_videos.html', videos=video_files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete_video/<filename>', methods=['POST'])
def delete_video(filename):
    # Construct the full file path
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        # Remove the file from the filesystem
        os.remove(file_path)
        return redirect(url_for('view_videos'))
    except FileNotFoundError:
        return "File not found", 404
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
