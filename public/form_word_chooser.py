from django import forms

from crispy_forms.helper import FormHelper
#from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import FormActions
from django.core.exceptions import ValidationError
from public.models import WordUse


def validate_word(new_word):
    try:
        WordUse.objects.get(word__exact=new_word)
        raise ValidationError('The word "%s" has already been used' % new_word)
    except WordUse.DoesNotExist:
        pass


class WordChooserForm(forms.Form):
    new_word = forms.CharField(max_length=100, validators=[validate_word])

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('new_word', css_class='input-xlarge'),
        FormActions(
            Submit('use', 'Use word', css_class="btn-primary"),
            Submit('cancel', 'Cancel', css_class="btn-link"),
        )
    )
