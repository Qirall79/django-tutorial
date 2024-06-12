import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.db.models import Count

from .models import Question, Choice

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
        
def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question_id):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    return Choice.objects.create(question_id=question_id, choice_text='this is a choice')

class QuestionIndexViewTests(TestCase):
    
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
    
    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_choice(question_id=question.pk)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question1 = create_question(question_text="Past question.", days=-30)
        create_choice(question_id=question1.pk)
        question2 = create_question(question_text="Future question.", days=30)
        create_choice(question_id=question2.pk)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question1],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        create_choice(question_id=question1.pk)
        question2 = create_question(question_text="Past question 2.", days=-5)
        create_choice(question_id=question2.pk)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )
     
class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        create_choice(question_id=future_question.pk)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        create_choice(question_id=past_question.pk)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionChoiceTests(TestCase):
	def test_question_without_choice(self):
		"""
			The questions published without choices
		"""
		question = create_question(question_text='question without choice', days=-1)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerySetEqual(response.context['latest_question_list'], [])

	def test_question_with_choice(self):
		"""
			The questions published with 2 choices
		"""
		question = create_question(question_text='question without choice', days=-1)
		create_choice(question_id=question.pk)
		create_choice(question_id=question.pk)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerySetEqual(response.context['latest_question_list'], [question])
		