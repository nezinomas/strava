from datetime import datetime
from crispy_forms.helper import FormHelper
from django import forms

from .models import Goals


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goals
        fields = ["year", "month", "hours"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["year"].initial = datetime.now().year

        self.helper = FormHelper()