import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category,db

QUESTIONS_PER_PAGE = 10
def pagination_quesions(request,selection):
  page = request.args.get('page',1,type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  Questions = [question.format() for question in selection]
  current_ques = Questions[start:end]
  return current_ques

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app,resources={r"/api/*": {"origins": "*"}})
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response
 

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
      categories1 = Category.query.all()
      if len(categories1) == 0:
            abort(404)

      return jsonify({
        'success':True,
        'categories':{category.id: category.type for category in categories1}
      
      })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

 
  @app.route('/questions', methods=['GET'])
  def get_questions():
      selection = Question.query.order_by(Question.id).all()
      current_qes = pagination_quesions(request,selection)
      categories1 = Category.query.all()
      if len(current_qes) == 0:
          abort(404)
      return jsonify({
            'success':True,
            'questions':current_qes,
            'total_questions':len(Question.query.all()),
            'categories':{category.id: category.type for category in categories1}
            
          })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_question(question_id):
      try:
          question = Question.query.get(question_id)
          question.delete()
          return jsonify({
                'success':True,
                'deleted':question_id
                  })
      except:
        abort(422) 
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question():
      body = request.get_json()
      search_term = body.get('searchTerm',None)
      if search_term:
        search_res = Question.query.filter(Question.question.ilike("%" + search_term + "%")).all()
        current_qes = pagination_quesions(request,search_res)
      
      return jsonify({
              'success':True,
              'questions':current_qes,
              'total_questions':len(search_res),
              'current_category':None
                })
      abort(404) 
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
      body = request.get_json()
      ques = body.get('question')
      ans = body.get('answer')
      difficulty_score = body.get('difficulty')
      category = body.get('category')
      try:
          question = Question(question=ques,answer=ans,difficulty=difficulty_score,category=category)
          question.insert()
          
          return jsonify({
                'success':True,
                'created':question.id
                  })
      except:
        abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<category_id>/questions', methods=['GET'])
  def questions_by_category(category_id):

        try:
            questions = Question.query.filter(Question.category == category_id).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': category_id
            })
        except:
            abort(404)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def quiz():

        try:

            body = request.get_json()
            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)

            category = body.get('quiz_category')
            pre_que = body.get('previous_questions')

            if category['type'] == 'click':
                questions = Question.query.filter(
                    Question.id.notin_((pre_que))).all()
            else:
                questions = Question.query.filter_by(
                    category=category['id']).filter(Question.id.notin_((pre_que))).all()

            random_questions = questions[random.randrange(5, len(questions))].format() if len(questions) > 0 else None

            return jsonify({
                'success': True,
                'question': random_questions
            })
        except:
            abort(422)
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400
  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404
  @app.errorhandler(422)
  def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422     
  return app

    