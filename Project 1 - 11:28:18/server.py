#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import datetime
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
PRO_ID=['X']


# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "lh2922"
DB_PASSWORD = "r5gq4aky"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass
product_info = ['a','b']

#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print datetime.datetime.now()


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT R.product_brand, R.product_name, AVG(R.rating) FROM Review_Posts R GROUP BY R.product_brand, R.product_name ORDER BY AVG(R.rating) DESC LIMIT 5")
  info = []
  cnt = 1
  for result in cursor:
    dic = dict()
    dic['product_brand'] = result[0]
    dic['product_name'] = result[1]
    dic['rating'] = result[2]
    dic['cnt'] = cnt
    cnt += 1
    info.append(dic)
  cursor.close()
  context = dict(data = info)

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("homepage.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/to_addUser')
def to_addUser():
  return render_template("addUser.html")

@app.route('/to_addArticle')
def to_addArticle():
  return render_template("addArticle.html")

@app.route('/to_addReview')
def to_addReview():
  return render_template("addReview.html")

@app.route('/homepage')
def homepage():
  cursor = g.conn.execute("SELECT R.product_brand, R.product_name, AVG(R.rating) FROM Review_Posts R GROUP BY R.product_brand, R.product_name ORDER BY AVG(R.rating) DESC LIMIT 5")
  info = []
  cnt = 1
  for result in cursor:
    dic = dict()
    dic['product_brand'] = result[0]
    dic['product_name'] = result[1]
    dic['rating'] = result[2]
    dic['cnt'] = cnt
    cnt += 1
    info.append(dic)
  cursor.close()
  context = dict(data = info)
  print datetime.datetime.now()
  return render_template("homepage.html", **context)

@app.route('/allArticle')
def allArticle():
  cursor = g.conn.execute("SELECT article_post_time,article_text,article_image_url,users_id FROM Article_Posts")
  info1 = []
  for result in cursor:
    dic = dict()
    dic['article_post_time'] = result[0]
    dic['article_text'] = result[1]
    dic['article_image_url'] = result[2]
    dic['users_id'] = result[3]
    info1.append(dic)
  cursor.close()
  cursor = g.conn.execute("SELECT comment_users_id,article_reply_time,comment_text, article_post_time,article_users_id FROM Comment_Replies")
  info2 = []
  for result in cursor:
    dic = dict()
    dic['comment_users_id'] = result[0]
    dic['article_reply_time'] = result[1]
    dic['comment_text'] = result[2]
    dic['article_post_time'] = result[3]
    dic['article_users_id'] = result[4]
    info2.append(dic)
  cursor.close()
  context = dict(Article = info1,Comment = info2)
  return render_template("allArticle.html", **context)


@app.route('/productList',methods=['GET'])
def productList():
  cursor = g.conn.execute("SELECT product_brand, product_name, product_image_url,category,price FROM Product")
  info = []
  cnt = 1
  for result in cursor:
    dic = dict()
    dic['product_brand'] = result[0]
    dic['product_name'] = result[1]
    dic['product_image_url'] = result[2]
    dic['category'] = result[3]
    dic['price'] = result[4]
    dic['cnt'] = cnt
    info.append(dic)
    cnt += 1
  cursor.close()
  context = dict(Product = info)
  return render_template("productList.html", **context)
PRO_ID=['a','b']
@app.route('/product',methods=['POST'])
def product():
  product_brand = request.form['product_brand']
  product_name = request.form['product_name']
  PRO_ID[0] = product_brand
  PRO_ID[1] = product_name
  cursor = g.conn.execute(text("SELECT product_brand, product_name, product_image_url,category,price FROM Product WHERE product_brand = :product_brand AND product_name = :product_name "),product_brand=product_brand,product_name = product_name)
  info1 = []
  for result in cursor:
    dic = dict()
    dic['product_brand'] = result[0]
    dic['product_name'] = result[1]
    dic['product_image_url'] = result[2]
    dic['category'] = result[3]
    dic['price'] = result[4]
    info1.append(dic)
  cursor.close()
  cursor = g.conn.execute(text("SELECT users_id, rating, review_text,review_time FROM Review_Posts WHERE product_brand = :product_brand AND product_name = :product_name "),product_brand=product_brand,product_name = product_name)
  info2 = []
  for result in cursor:
    dic = dict()
    dic['users_id'] = result[0]
    dic['rating'] = result[1]
    dic['review_text'] = result[2]
    dic['review_time'] = result[3]
    info2.append(dic)
  cursor.close()
  cursor = g.conn.execute(text("WITH I AS(SELECT I1.ingredient_id, I1.function,I1.description,II.ingredient_name FROM Ingredient I1 JOIN Ingredient_Names_Relates II \
                ON I1.ingredient_id = II.ingredient_id) \
                SELECT I.ingredient_id, I.ingredient_name, I.function, I.description FROM Contains C JOIN I \
                ON C.ingredient_id = I.ingredient_id \
                WHERE C.product_brand = :product_brand AND \
                C.product_name = :product_name "),product_brand=product_brand,product_name = product_name)
  info3 = []
  for result in cursor:
    dic = dict()
    dic['ingredient_id'] = result[0]
    dic['ingredient_name'] = result[1]
    dic['function'] = result[2]
    dic['description'] = result[3]
    
    info3.append(dic)
  cursor.close()
  info4 = []
  cursor = g.conn.execute(text("SELECT COUNT(*)\
                                FROM Review_Posts R\
                                WHERE R.product_brand = :product_brand AND\
                                R.product_name = :product_name"),product_brand=product_brand,product_name = product_name)
  for result in cursor:
    dic = dict()
    dic['num'] = result[0]
    info4.append(dic)
  cursor.close()
  print info4
  context = dict(Product = info1,Review = info2,Ingredients = info3,totalReviews = info4)
  return render_template("product.html", **context)


# Example of adding new data to the database

@app.route('/addUser', methods=['POST'])
def addUser():
  users_id = request.form['users_id']
  users_name = request.form['users_name']
  hair_color = request.form['hair_color']
  eye_color = request.form['eye_color']
  skin_type = request.form['skin_type']
  date_of_birth = request.form['date_of_birth']
  #print name
  #users_id need to be different from each other
  result = g.conn.execute(text('SELECT users_id from Users'))
  user_id_list = []
  for r in result:
      user_id_list.append(str(r[0]))
  if users_id in user_id_list:
      return render_template('useriderror.html')
  else:
      cmd = 'INSERT INTO Users(users_id,users_name,hair_color,eye_color,skin_type,date_of_birth) VALUES (:users_id,:users_name,:hair_color,:eye_color,:skin_type,:date_of_birth)';
      g.conn.execute(text(cmd), users_id = users_id, users_name = users_name,  hair_color = hair_color, eye_color = eye_color, skin_type = skin_type ,date_of_birth=date_of_birth);
      return render_template("successfulcreate.html")

@app.route('/addArticle', methods=['POST'])
def addArticle():
  a = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  article_text = request.form['article_text']
  users_id = request.form['users_id']
  article_image_url = request.form['article_image_url']

  cmd = 'INSERT INTO Article_Posts(article_post_time,article_text,article_image_url,users_id) \
  VALUES(:article_post_time,:article_text,:article_image_url,:users_id)'
  g.conn.execute(text(cmd),\
    article_post_time= a ,article_text=article_text,article_image_url = article_image_url, users_id=users_id)
  return render_template('successfulcreate.html')

@app.route('/addReview', methods=['POST'])
def addReview():
  a = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  users_id = request.form['users_id']
  product_name = PRO_ID[1]
  product_brand = PRO_ID[0]
  rating = request.form['rating']
  review_text = request.form['review_text']
  cmd = 'INSERT INTO Review_Posts(users_id,product_brand,product_name,review_text,review_time,rating) \
  VALUES(:users_id,:product_brand,:product_name,:review_text,:review_time,:rating)'
  g.conn.execute(text(cmd),users_id=users_id,product_brand=product_brand,product_name = product_name, review_text=review_text,review_time=a,rating=rating)
  return render_template('reviewsuccessful.html')

@app.route('/addComment',methods=["POST"])
def addComment():
  a = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  article_users_id = request.form['article_users_id']
  article_post_time = request.form['article_post_time']
  comment_users_id = request.form['comment_users_id']
  comment_text = request.form['comment_text']
  cmd = 'INSERT INTO Comment_Replies(article_users_id,article_post_time,comment_users_id,comment_text,article_reply_time) VALUES (:article_users_id,:article_post_time,:comment_users_id,:comment_text,:article_reply_time)'
  g.conn.execute(text(cmd),article_users_id = article_users_id,article_post_time=article_post_time, comment_users_id=comment_users_id, comment_text=comment_text, article_reply_time = a)
  return render_template("commentsuccessful.html")


@app.route('/addResponse', methods=['POST'])
def addResponse():
  original_users_id = request.form['original_users_id']
  responding_users_id = request.form['responding_users_id']
  helpful = request.form['helpful']
  review_time = request.form['review_time']
  product_brand = PRO_ID[0]
  product_name = PRO_ID[1]
  cmd = 'INSERT INTO Responds(original_users_id,responding_users_id,product_brand,product_name,review_time,helpful) \
  VALUES(:original_users_id,:responding_users_id,:product_brand,:product_name,:review_time,:helpful)'
  g.conn.execute(text(cmd),original_users_id=original_users_id,responding_users_id = responding_users_id,product_brand = product_brand,product_name=product_name,review_time=review_time,helpful = helpful)
  return render_template("homepage.html")

@app.route('/deletecomment', methods=['POST'])
def deletecomment():
    comment_users_id = request.form['d_comment_users_id']
    article_reply_time = request.form['d_article_reply_time']
    cmd = 'DELETE FROM Comment_Replies WHERE comment_users_id = :comment_users_id AND article_reply_time = :article_reply_time'
    g.conn.execute(text(cmd),comment_users_id=comment_users_id,article_reply_time = article_reply_time)
    return render_template("deletesuccessful.html")

@app.route('/Iwant',methods=['POST'])
def Iwant():
    ingredient_name = request.form['ingredient_name']
    cmd = 'SELECT DISTINCT C.product_brand, C.product_name FROM Contains C JOIN Ingredient I \
                            ON C.ingredient_id = I.ingredient_id \
                            WHERE I.ingredient_id = (SELECT R.ingredient_id \
                            FROM Ingredient_Names_Relates R \
                            WHERE R.ingredient_name = :ingredient_name)'
    cursor = g.conn.execute(text(cmd),ingredient_name=ingredient_name)
    info = []
    for result in cursor:
        dic = dict()
        dic['product_brand'] = result[0]
        dic['product_name'] = result[1]
        info.append(dic)
    cursor.close()
    context = dict(Product = info)
    return render_template("Iwant.html",**context)

@app.route('/profile',methods=['POST'])
def profile():
    users_id = request.form['users_id']
    cmd = 'SELECT * FROM Users \
                            WHERE Users.users_id = :users_id'
    cursor = g.conn.execute(text(cmd),users_id=users_id)
    info = []
    for result in cursor:
        dic = dict()
        dic['users_id'] = result[0]
        dic['users_name'] = result[1]
        dic['hair_color'] = result[2]
        dic['eye_color'] = result[3]
        dic['skin_type'] = result[4]
        dic['date_of_birth'] = result[5]
        info.append(dic)
    cursor.close()
    context = dict(Users = info)
    return render_template("profile.html",**context)

@app.route('/mostPopular')
def mostPopular():
  cursor = g.conn.execute(text("SELECT R.product_brand, R.product_name, COUNT(*)\
                                FROM Review_Posts R \
                                GROUP BY R.product_brand, R.product_name \
                                ORDER BY COUNT(*) DESC \
                                LIMIT 3"))
  info = []
  cnt = 1
  for result in cursor:
    dic = dict()
    dic['product_brand'] = result[0]
    dic['product_name'] = result[1]
    dic['count'] = result[2]
    dic['cnt'] = cnt
    cnt += 1
    info.append(dic)
  cursor.close()
  context = dict(List = info)
  return render_template("mostPopular.html", **context)



@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
