# main.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from gevent.pywsgi import WSGIServer
from .models import User,Link, db

#------- image crawling part
from .g_images_download import googleimagesdownload   #importing the library
from random import randint
import random

# init SQLAlchemy so we can use it later in our models

goog_respond = googleimagesdownload()  # class instantiation


main = Blueprint('main', __name__)

arguments = {"keywords": "cat", "no_download": "no_download", "limit": 30}  # creating list of arguments


@main.route('/', methods=['GET', 'POST'])
def index():
    text = "cat"

    user = current_user

    img_list = Link.query.join(User).filter_by(name=user.name).all()
    # if it is the first time visiting the webpage
    if (len(img_list)==0):
        img_list = Link.query.join(User).filter_by(name='Guest').all()

    #update the page with new search
    if request.method == 'POST':
        text = request.form['text']
        
        # Check to see if is already exists or not
        img_list = Link.query.filter_by(key_word=text).all()


    if(len(img_list)==0):
        img_list = goog_search(text)
        update_the_database(text,img_list)
        #retrive it from db again
        img_list = Link.query.filter_by(key_word=text).all()



    return update_content(img_list,'index.html')

    




def update_content(img_list,html_name):
    imgs = random.sample(img_list, 6)
    #if (current_user.is_active):
    return render_template(html_name, name1=imgs[0].link, name2=imgs[1].link, name3=imgs[2].link \
                                        ,name4=imgs[3].link, name5=imgs[4].link, name6=imgs[5].link )
    '''else:
        return render_template(html_name, name1=imgs[0], name2=imgs[1], name3=imgs[2] \
                               , name4=imgs[3], name5=imgs[4], name6=imgs[5])'''

def update_the_database(text,img_list):
    '''
        gets the key_word and updates the databse
        with found image_lists
    '''

    #user_name= current_user.name
    # if the key_word exists before 
    
    user = current_user    
    if (user.is_anonymous):
        user = User.query.filter_by(name='Guest').first()
        if (not user):
            user = User(email='guest@test.com',password='123',name='Guest')
            db.session.add(user)

    # adding to databse
    for img in (img_list):
        link = Link(key_word=text, link=img, owner = user)
        # user.link = link
        db.session.add(link)
    # submit only if the user is registered

    db.session.commit()
    #else:
        #save_it and wait for the login


def goog_search(text):
    if text == "":
        text = "cat"
    arguments["keywords"] = text
    paths, img_list = goog_respond.download(arguments)  # passing the arguments to the function
    return img_list

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


