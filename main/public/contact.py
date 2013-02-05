from django import forms

from crispy_forms.helper import FormHelper
#from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField()
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('subject', css_class='input-xlarge'),
        Field('message', rows="3", css_class='input-xlarge'),
        Field('sender', css_class='input-xlarge'),
        Field('cc_myself', css_class='checkbox'),
        FormActions(
            Submit('save_changes', 'Save changes', css_class="btn-primary"),
            Submit('cancel', 'Cancel', css_class="btn-link"),
        )
    )
