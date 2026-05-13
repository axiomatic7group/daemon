from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

server_type_list = [
    ('llama.cpp', 'llama.cpp'),
    ('vllm', 'vllm'),
]

chat_type_list = [
    ('admin', 'admin'),
    ('support', 'support'),
]

chat_sender_list = [
    ('user', 'user'),
    ('model', 'model'),
]

personality_type_list = [
    ('behavior', 'behavior'),
    ('outcome', 'outcome'),
    ('agent', 'agent'),
    ('other', 'other'),
]

class model_connection(models.Model):
    date_created = models.DateTimeField('date created', default=timezone.now)
    model_connection_name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    model_base = models.CharField(max_length=150)
    model_api_key = models.CharField(max_length=150, blank=True, default="")
    input_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)
    output_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)

class model_intiate(models.Model):
    date_created = models.DateTimeField('date created', default=timezone.now)
    model_connection_name = models.OneToOneField(model_connection, on_delete=models.CASCADE, unique=True)
    name_nd_quant = models.CharField(max_length=150)
    path_to_build = models.CharField(max_length=150)
    server_type = models.CharField(max_length=100, choices=server_type_list, default='llama.cpp')

class model_chats(models.Model):
    date_created = models.DateTimeField('date created', default=timezone.now)
    model_connection_name = models.ForeignKey(model_connection, on_delete=models.CASCADE, unique=False)
    chat_user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)
    chat_type = models.CharField(max_length=100, choices=chat_type_list, default='admin')
    chat_title = models.CharField(max_length=75, default='')

class model_chats_summary(models.Model):
    date_created = models.DateTimeField('date created', default=timezone.now)
    model_chat = models.OneToOneField(model_chats, on_delete=models.CASCADE)
    chat_summary = models.CharField(max_length=7500)
    chat_title = models.CharField(max_length=75)
    
class chat_messages(models.Model):
    date_created = models.DateTimeField('date created', default=timezone.now)
    message_model_chats = models.ForeignKey(model_chats, on_delete=models.CASCADE, unique=False)
    chat_sender = models.CharField(max_length=100, choices=chat_sender_list)
    chat_meta = models.CharField(max_length=500)
    chat_message = models.CharField(max_length=50000)

class chat_message_summarized(models.Model):
    date_summairzed = models.DateTimeField('date created', default=timezone.now)
    chat_message = models.OneToOneField(chat_messages, on_delete=models.CASCADE)
    chat_summarized = models.BooleanField(default=False)

class chat_message_private_summary(models.Model):
    date_created = models.DateTimeField('date created', default=timezone.now)
    model_chat = models.OneToOneField(model_chats, on_delete=models.CASCADE)
    chat_private_summary = models.CharField(max_length=75000)


class model_personality(models.Model):
    date_created = models.DateTimeField('date created', default=timezone.now)
    personality_name = models.CharField(max_length=75)
    personality_description = models.CharField(max_length=75000)
    personality_type = models.CharField(max_length=100, choices=personality_type_list, default='behavior')


class message_attachement(models.Model):
    datetime_created = models.DateTimeField('date created', default=timezone.now)
    attachemnet_task = models.ForeignKey(chat_messages, on_delete=models.CASCADE)
    attachemnet = models.CharField(max_length=500, default='')

