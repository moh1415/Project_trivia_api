import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:1415@localhost:5432/trivia_test";
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


    def get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    def not_found_category(self):
        res = self.client().get('/categories/1000')
        data = json.loads(res.data)

    def not_found_for_wrong_page_number(self):
        res = self.client().get('/questions?page=100000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    def test_delete_question(self):
        question_id = 2
        res = self.client().delete('/questions/{question_id}')
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)

    def search_questions(self):
        new_term = {'searchTerm': 'a'}
        res = self.client().post('/questions/search', json=new_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])
    def not_found_search_question(self):
        new_term = {'searchTerm': '',}
        res = self.client().post('/questions/search', json=new_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    def test_add_question(self):
        question = {
            'question': 'test 1',
            'answer': 'new test',
            'difficulty': 5,
            'category': 1
        }
        total_questions_before = len(Question.query.all())
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)
        total_questions_after = len(Question.query.all())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()