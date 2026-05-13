import pandas as pd
from bots.models import *
from django.core.management.base import BaseCommand, CommandError

import subprocess, requests


def initiate_model(model_int_id):
    if model_intiate.objects.filter(id=model_int_id).exists:
        model_to_initiate = pd.DataFrame(model_intiate.objects.filter(id=model_int_id).values())
        model_to_initiate_conn = pd.DataFrame(model_connection.objects.filter(id=model_to_initiate['model_connection_name_id'].iloc[0]).values())

        try:
            response = requests.head(model_to_initiate_conn['model_base'].iloc[0], timeout=5)
            return {"message":"model is available",
                "state":"1"}
        except:
            x = 0

    else:
        return {"message":"model not found",
                "state":"0"}

    try:
        cmd = [
            "./llama-server", 
            "-hf", model_to_initiate['name_nd_quant'].iloc[0], 
            "-ngl", "99",]
        process = subprocess.Popen( cmd, cwd=model_to_initiate['path_to_build'].iloc[0])
        
        return process
        
    except Exception as e:
        print(f"Failed to start server: {e}")
        return None



class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('model_to_initiate', type=int)

    def handle(self, *args, **options):
        model_to_initiate = options['model_to_initiate']
        initiate_model(model_to_initiate)