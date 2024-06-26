from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from .models import Question, Choice
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.db.models import Count


class IndexView(generic.ListView):
	template_name = 'polls/index.html'
	context_object_name = 'latest_question_list'

	def get_queryset(self):
		"""Return the last five published questions."""
		questions = Question.objects.annotate(num_choices=Count('choice')).filter(num_choices__gte=1).filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
		return questions

class DetailView(generic.DetailView):
	model = Question
	template_name = 'polls/detail.html'
 
	def get_queryset(self):
		"""
		Excludes any questions that aren't published yet.
		"""
		question = Question.objects.annotate(num_choices=Count('choice')).filter(num_choices__gte=1).filter(pub_date__lte=timezone.now())
		return question


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'



def vote(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	try:
		selected_choice = Choice.objects.get(pk=request.POST['choice'])
	except (KeyError, Choice.DoesNotExist):
		return render(request, 'polls/detail.html', {'question': question, 'error_message': "You didn't select a choice."})
	else:
		selected_choice.votes += 1
		selected_choice.save()
	return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))