from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django import forms
from django.forms.widgets import DateInput

from .models import *
from django.contrib.auth.models import User 


### model_intiate
### model_chats
### chat_messages

class models_list_view(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f" {obj.model_name} , - {obj.model_connection_name}"

class model_chats_list_view(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f" {obj.chat_title} , - {obj.model_connection_name}"


class create_model_connection_form(ModelForm):
    
    class Meta:
        model = model_connection
        exclude = ['date_created']
        fields = '__all__'

class create_model_intiate_form(ModelForm):
    model_connection_name = models_list_view(queryset=model_connection.objects.all())
    
    class Meta:
        model = model_intiate
        exclude = ['date_created']
        fields = '__all__'

class create_model_chats_form(ModelForm):
    model_connection_name = models_list_view(queryset=model_connection.objects.all())
    
    class Meta:
        model = model_chats
        exclude = ['date_created']
        fields = '__all__'

class create_chat_messages_form(ModelForm):
    chat_message = forms.CharField( label="", widget=forms.Textarea(attrs={'placeholder': 'what can I help you with today :)'}))
    
    class Meta:
        model = chat_messages
        exclude = ['date_created', 'message_model_chats', 'chat_sender', 'chat_meta']
        fields = '__all__'

class create_model_personality_form(ModelForm):
    
    class Meta:
        model = model_personality
        exclude = ['date_created', 'personality_type',]
        fields = '__all__'


class create_model_summary(ModelForm):
    chat_summary = forms.CharField( label="", widget=forms.Textarea())
    
    class Meta:
        model = model_chats_summary
        exclude = ['date_created', 'chat_title', 'model_chat']
        fields = '__all__'

class create_model_private_summary(ModelForm):
    chat_private_summary = forms.CharField( label="", widget=forms.Textarea())
    
    class Meta:
        model = chat_message_private_summary
        exclude = ['date_created', 'model_chat']
        fields = '__all__'