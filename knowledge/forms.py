from django import forms
from django.utils.translation import ugettext_lazy as _

from . import settings
from knowledge.models import Question, Response, Category
from knowledge.widgets import CustomRelatedFieldWidgetWrapper
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.urls import reverse

OPTIONAL_FIELDS = ['alert', 'phone_number', 'categories', 'status']


__todo__ = """
This is serious badness. Really? Functions masquerading as
clases? Lame. This should be fixed. Sorry.
                                                    ~bryan
"""


def QuestionForm(user, *args, **kwargs):
    """
    Build and return the appropriate form depending
    on the status of the passed in user.
    """

    if user.is_anonymous:
        if not settings.ALLOW_ANONYMOUS:
            return None
        else:
            selected_fields = ['name', 'email', 'title', 'body']
    else:
        selected_fields = ['user', 'title', 'body', 'categories']

    if settings.ALERTS:
        selected_fields += ['alert']

    class _QuestionForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(_QuestionForm, self).__init__(*args, **kwargs)

            for key in self.fields:
                if not key in OPTIONAL_FIELDS:
                    self.fields[key].required = True

            # a bit of a hack...
            # hide a field, and use clean to force
            # a specific value of ours
            for key in ['user']:
                qf = self.fields.get(key, None)
                if qf:
                    qf.widget = qf.hidden_widget()
                    qf.required = False
            
            self.fields['categories'].queryset = Category.objects.all()

        # honey pot!
        phone_number = forms.CharField(required=False)

        def clean_user(self):
            return user

        class Meta:
            model = Question
            fields = selected_fields

    return _QuestionForm(*args, **kwargs)


def ResponseForm(user, question, *args, **kwargs):
    """
    Build and return the appropriate form depending
    on the status of the passed in user and question.
    """

    if question.locked:
        return None

    if not settings.FREE_RESPONSE and not \
            (user.is_staff or question.user == user):
        return None

    if user.is_anonymous:
        if not settings.ALLOW_ANONYMOUS:
            return None
        else:
            selected_fields = ['name', 'email']
    else:
        selected_fields = ['user']

    selected_fields += ['body', 'question']

    if settings.ALERTS:
        selected_fields += ['alert']

    class _ResponseForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(_ResponseForm, self).__init__(*args, **kwargs)

            for key in self.fields:
                if not key in OPTIONAL_FIELDS:
                    self.fields[key].required = True

            # a bit of a hack...
            for key in ['user', 'question']:
                qf = self.fields.get(key, None)
                if qf:
                    qf.widget = qf.hidden_widget()
                    qf.required = False

            self.status = 'inherit'

        # honey pot!
        phone_number = forms.CharField(required=False)

        def clean_user(self):
            return user

        def clean_question(self):
            return question

        class Meta:
            model = Response
            fields = selected_fields

    return _ResponseForm(*args, **kwargs)
