# main.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, Response
from flask_login import login_required, current_user
from gevent.pywsgi import WSGIServer
from .models import User,Link, db
import json
import pdb
#--------------- bing packages
import os, urllib.request, re, threading, posixpath, urllib.parse, argparse, socket, time, hashlib, pickle, signal, imghdr



#------- image crawling part
#from .google_images_download import googleimagesdownload   #importing the library
from .g_dl_2 import googleimagesdownload
from .bbid  import fetch_images_from_keyword
#from .g_images_download import googleimagesdownload   #importing the library
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

    # search for the in google
    arguments= {}
    img_list  = search_the_images(text,img_list,arguments)
    
    return update_content(img_list,'index.html')


@main.route('/similar', methods=['POST'])
def get_similar_links():
    
    data = request.form['src']
    
    # #setting the args for similar images
    arguments = {"similar_images":data, "limit":18, "no_download": "no_download"}
    #paths,err, imgs = goog_respond.download(arguments)  # passing the arguments to the function

    # update the datbase
    imgs = search_the_images('',[],arguments)
    data = []
    for i in range (0,6):
        data.append({'img': str(imgs[i])})
    
    data_json = json.dumps(data)
    resp = Response(response=data_json, status=200, mimetype="application/json")
    return resp 
   
def search_the_images(text, img_list,arguments):
    '''
    search for the given text in google
    '''
    counter = 0

    # we should find at least 6 images in our search
    while(len(img_list)<6):
        #search for similar images
        if (text == ''):         
            imgl_ist = []   
            paths,err, imglist = goog_respond.download(arguments)  # passing the arguments to the function
            for img in imglist:
                element = {'image_link':img}
                img_list.append(element)

        else: # normal search for text
            img_list = goog_search(text)
        #img_list = bing_search(text)

        update_the_database(text,img_list)
        #retrive it from db again
        img_list = Link.query.filter_by(key_word=text).all()
        counter = counter +1
        # if there is no results for this query
        if (counter > 6) :
            img_list = Link.query.filter_by(key_word="cat").all()
            break

    return img_list

@main.route('/magic', methods=['GET'])
def ajax_route():
    '''
    for providing images from database
    '''

    user = current_user
    print (user)

    img_list = Link.query.join(User).filter_by(name=user.name).all() 
    
    # try at least 6 times to search  and find something   
    while (len(img_list)<6):
        img_list = Link.query.join(User).filter_by(name='Guest').all()

    imgs = random.sample(img_list, 6)    
    data = []
    for i in range (0,6):
        data.append({'img': str(imgs[i].link)})

    data_json = json.dumps(data)
    resp = Response(response=data_json, status=200, mimetype="application/json")
    return resp 

def update_content(img_list,html_name):
    try:
        imgs = random.sample(img_list, 6)        
        return render_template(html_name, name1=imgs[0].link, name2=imgs[1].link, name3=imgs[2].link \
                                            ,name4=imgs[3].link, name5=imgs[4].link, name6=imgs[5].link )
    except:
        print("Error ----OOPS !!images are not rettived-----")



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
    #print("--------list of imgaes",img_list)
    
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
    arguments["keywords"] = str(text)
    paths,err, img_list = goog_respond.download(arguments)  # passing the arguments to the function
    return img_list

def bing_search(text):
    '''
    search in bb
    '''
    
    adlt = 'off'
    threads = 10
    pool_sema = threading.BoundedSemaphore(threads)
    if text == "":
        text = "cat"
    output_dir = './bing' #default output dir
    #parser.add_argument('--filters', help = 'Any query based filters you want to append when searching for images, e.g. +filterui:license-L1', required = False)
    filters = ''
    limit = 20

    img_list = fetch_images_from_keyword(pool_sema, text ,output_dir, filters, limit)
    return img_list

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)



