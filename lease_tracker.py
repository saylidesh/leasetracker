from flask import Flask, render_template, request
from dateutil import parser
from DBConfig import UseDatabase
import datetime



app = Flask(__name__)
app.secret_key = 'YouWillNeverGuessMySecretKey' 
app.config['dbconfig'] = {'host': '127.0.0.1', 
                          'user': 'tracker', 
                          'password': 'trackerpass', 
                          'database': 'Apartment_Lease_Tracker', }


@app.route('/', methods=['GET'])
def entry_page() -> 'html':
    return render_template('home.html', the_title='Welcome to the Lease Tracker!')

@app.route('/direct', methods=['POST'])
def direct() -> 'html':
    if request.form['action'] == 'Search':
        return render_template('application_search.html', the_title='Welcome to the Lease Tracker!')
     
    if request.form['action'] == 'Submit':
        return render_template('application_submit.html', the_title='Welcome to the Lease Tracker!')

    
    if request.form['action'] == 'List':
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL1 = """select first_name, middle_name, last_name,email_id, contact_no from Application"""    
            cursor.execute(_SQL1)
            records = cursor.fetchall()   
            
            applications = []  
            for row in records:
                applications.append(row)   
            cursor.close()
 
        return render_template('application_list.html', applications=applications)
    
    if request.form['action'] == 'Edit':
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        email_id = request.form['email_id']
        contact_no = request.form['contact_no']
        application_status = request.form['application_status']
        application_id = request.form['application_id']
        submitted_dt = request.form['submitted_dt']
        
        if application_status == 'Submitted':
            application_status = 'S'
        elif application_status == 'Work in Progress':
            application_status = 'W'
        elif application_status == 'Approved':
            application_status = 'A'
        elif application_status == 'Denied':
            application_status = 'D'
        
        
        return render_template('application_update.html', the_title='Welcome to the Lease Tracker!',first_name=first_name,  middle_name=middle_name, last_name=last_name,email_id=email_id,contact_no=contact_no,application_status=application_status,submitted_dt=submitted_dt, application_id=application_id, )

@app.route('/submitApplication', methods=['POST'])
def submit_application():
    
    """Fetch Request Parameters and send to database"""
    first_name = request.form['first_name']
    middle_name = request.form['middle_name']
    last_name = request.form['last_name']
    email_id = request.form['email_id']
    contact_no = request.form['contact_no']
    application_status = 'S'  
    submitted_dt = datetime.datetime.now() 
    application_id = ''
    
    
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select first_name, middle_name, last_name,email_id, contact_no, application_status, submitted_dt,application_id from Application where email_id = %s"""
        cursor.execute(_SQL, (email_id,)) 
                      
        result_set = cursor.fetchone()

        if result_set:  
            return render_template('application_submit.html', the_title='Welcome to the Lease Tracker!', error_msg="Email Id already exists", first_name=first_name,  middle_name=middle_name, last_name=last_name,email_id=email_id,contact_no=contact_no, )
  
    with UseDatabase(app.config['dbconfig']) as cursor_insert:
        _SQL_insert = """insert into Application (first_name, middle_name, last_name, email_id, contact_no, application_status, submitted_dt) values (%s, %s, %s, %s, %s, %s, %s)"""
        cursor_insert.execute(_SQL_insert, (first_name, middle_name, last_name,email_id,contact_no,application_status,submitted_dt, ))  

    with UseDatabase(app.config['dbconfig']) as cursor_read:
        _SQL_read = """select application_id from Application where email_id = %s"""
        cursor_read.execute(_SQL_read, (email_id,)) 
             
        result_set = cursor_read.fetchone()
        application_id = result_set[0]
    
    if application_status == 'S':
        application_status = 'Submitted'
    
    submitted_dt = submitted_dt.strftime('%m/%d/%Y')
        
    return render_template('application_results.html', first_name=first_name,  middle_name=middle_name, last_name=last_name,email_id=email_id,contact_no=contact_no,application_status=application_status,submitted_dt=submitted_dt,application_id=application_id, )



@app.route('/searchApplication', methods=['POST'])
def search_application():
    
    """Fetch Request Parameters and send to database"""
    email_id = request.form['email_id']

    
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select first_name, middle_name, last_name,email_id, contact_no, application_status, submitted_dt,application_id from Application where email_id = %s"""
        cursor.execute(_SQL, (email_id,)) 
                      
        result_set = cursor.fetchone()

        if result_set:
            print("application exists")
        else:   
            return render_template('application_search.html', the_title='Welcome to the Lease Tracker!', error_msg="Email Id does not exist", email_id=email_id,)

        
        first_name = result_set[0]
        middle_name = result_set[1] 
        last_name = result_set[2] 
        email_id = result_set[3] 
        contact_no = result_set[4]
        application_status = result_set[5] 
        submitted_dt = result_set[6]
        application_id = result_set[7]
            
    submitted_dt = submitted_dt.strftime('%m/%d/%Y')      
    
    if application_status == 'S':
        application_status = "Submitted"
    elif application_status == 'W':
        application_status = "Work in Progress"
    elif application_status == 'A':
        application_status = "Approved"
    elif application_status == 'D':
        application_status = "Denied"
    
      
    return render_template('application_results.html', first_name=first_name,  middle_name=middle_name, last_name=last_name,email_id=email_id,contact_no=contact_no,application_status=application_status,submitted_dt=submitted_dt,application_id=application_id, )

@app.route('/updateApplication', methods=['POST'])
def update_application():
    
    """Fetch Request Parameters and send to database"""
    first_name = request.form['first_name']
    middle_name = request.form['middle_name']
    last_name = request.form['last_name']
    email_id = request.form['email_id']
    contact_no = request.form['contact_no']
    application_status = request.form['application_status'] 
    application_id = request.form['application_id']
    submitted_dt = request.form['submitted_dt']

    
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """update Application set first_name=%s, middle_name=%s, last_name=%s, email_id=%s,contact_no=%s,application_status=%s where application_id = %s"""
        cursor.execute(_SQL, (first_name, middle_name, last_name,email_id,contact_no,application_status,application_id, ))  
  
        
    if application_status == 'S':
        application_status = "Submitted"
    elif application_status == 'W':
        application_status = "Work in Progress"
    elif application_status == 'A':
        application_status = "Approved"
    elif application_status == 'D':
        application_status = "Denied"
    
        
    return render_template('application_results.html', first_name=first_name,  middle_name=middle_name, last_name=last_name,email_id=email_id,contact_no=contact_no,application_status=application_status,submitted_dt=submitted_dt,application_id=application_id )


@app.route('/listApplication', methods=['GET'])
def get_applications():
    
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select first_name, middle_name, last_name,email_id, contact_no from Application"""    
        cursor.execute(_SQL) 
        records = cursor.fetchall()   
        applications = []  
        for row in records:
            applications.append(row)  
            print(row[0])   
        cursor.close()
 
            
 
    return render_template('application_list.html', applications=applications)



@app.route('/directResident', methods=['POST'])
def directResident() -> 'html':
    if request.form['action'] == 'Search':
        return render_template('resident_search.html', the_title='Welcome to the Lease Tracker!')
     
    if request.form['action'] == 'Submit':
        return render_template('resident_submit.html', the_title='Welcome to the Lease Tracker!')
    
    if request.form['action'] == 'List':
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL1 = """select first_name, middle_name, last_name,email_id, contact_no, building_no, apartment_no,lease_begin_dt, lease_end_dt from Resident"""    
            cursor.execute(_SQL1)
            records = cursor.fetchall()   
            residents = []  
            for row in records:
                residents.append(row)
                print(row[0] + ' ' + row[1])        
            cursor.close()
 
        return render_template('resident_list.html', residents=residents)

    if request.form['action'] == 'Edit':
        resident_id = request.form['resident_id']
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        building_no = request.form['building_no']
        apartment_no = request.form['apartment_no']
        lease_begin_dt = request.form['lease_begin_dt']
        lease_end_dt = request.form['lease_end_dt']
        email_id = request.form['email_id']
        contact_no = request.form['contact_no']
        
        
        return render_template('resident_update.html', the_title='Welcome to the Lease Tracker!',resident_id=resident_id, building_no = building_no, apartment_no=apartment_no,first_name=first_name, middle_name=middle_name, last_name=last_name,email_id=email_id,contact_no=contact_no,lease_begin_dt=lease_begin_dt, lease_end_dt=lease_end_dt, )

@app.route('/submitResident', methods=['POST'])
def submit_resident():
    
    """Fetch Request Parameters and send to database"""
    application_id = request.form['application_id']
    first_name = request.form['first_name']
    middle_name = request.form['middle_name']
    last_name = request.form['last_name']
    building_no = request.form['building_no']
    apartment_no = request.form['apartment_no']
    lease_begin_dt = request.form['lease_begin_dt']
    lease_end_dt = request.form['lease_end_dt']
    email_id = request.form['email_id']
    contact_no = request.form['contact_no']
    
    lease_begin_dt = parser.parse(lease_begin_dt)
    lease_end_dt = parser.parse(lease_end_dt)
    
    with UseDatabase(app.config['dbconfig']) as cursor_read_application:
        _SQL_get_app = """select application_id from Application where application_id = %s"""
        cursor_read_application.execute(_SQL_get_app, (application_id, ))  
        row = cursor_read_application.fetchone()
        if row:
            print("application exists")
        else:   
            return render_template('resident_submit.html', the_title='Welcome to the Lease Tracker!', error_msg="Application Id does not exist", first_name=first_name,  middle_name=middle_name, last_name=last_name,email_id=email_id,contact_no=contact_no,application_id=application_id,lease_begin_dt=lease_begin_dt, lease_end_dt=lease_end_dt,building_no = building_no, apartment_no=apartment_no,)

    with UseDatabase(app.config['dbconfig']) as cursor_insert:
        _SQL_insert = """insert into Resident (first_name, middle_name, last_name, email_id, contact_no, application_id, building_no,apartment_no,lease_begin_dt, lease_end_dt) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor_insert.execute(_SQL_insert, (first_name, middle_name, last_name, email_id, contact_no,application_id,building_no,apartment_no,lease_begin_dt, lease_end_dt, ))  

    with UseDatabase(app.config['dbconfig']) as cursor_read:
        _SQL_read = """select resident_id from Resident where email_id = %s"""
        cursor_read.execute(_SQL_read, (email_id,)) 
             
        result_set = cursor_read.fetchone()
        resident_id = result_set[0]
    
    
    lease_begin_dt = lease_begin_dt.strftime('%m/%d/%Y')
    lease_end_dt = lease_end_dt.strftime('%m/%d/%Y')
        
    return render_template('resident_results.html', resident_id=resident_id, first_name=first_name,  middle_name=middle_name, last_name=last_name,email_id=email_id,contact_no=contact_no,application_id=application_id,lease_begin_dt=lease_begin_dt, lease_end_dt=lease_end_dt,building_no = building_no, apartment_no=apartment_no,)



@app.route('/searchResident', methods=['POST'])
def search_resident():
    
    """Fetch Request Parameters and send to database"""
    email_id = request.form['email_id']

    
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select first_name, middle_name, last_name,email_id, contact_no, application_id, resident_id, lease_begin_dt, lease_end_dt, building_no, apartment_no from Resident where email_id = %s"""
        cursor.execute(_SQL, (email_id,)) 

        result_set = cursor.fetchone()
        if result_set:
            print("resident exists")
        else:   
            return render_template('resident_search.html', the_title='Welcome to the Lease Tracker!', error_msg="Email Id does not exist", email_id=email_id,)
        
        
        first_name = result_set[0]
        middle_name = result_set[1] 
        last_name = result_set[2] 
        email_id = result_set[3] 
        contact_no = result_set[4]
        application_id = result_set[5] 
        resident_id = result_set[6]
        lease_begin_dt = result_set[7]
        lease_end_dt = result_set[8]
        building_no = result_set[9]
        apartment_no = result_set[10]
            
 
    return render_template('resident_results.html', first_name=first_name,  middle_name=middle_name, last_name=last_name,email_id=email_id,contact_no=contact_no,application_id=application_id,resident_id=resident_id, apartment_no=apartment_no, building_no=building_no, lease_begin_dt=lease_begin_dt,lease_end_dt=lease_end_dt )

@app.route('/updateResident', methods=['POST'])
def update_resident():
    
    """Fetch Request Parameters and send to database"""
    resident_id = request.form['resident_id']
    first_name = request.form['first_name']
    middle_name = request.form['middle_name']
    last_name = request.form['last_name']
    email_id = request.form['email_id']
    contact_no = request.form['contact_no']
    building_no = request.form['building_no']
    apartment_no = request.form['apartment_no']
    lease_begin_dt = request.form['lease_begin_dt']
    lease_end_dt = request.form['lease_end_dt']

    
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """update Resident set first_name=%s, middle_name=%s, last_name=%s, email_id=%s,contact_no=%s,building_no=%s,apartment_no=%s,lease_begin_dt=%s,lease_end_dt=%s where resident_id = %s"""
        cursor.execute(_SQL, (first_name, middle_name, last_name,email_id,contact_no, building_no,apartment_no,lease_begin_dt,lease_end_dt, resident_id))  

    
        
    return render_template('resident_results.html', first_name=first_name,  middle_name=middle_name, last_name=last_name,email_id=email_id,contact_no=contact_no,apartment_no=apartment_no,building_no=building_no,lease_begin_dt=lease_begin_dt,lease_end_dt=lease_end_dt,resident_id=resident_id)

@app.route('/listResident', methods=['GET'])
def get_residents():
    
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select first_name, middle_name, last_name,email_id, contact_no, building_no, apartment_no,lease_begin_dt, lease_end_dt from Resident"""    
        cursor.execute(_SQL) 
        records = cursor.fetchall()   
        residents = []  
        for row in records:
            residents.append(row)
            print(row[0] + ' ' + row[1])        
        cursor.close()
 
            
 
    return render_template('resident_list.html', residents=residents)




if __name__ == '__main__':
    app.run(debug=True)
