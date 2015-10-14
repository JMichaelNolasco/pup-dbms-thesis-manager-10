import json
import os
import urllib
import jinja2
import webapp2
import json
import csv
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext.db import Key
import logging
import re

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)




class Thesis(ndb.Model):
    year = ndb.StringProperty(indexed=True)
    title = ndb.StringProperty(indexed=True)
    subtitle = ndb.StringProperty()
    abstract = ndb.TextProperty()
    section = ndb.StringProperty()
    adviser_key = ndb.KeyProperty(indexed=True)
    proponent_keys = ndb.KeyProperty(repeated=True)
    department_key = ndb.KeyProperty(indexed=True)
    tags = ndb.StringProperty(repeated=True)


    created_by = ndb.KeyProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    @property
    def department_name(self):
        return self.department_key.get().name
    @property
    def college_name(self):
         return self.department_key.get().college_key.get().name
    @property
    def university_name(self):
        return self.department_key.get().college_key.get().university_key.get().name
    

class Faculty(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)
    department=ndb.StringProperty(indexed=True)
    dept=ndb.KeyProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def get_by_key(cls, keyname):
        try:
            return ndb.Key(cls, keyname).get()
        except Exception:
            return None
class Student(ndb.Model):
    first_name = ndb.StringProperty(indexed=True)
    middle_name = ndb.StringProperty(indexed=True)
    last_name = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
class Department(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    chairperson = ndb.StringProperty(indexed=True)
    college_key = ndb.KeyProperty(indexed=True)
class College(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    address=ndb.StringProperty(indexed=True)
    university_key = ndb.KeyProperty(indexed=True)
    @property
    def univ_name(self):
        return self.university_key.get().name
class University(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    initials = ndb.StringProperty(indexed=True)
class User(ndb.Model):
    email = ndb.StringProperty(indexed=True)
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    phone_number = ndb.StringProperty()
    created_date = ndb.DateTimeProperty(auto_now_add=True)


class SetupDBHandler(webapp2.RequestHandler):
    def get(self):

        university = University(name='Polytechnic University of the Philippines', initials='PUP')
        university.put()

        up = University(name='University of the Philippines', initials='UP')
        up.put()

        college = College(name='Engineering', university_key=university.key)
        college.put()

        college_up = College(name='Engineering', university_key=up.key)
        college_up.put()

        archi_college = College(name='Architecture', university_key=university.key)
        archi_college.put()

        coe_department = Department(name='COE', college_key=college.key)
        coe_department.put()

        coe_up_department = Department(name='COE', college_key=college_up.key)
        coe_up_department.put()

        ece_department = Department(name='ECE', college_key=college.key)
        ece_department.put()

        self.response.write('Datastore setup completed')
class ImportHandler(webapp2.RequestHandler):
    def get(self):
        file = open(os.path.join(os.path.dirname(__file__), 'entry.csv'))
        # logging.info(file)
        fileReader = csv.reader(file)

        department_key = ndb.Key(urlsafe='ah9kZXZ-cHVwLWRibXMtdGhlc2lzLW1hbmFnZXItMTBhchcLEgpEZXBhcnRtZW50GICAgICAgMAJDA')
        department = department_key.get()
        college = department.college_key.get()
        university = college.university_key.get()

        for row in fileReader:
            thesis = Thesis()
            thesis.year = row[3]
            thesis.title = row[4]
            subtitle = ''
            thesis.abstract = row[5]
            thesis.section = row[6]
            # thesis.department_key = department_key
            thesis.tags = ['pupcoe', 'mcu']
            adviser_name = row[7] # 'Rodolfo Talan'
            
            adviser_keyname = adviser_name.strip().replace(' ', '').lower()
            adviser = Faculty.get_by_key(adviser_keyname)

            for i in range(8,13):
                        stud = Student()
                        if row[i]:
                            stud_name = row[i].title().split(' ')
                            size = len(stud_name)
                            if size >= 1:
                                stud.first_name = stud_name[0]
                            if size >= 2:
                                stud.middle_name = stud_name[1]
                            if size >= 3:
                                stud.last_name = stud_name[2]
                            thesis.proponent_keys.append(stud.put())
            
            

            if adviser is None:
                adviser = Faculty(key=ndb.Key(Faculty, adviser_keyname), name=adviser_name)
                adviser.put()

            

            thesis.department_key = department_key
            thesis.adviser_key = adviser.key
            
            thesis.put()


        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render())
class RegistrationPageHandler(webapp2.RequestHandler):
    def get(self):
        loggedin_user = users.get_current_user()

        if loggedin_user:
            user_key = ndb.Key('User', loggedin_user.user_id())
            user = user_key.get()
            if user:
                self.redirect('/home')
            else:
                template = JINJA_ENVIRONMENT.get_template('register.html')
                logout_url = users.create_logout_url('/login')
                email=users.get_current_user().email() 
                template_values = {
                    'email':email,
                    'logout_url': logout_url

                }
                self.response.write(template.render(template_values))
        else:
            login_url = users.create_login_url('/register')
            self.redirect(login_url)

    def post(self):
        loggedin_user = users.get_current_user()
        user = User(id=loggedin_user.user_id(), email=loggedin_user.email(),
                     first_name=self.request.get('first_name'),
                     last_name=self.request.get('last_name'),
                     phone_number=self.request.get('phone_number'))
        user.put()
        self.redirect('/home')
class LoginPage(webapp2.RequestHandler):
    def get(self):
             
        loggedin_user = users.get_current_user()
        if loggedin_user:
            user_key = ndb.Key('User', loggedin_user.user_id())
            user=user_key.get()
            if user:
    
                      
                self.redirect('/home')
            else:
                self.redirect('/register')               
        else:
              template = JINJA_ENVIRONMENT.get_template('login.html')
              login=users.create_login_url(self.request.uri)
              template_values = {
                'login' :login,

              }
              self.response.write(template.render(template_values))
class HomePage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('home.html')
        user = users.get_current_user()
        if user:
       
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout Account'
            email=users.get_current_user().email() 
            user_login=True 
            check_login =True 
        else:
            url =  users.create_login_url('/login')
            url_linktext =  'Login'
            user_login=False
            check_login = True


        template_values = {
            'user': user,
            'url': url,

            'url_linktext': url_linktext,
            'user_login': user_login,
            'check_login' :check_login
        }

        self.response.write(template.render(template_values))
class ThesisHome(webapp2.RequestHandler):
     def get(self):
        template = JINJA_ENVIRONMENT.get_template('thesis_home.html')
        user = users.get_current_user()
        if user:
       
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout Account'
            email=users.get_current_user().email() 
            user_login=True 
            check_login =True 
        else:
            url =  users.create_login_url('/login')
            url_linktext =  'Login'
            user_login=False
            check_login = True


        template_values = {
            'user': user,
            'url': url,

            'url_linktext': url_linktext,
            'user_login': user_login,
            'check_login' :check_login
        }

        self.response.write(template.render(template_values))
class StudentHome(webapp2.RequestHandler):
     def get(self):
        template = JINJA_ENVIRONMENT.get_template('student_home.html')
        user = users.get_current_user()
        if user:
       
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout Account'
            email=users.get_current_user().email() 
            user_login=True 
            check_login =True 
        else:
            url =  users.create_login_url('/login')
            url_linktext =  'Login'
            user_login=False
            check_login = True


        template_values = {
            'user': user,
            'url': url,

            'url_linktext': url_linktext,
            'user_login': user_login,
            'check_login' :check_login
        }

        self.response.write(template.render(template_values))
class FacultyHome(webapp2.RequestHandler):
     def get(self):
        template = JINJA_ENVIRONMENT.get_template('faculty_home.html')
        user = users.get_current_user()
        if user:
       
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout Account'
            email=users.get_current_user().email() 
            user_login=True 
            check_login =True 
        else:
            url =  users.create_login_url('/login')
            url_linktext =  'Login'
            user_login=False
            check_login = True


        template_values = {
            'user': user,
            'url': url,

            'url_linktext': url_linktext,
            'user_login': user_login,
            'check_login' :check_login
        }

        self.response.write(template.render(template_values))      
class UniversityHome(webapp2.RequestHandler):
     def get(self):
        template = JINJA_ENVIRONMENT.get_template('university_home.html')
        user = users.get_current_user()
        if user:
       
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout Account'
            email=users.get_current_user().email() 
            user_login=True 
            check_login =True 
        else:
            url =  users.create_login_url('/login')
            url_linktext =  'Login'
            user_login=False
            check_login = True


        template_values = {
            'user': user,
            'url': url,

            'url_linktext': url_linktext,
            'user_login': user_login,
            'check_login' :check_login
        }

        self.response.write(template.render(template_values))  
class CollegeHome(webapp2.RequestHandler):
     def get(self):
        template = JINJA_ENVIRONMENT.get_template('college_home.html')
        user = users.get_current_user()
        if user:
       
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout Account'
            email=users.get_current_user().email() 
            user_login=True 
            check_login =True 
        else:
            url =  users.create_login_url('/login')
            url_linktext =  'Login'
            user_login=False
            check_login = True


        template_values = {
            'user': user,
            'url': url,

            'url_linktext': url_linktext,
            'user_login': user_login,
            'check_login' :check_login
        }

        self.response.write(template.render(template_values))  
class ThesisCreate(webapp2.RequestHandler):
    def get(self):
   
        loggedin_user = users.get_current_user()
        if loggedin_user:
            user_key = ndb.Key('User', loggedin_user.user_id())
            user=user_key.get()
            if user:
                template = JINJA_ENVIRONMENT.get_template('thesis_create.html')
                url = users.create_logout_url('/login') 
                url_linktext = 'Logout' + ' ' + users.get_current_user().email()
                thesis= Thesis.query().fetch()
                student= Student.query().fetch()
                adviser= Faculty.query().fetch()
                university=University.query().fetch()
                department=Department.query().fetch()
                college=College.query().fetch()
                template_values = {
                   'url': url,
                   'url_linktext': url_linktext,
                   'student':student,
                   'adviser': adviser,
                   'thes': thesis,
                   'university': university,
                   'college': college,
                   'department': department,
              
                }
                self.response.write(template.render(template_values))  
            else:
                self.redirect('/register')
        else:
            self.redirect('/login')        

    def post(self):
      
       

               
       
        self.redirect('/thesis/list')
class ThesisList(webapp2.RequestHandler):
    def get(self):
        records = Thesis.query().fetch()
        

        template_values = {
                "records": records,
              
        }
        
        template = JINJA_ENVIRONMENT.get_template('thesis_list.html')
        self.response.write(template.render(template_values))       
class ThesisEdit(webapp2.RequestHandler):
    def get(self,id):
        template = JINJA_ENVIRONMENT.get_template('thesis_edit.html')
        self.response.write(template.render())
        
        th_id=int(id)
        s = Thesis.get_by_id(int(th_id))
        studs = {}
        for i in range(0,len(s.proponent_keys)):
            studs[i] = s.proponent_keys[i].get()


        records = Thesis.query().order(-Thesis.date).fetch()
        thesis_id = int(id)
        student= Student.query().fetch()

        university=University.query().fetch()
        department=Department.query().fetch()
        college=College.query().fetch()

        response = {
            'records': records,
            'id':thesis_id,
            'student':student,
            "studs":studs,
             'university': university,
            'college': college,
         'department': department,
        }

        self.response.write(template.render(response))

    def post(self,id):
        thesis_id = int(id)    
        thesis = Thesis.get_by_id(thesis_id)

        thesis.year = self.request.get('year')
        thesis.title = self.request.get('title')
        thesis.subtitle = self.request.get('sub')
        thesis.section = self.request.get('section')
        thesis.abstract = self.request.get('abstract')

        adviser_name=self.request.get('adviser')
        adviser_keyname = adviser_name.strip().replace(' ', '').lower()
        adviser = Faculty.get_by_key(adviser_keyname)

        if adviser is None:
                adviser = Faculty(key=ndb.Key(Faculty, adviser_keyname), name=adviser_name)
                adviser.put()

        thesis.adviser_key=adviser.key
        
        thesis.put()
        self.redirect('/thesis/list')
class ThesisDelete(webapp2.RequestHandler):
       
    def get(self,id):    
        thesis_key = Thesis.get_by_id(int(id))
        thesis_key.key.delete()
        self.redirect('/thesis/home')
class ThesisDetailsPage (webapp2.RequestHandler):
    def get(self,id):    

        th_id=int(id)
        s = Thesis.get_by_id(int(th_id))
        studs = {}
        for i in range(0,len(s.proponent_keys)):
            studs[i] = s.proponent_keys[i].get()

        thesis = Thesis.query().order(-Thesis.date).fetch()
        thesis_id=int(id)
        t=Thesis()



        keywords = re.sub('[^\w]', ' ', s.title).split()
        #words to be removed
        remove_articles = ['is','and','for','s','are','in','on','of','if','with','as','a','for']
        for i in range(len(remove_articles)):
            if remove_articles[i] in keywords:
                keywords.remove(remove_articles[i])
        i = 0

      
        template_values = {
                    "records": thesis,
                    "id": thesis_id,
                    "studs":studs,
                    'keywords':keywords
         
        }
   
        template = JINJA_ENVIRONMENT.get_template('thesis_details_page.html')
        self.response.write(template.render(template_values))
   
        
 

class APIThesis(webapp2.RequestHandler):
    
    def get(self):
        CpE_Thesis= Thesis.query().order(-Thesis.date).fetch()

        thesis_list=[]
        for thesis in CpE_Thesis:
   
            thesis_list.append ({
                'title': thesis.title,
                'subtitle':thesis.subtitle,
                # 'id': thesis.key.id(),
                'year' : thesis.year,
                
                'abstract': thesis.abstract,
             
                'section': thesis.section
              
            })
        response = {
            'result' :'OK' ,
            'data' : thesis_list 
            
        }
      
        self.response.headers['Content-type'] = 'app/json'
        self.response.out.write(json.dumps(response))

    def post(self):
        
        student=Student()
        faculty=Faculty()
        department=Department()
        thesis=Thesis()
        thesis.title=self.request.get('title')
        logging.info(thesis.title)
        thesis.subtitle=self.request.get('sub')
        #Thesis Section
        
        thesis.year=self.request.get('year')
        thesis.tags = ['pupcoe', 'mcu']
        thesis.abstract=self.request.get('abstract')
        thesis.section=self.request.get('section')
        

         #For Faculty Key & Name
        adviser_name=self.request.get('adviser')
        logging.info(adviser_name)
        adviser_keyname = adviser_name.strip().replace(' ', '').lower()
        adviser = Faculty.get_by_key(adviser_keyname)
        if adviser is None:
                adviser = Faculty(key=ndb.Key(Faculty, adviser_keyname), name=adviser_name)
                adviser.put()
        thesis.adviser_key=adviser.key
   
        university = self.request.get('univ')
        logging.info(university)
        college = self.request.get('college')
        logging.info(college)
        department = self.request.get('department')
        logging.info(department)
        
        university_name = University(name = university)
        university_name.put()
        
        college_name = College(name = college, university_key = university_name.key)
        college_name.put()

        department_name = Department(name = department, college_key = college_name.key)
        thesis.department_key = department_name.put()
        
        #Proponents

        proponents = []
        if self.request.get('proponents1'):
            proponents.append(self.request.get('proponents1'))
        if self.request.get('proponents2'):
            proponents.append(self.request.get('proponents2'))
        if self.request.get('proponents3'):
            proponents.append(self.request.get('proponents3'))
        if self.request.get('proponents4'):
            proponents.append(self.request.get('proponents4'))
        if self.request.get('proponents5'):
            proponents.append(self.request.get('proponents5'))
        
        for i in range(0,len(proponents)):
                name = proponents[i].title().split(' ')
                size = len(name)
                stud = Student()
                if size >= 1:
                    stud.first_name = name[0]
                if size >= 2:
                    stud.middle_name= name[1]
                if size >= 3:
                    stud.last_name= name[2]
                thesis.proponent_keys.append(stud.put())
        logging.info(proponents)
        thesis.put()
        

        self.response.headers['Content-type'] = 'app/json'
        response = {
            'result': 'OK',
            'data':{
                # 'id': thesis.key.id(),
                'year' : thesis.year,
                'title': thesis.title,
                'subtitle':thesis.subtitle,
                'abstract': thesis.abstract,
            
                'section': thesis.section

            }
        }
        self.response.out.write(json.dumps(response))


class Search(webapp2.RequestHandler):
    def get(self):
        thesis = Thesis.query().order(-Thesis.date).fetch()
        student = Student.query().fetch()
        template_values = {
                "thesis": thesis,
                "student": student
        }
            
        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))           

class StudentCreate(webapp2.RequestHandler):
    def get(self):
   
        loggedin_user = users.get_current_user()
        if loggedin_user:
            user_key = ndb.Key('User', loggedin_user.user_id())
            user=user_key.get()
            if user:
                template = JINJA_ENVIRONMENT.get_template('student_create.html')
                url = users.create_logout_url('/login') 
                url_linktext = 'Logout' + ' ' + users.get_current_user().email()
                thesis= Thesis.query().fetch()
                student= Student.query().fetch()
                adviser= Faculty.query().fetch()
                university=University.query().fetch()
                department=Department.query().fetch()
                college=College.query().fetch()
                template_values = {
                   'url': url,
                   'url_linktext': url_linktext,
                   'student':student,
                   'adviser': adviser,
                   'thes': thesis,
                   'university': university,
                   'college': college,
                   'department': department,
              
                }
                self.response.write(template.render(template_values))  
            else:
                self.redirect('/register')
        else:
            self.redirect('/login')        

    def post(self):
        student=Student()
        student.first_name=self.request.get("first_name")
        student.middle_name=self.request.get("middle_name")
        student.last_name=self.request.get("last_name")
        student.email=self.request.get("email")
        student.put()
        self.redirect('/student/home')
class StudentList(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('student_list.html')
        students = Student.query().order(-Student.date).fetch()
        thesis= Thesis.query().order(-Thesis.date).fetch()
        template_values = {
            "students": students,
            "thesis":thesis,
        }
        logging.info(students)
       
        self.response.write(template.render(template_values))  
class StudentDelete(webapp2.RequestHandler):
       
    def get(self,id):    
        student_key = Student.get_by_id(int(id))
        student_key.key.delete()
        self.redirect('/student/home')
class StudentDetailsPage (webapp2.RequestHandler):
    def get(self,id):    

        
        student = Student.query().fetch()
        studs_id=int(id)
      
        template_values = {
                "student": student,
                "id": studs_id,

        }
   
        template = JINJA_ENVIRONMENT.get_template('student_details_page.html')
        self.response.write(template.render(template_values))
class StudentEdit(webapp2.RequestHandler):
    def get(self,id):
        template = JINJA_ENVIRONMENT.get_template('student_edit.html')
        records = Thesis.query().order(-Thesis.date).fetch()
        thesis_id = int(id)
        student= Student.query().fetch()
        values = {
            'records': records,
            'id':thesis_id,
            'student':student,
        }

        self.response.write(template.render(values))  

    def post(self,id):
        stud_id = int(id)    
        student = Student.get_by_id(stud_id)

        student.first_name=self.request.get("first_name")
        student.middle_name=self.request.get("middle_name")
        student.last_name=self.request.get("last_name")
        student.email=self.request.get("email")
        student.put()
        self.redirect('/student/home')

class FacultyCreate(webapp2.RequestHandler):
    def get(self):
   
        loggedin_user = users.get_current_user()
        if loggedin_user:
            user_key = ndb.Key('User', loggedin_user.user_id())
            user=user_key.get()
            if user:
                template = JINJA_ENVIRONMENT.get_template('faculty_create.html')
                url = users.create_logout_url('/login') 
                url_linktext = 'Logout' + ' ' + users.get_current_user().email()
                thesis= Thesis.query().fetch()
                student= Student.query().fetch()
                adviser= Faculty.query().fetch()
                university=University.query().fetch()
                department=Department.query().fetch()
                college=College.query().fetch()
                template_values = {
                   'url': url,
                   'url_linktext': url_linktext,
                   'student':student,
                   'adviser': adviser,
                   'thes': thesis,
                   'university': university,
                   'college': college,
                   'department': department,
              
                }
                self.response.write(template.render(template_values))  
            else:
                self.redirect('/register')
        else:
            self.redirect('/login')        

    def post(self):
        faculty=Faculty()
        faculty.name=self.request.get("name")
        faculty.email=self.request.get("email")
        faculty.department=self.request.get("department")
        faculty.put()
        self.redirect('/faculty/home')
class FacultyList(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('faculty_list.html')
        faculty = Faculty.query().fetch()
        template_values = {
            "faculty":faculty,
        }
       
        self.response.write(template.render(template_values))  
class FacultyDelete(webapp2.RequestHandler):
       
    def get(self,id):    
        faculty_key = Faculty.get_by_id(int(id))
        faculty_key.key.delete()
        self.redirect('/faculty/home')
class FacultyDetailsPage (webapp2.RequestHandler):
    def get(self,id):    

        
        faculty = Faculty.query().fetch()
        f_id=int(id)
      
        template_values = {
                "faculty": faculty,
                "id": f_id,

        }
   
        template = JINJA_ENVIRONMENT.get_template('faculty_details_page.html')
        self.response.write(template.render(template_values))
class FacultyEdit(webapp2.RequestHandler):
    def get(self,id):
        template = JINJA_ENVIRONMENT.get_template('faculty_edit.html')
        faculty= Faculty.query().fetch()
        thesis_id = int(id)
        student= Student.query().fetch()
        department=Department.query().fetch()
        values = {

            'id':thesis_id,
            'faculty':faculty,
            'department':department
        }

        self.response.write(template.render(values))  

    def post(self,id):
        f_id = int(id)    
        faculty = Faculty.get_by_id(fs_id)
        faculty.name=self.request.get("name")
        faculty.email=self.request.get("email")
        faculty.put()
        self.redirect('/faculty/home')

class UniversityCreate(webapp2.RequestHandler):
    def get(self):
   
        loggedin_user = users.get_current_user()
        if loggedin_user:
            user_key = ndb.Key('User', loggedin_user.user_id())
            user=user_key.get()
            if user:
                template = JINJA_ENVIRONMENT.get_template('university_create.html')
                url = users.create_logout_url('/login') 
                url_linktext = 'Logout' + ' ' + users.get_current_user().email()
                thesis= Thesis.query().fetch()
                student= Student.query().fetch()
                adviser= Faculty.query().fetch()
                university=University.query().fetch()
                department=Department.query().fetch()
                college=College.query().fetch()
                template_values = {
                   'url': url,
                   'url_linktext': url_linktext,
                   'student':student,
                   'adviser': adviser,
                   'thes': thesis,
                   'university': university,
                   'college': college,
                   'department': department,
              
                }
                self.response.write(template.render(template_values))  
            else:
                self.redirect('/register')
        else:
            self.redirect('/login')        

    def post(self):
        university=University()
        university.name=self.request.get("name")
        university.initials=self.request.get("initials")
        university.put()
        self.redirect('/university/home')
class UniversityList(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('university_list.html')
        university= University.query().fetch()
        template_values = {
            "university":university,
        }
       
        self.response.write(template.render(template_values))  
class UniversityDelete(webapp2.RequestHandler):
       
    def get(self,id):    
        university_key = University.get_by_id(int(id))
        university_key.key.delete()
        self.redirect('/university/home')
class UniversityDetailsPage (webapp2.RequestHandler):
    def get(self,id):    

        
        university = University.query().fetch()
        u_id=int(id)
      
        template_values = {
                "university":university,
                "id": u_id,

        }
   
        template = JINJA_ENVIRONMENT.get_template('university_details_page.html')
        self.response.write(template.render(template_values))
class UniversityEdit(webapp2.RequestHandler):
    def get(self,id):
        template = JINJA_ENVIRONMENT.get_template('university_edit.html')
        university= University.query().fetch()
        u_id = int(id)
        student= Student.query().fetch()
        values = {

            'id':u_id,
            'university':university,
        }

        self.response.write(template.render(values))  

    def post(self,id):
        u_id = int(id)    
        university = University.get_by_id(u_id)
        university.name=self.request.get("name")
        university.initials=self.request.get("initials")
        university.put()
        self.redirect('/university/home')

class CollegeCreate(webapp2.RequestHandler):
    def get(self):
   
        loggedin_user = users.get_current_user()
        if loggedin_user:
            user_key = ndb.Key('User', loggedin_user.user_id())
            user=user_key.get()
            if user:
                template = JINJA_ENVIRONMENT.get_template('college_create.html')
                url = users.create_logout_url('/login') 
                url_linktext = 'Logout' + ' ' + users.get_current_user().email()
                thesis= Thesis.query().fetch()
                student= Student.query().fetch()
                adviser= Faculty.query().fetch()
                university=University.query().fetch()
                department=Department.query().fetch()
                college=College.query().fetch()
                template_values = {
                   'url': url,
                   'url_linktext': url_linktext,
                   'student':student,
                   'adviser': adviser,
                   'thes': thesis,
                   'university': university,
                   'college': college,
                   'department': department,
              
                }
                self.response.write(template.render(template_values))  
            else:
                self.redirect('/register')
        else:
            self.redirect('/login')        

    def post(self):
        college=College()
        college.name=self.request.get("name")
        college.address=self.request.get("address")
        college.put()
        self.redirect('/college/home')
class CollegeList(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('college_list.html')
        college= College.query().fetch()
        template_values = {
            "college":college,
        }
       
        self.response.write(template.render(template_values))  
class CollegeDelete(webapp2.RequestHandler):
       
    def get(self,id):    
        college_key = College.get_by_id(int(id))
        college_key.key.delete()
        self.redirect('/college/home')
class CollegeDetailsPage (webapp2.RequestHandler):
    def get(self,id):    

        
        college =College.query().fetch()
        c_id=int(id)
      
        template_values = {
                "college":college,
                "id": c_id,

        }
   
        template = JINJA_ENVIRONMENT.get_template('college_details_page.html')
        self.response.write(template.render(template_values))
class CollegeEdit(webapp2.RequestHandler):
    def get(self,id):
        template = JINJA_ENVIRONMENT.get_template('college_edit.html')
        college= College.query().fetch()
        c_id = int(id)
    
        values = {

            'id':c_id,
            'college': college,
        }

        self.response.write(template.render(values))  

    def post(self,id):
        u_id = int(id)    
        college = College.get_by_id(u_id)
        college.name=self.request.get("name")
        college.address=self.request.get("address")
        college.put()
        self.redirect('/college/home')

class DepartmentCreate(webapp2.RequestHandler):
    def get(self):
   
        loggedin_user = users.get_current_user()
        if loggedin_user:
            user_key = ndb.Key('User', loggedin_user.user_id())
            user=user_key.get()
            if user:
                template = JINJA_ENVIRONMENT.get_template('department_create.html')
                url = users.create_logout_url('/login') 
                url_linktext = 'Logout' + ' ' + users.get_current_user().email()
                thesis= Thesis.query().fetch()
                student= Student.query().fetch()
                adviser= Faculty.query().fetch()
                university=University.query().fetch()
                department=Department.query().fetch()
                college=College.query().fetch()
                template_values = {
                   'url': url,
                   'url_linktext': url_linktext,
                   'student':student,
                   'adviser': adviser,
                   'thes': thesis,
                   'university': university,
                   'college': college,
                   'department': department,
              
                }
                self.response.write(template.render(template_values))  
            else:
                self.redirect('/register')
        else:
            self.redirect('/login')        

    def post(self):
        department=Department()
        department.name=self.request.get("name")
        department.chairperson=self.request.get("chairperson")
        department.put()
        self.redirect('/home')


app = webapp2.WSGIApplication([

    ('/setup', SetupDBHandler),
    ('/csv', ImportHandler),
    ('/api/thesis', APIThesis),

    ('/register' , RegistrationPageHandler),
    ('/login', LoginPage),
    ('/search', Search),


    ('/home',HomePage),
    ('/',HomePage),


    ('/thesis/home',ThesisHome),
    ('/student/home',StudentHome),
    ('/faculty/home',FacultyHome),
    ('/university/home',UniversityHome),
    ('/college/home',CollegeHome),


    ('/thesis/list',ThesisList),
    ('/thesis/list/all',ThesisList),
    ('/thesis/create',ThesisCreate),
    ('/thesis/edit/(\d+)',ThesisEdit),
    ('/thesis/delete/(\d+)',ThesisDelete),
    ('/thesis/(\d+)',ThesisDetailsPage),

    ('/student/create',StudentCreate),
    ('/student/list',StudentList),
    ('/student/edit/(\d+)',StudentEdit),
    ('/student/delete/(\d+)',StudentDelete),
    ('/student/(\d+)',StudentDetailsPage),

    ('/faculty/create',FacultyCreate),
    ('/faculty/list',FacultyList),
    ('/faculty/edit/(\d+)',FacultyEdit),
    ('/faculty/delete/(\d+)',FacultyDelete),
    ('/faculty/(\d+)',FacultyDetailsPage),

    ('/university/create',UniversityCreate),
    ('/university/list',UniversityList),
    ('/university/edit/(\d+)',UniversityEdit),
    ('/university/delete/(\d+)',UniversityDelete),
    ('/university/(\d+)',UniversityDetailsPage),

    ('/college/create',CollegeCreate),
    ('/college/list',CollegeList),
    ('/college/edit/(\d+)',CollegeEdit),
    ('/college/delete/(\d+)',CollegeDelete),
    ('/college/(\d+)',CollegeDetailsPage),

    ('/department/create',DepartmentCreate),
 

 
 

    # ('/student/list',StudentList),

], debug=True)