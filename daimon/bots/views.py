from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.views import View
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.contrib.auth.forms import AuthenticationForm

import pandas as pd
import json, re,requests, random, os, urllib.parse, subprocess, ast, markdown
from bs4 import BeautifulSoup
from .models import *
from .forms import *

from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader, PythonLoader, TextLoader

from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from quicksand.quicksand import quicksand

from typing import List, Literal
from pydantic import BaseModel, Field
from tempfile import NamedTemporaryFile

UPLOAD_FOLDER = "/home/daniel/Desktop/test/"

fast_personality = "You are an AI assitant being obeserved for your efficiency and performance. Along with these instructions you will be provided context to answer the questions you are asked." \
"Use predominately the context material to generate your answer, if not enough information is provided, specify that in your respons." \
"Your answers should be short and straight to the point, include the reference url to where you are getting each piece of information from as much as possible, and remember you are being observed for efficiency and accuracy."

reasoning_personality = "You are an AI assitant being obeserved for your efficiency and performance. Along with these instructions you will be provided context to answer the questions you are asked." \
"Use predominately the context material to generate your answer, if not enough information is provided, specify that in your respons." \
"Make sure to think through step-by-step before giving your answer, include the reference url to where you are getting each piece of information from as much as possible, and remember you are being observed for efficiency and accuracy."

summary_personality = "You are an AI Agent being observed for performance and efficiency." \
    "Your primary objective is to summarize the context provided in the chat history." \
    "The summary you provide will be used to replace chat history going forward and use your summary to substitute this." \
    "Be sure your summary is organized and detailed, be sure to specifically include any relevant facts, dates, names, places, ideas." \
    "Make sure that if any passwords, private keys, and such are specifically included. " \
    "Especially in coding scripts, be sure private keys and passwords/user credentials are stored specifically here, and neve in the general summary." \
    "Create subcategories in your output to specify these if needed." \
    "Your expected output inlcudes a 'general' summary, and a 'private' summary, make sure that all personally indentifiable information and/or any private information is only included in the private summary." \
    "The private summary is exclusively reserved for this type of private information, all other context and iformation is to be included in the general summary." \
    "From time to time you will also be asked to update an existing summary with new chat history, be sure to make changes as needed." \
    "Update old specific and relevant points you might have writtne down as their circumstnaces change." \
    "Again, be sure if new contact information or private information is introduced, that this infor is only updated in the private side and never included in the general summary." \
    "Be sure to keep track of ideas and thoughts and mention their progression as this summary will be used to provided feedback to the user about their chats." \
    "Remeber, you are being observed for your performance, be sure to follow instructions well and keep your repsonses brief and to the point." \
    "Make sure to think through step-by-step before giving your answer, include the reference url to where you are getting each piece of information from as much as possible, and remember you are being observed for efficiency and accuracy."

def reduce_tokens(input_text):
    if isinstance(input_text, str):
        output_text = input_text.replace('e', '').replace('a', '').replace(' an ', '').replace(' the ', '')
        return output_text
    else:
        return input_text

def get_local_search_results(search_query, links_count=4):
    url = 'https://html.duckduckgo.com/html/'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    params = {'q': search_query}
    headers = {'User-Agent': user_agent, 'Referer': 'https://duckduckgo.com/',}
    temp_html = requests.post(url, headers=headers, data=params)
    links_output = []
    if  temp_html.status_code == 200:
        soup = BeautifulSoup(temp_html.text, 'html.parser')
        links = soup.find_all('a', class_='result__a')
        for link in links:
            result_dict = {"text": link.get_text(strip=True), "url": link.get('href')}
            links_output.append(result_dict)
    else:
        search_query_url = urllib.parse.quote_plus(search_query)
        url = 'https://duckduckgo.com/search?q=' + search_query_url
        url = 'https://html.duckduckgo.com/html/search?q=' + search_query_url
        user_agent_list = ["Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36",]
        user_agent = random.choice(user_agent_list)
        headers = {'User-Agent': user_agent}

        options = Options()
        options.add_argument("--headless")
        options.add_argument(f'--user-agent={user_agent}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--excludeSwitches=enable-automation")
        options.add_argument('--excludeSwitches=enable-logging')
        options.add_argument('--useAutomationExtension=False')
        driver = Firefox(options=options)
        driver.get(url)

        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            if link.text != '':
                result_dict = {"text": link.text, "url": link.get_attribute("href")}
                links_output.append(result_dict)
        driver.quit()
    
    links_output = links_output[:links_count]
    search_output = {}
    for i, link in enumerate(links_output):
        temp_html = requests.get(link['url'], headers = headers, params=params, timeout=12)
        soup = BeautifulSoup(temp_html.content,'lxml')
        if soup.find('main') is not None:
            soup = soup.find('main')
        for match in soup.find_all('span', 'sup'):
            match.unwrap()
        
        content = soup.find_all('p')
        if content == []:
            content = soup
        content = str(content).replace('</p>', '').replace('<p>', '').replace('</a>', '')
        content = reduce_tokens(str(content))
        search_output['source '+str(i)] = {'url':link, 'context':content[:1500]}

    return search_output

def check_files(request):
    if os.path.isfile(str(request)):
        with open((request), "r", encoding="utf-8") as file:
            file_to_check = str(request)
            file_content = file.read()
    
    elif 'filename' not in request.FILES:
        return {'message': 'no file', 'state': '0'}
    else:
        file_to_check = request.FILES['filename']
        file_content = file_to_check.read()
    
    try:
        qs = quicksand(file_content)
        qs.process()
    except:
        qs = quicksand(file_to_check)
        qs.process()
    

    output = {}
    if not qs.results.get('exploits_found'):
        try:
            file_type = str(file_to_check.name).split(".")[-1].lower()
        except:
            file_type = str(file_to_check).split(".")[-1].lower()

        with NamedTemporaryFile(suffix=f".{file_type}") as tmp:
            try:
                tmp.write(file_content)
                tmp.flush()
                temp_name = tmp.name
            except:
                temp_name = str(file_to_check)
            
            if file_type == "txt" or file_type == "md":
                loader = TextLoader(temp_name, encoding='utf-8')
                
            elif file_type == "py":
                loader = PythonLoader(temp_name)
            
            elif file_type == "pdf":
                loader = PyPDFLoader(temp_name)

            else:
                return {'message': 'Unsupported type', 'state': '0'}
            
            docs = loader.load()
            full_text = "\n\n".join([doc.page_content for doc in docs])
            output["context"] = full_text
            output["state"] = "1"
    else:
        output = {'message': 'Error detected.', 'state': '0'}
    return output

def form_to_json_schema(form):
    schema = {}
    
    for name, field in form.fields.items():    
        field_data = {}
        
        if hasattr(field, 'choices') and field.choices:
            field_data['choices'] = [{'option': str(c[1])} for c in field.choices]

        schema[name] = field_data
    return schema

def check_authentication(check_request):
    if not check_request.user.is_authenticated:
        return redirect("/login")
    elif not check_request.user.is_staff:
        return redirect("/login")

def send_task_to_model(promt_message, user_request, chat_summary="",chat_tool="fast",
                        personality="", model_base="http://127.0.0.1:8080", model_name="local-model", 
                        model_api_key="dummy_key", run_tempereature=0.75, top_p=0.9,):
    
    run_model_start = ChatOpenAI( base_url=model_base, api_key=model_api_key,
        model=model_name, temperature=run_tempereature, top_p=top_p,)
    
    class StructuredResponse(BaseModel):
        status: Literal["1", "0"] = Field(description="Return '1' if successful/approved, or '0' if failed/rejected.")
        response: str = Field(description="The primary response to the user")
    
    run_model = run_model_start.with_structured_output(StructuredResponse)
    
    if chat_tool == "fast":
        system_context = {'system': {'priority':reduce_tokens(str(fast_personality)), 'secondary':reduce_tokens(personality),}, 'chat_summary':reduce_tokens(chat_summary),}
    elif chat_tool == "thinking":
        class ReasoningQuestions(BaseModel):
            questions: List[str] = Field(description="A list of 2-5 trageted reasoning questions to help answer the user prompt.")
        
        temp_prompt = ( "You are an AI assitant being obeserved for your efficiency and performance, analyze the user prompt and generate 2 to 5 deep reasoning questions that break down the complexity of the user prompt." )
        run_model_w_struct = run_model.with_structured_output(ReasoningQuestions)
        questions_list = run_model_w_struct.invoke(f"{temp_prompt}\\n\\n User Prompt:{promt_message}")
        questions_dict = []
        for i, q in enumerate(questions_list.questions):
            questions_dict.append({'question':q})
        
        temp_batch_promt = ChatPromptTemplate.from_template("{question}")
        temp_chain = temp_batch_promt | run_model_start | StrOutputParser()
        question_results = temp_chain.batch(questions_dict, config={"max_concurrency":5})

        system_context = {'system': {'priority':reduce_tokens(str(reasoning_personality)), 'secondary':reduce_tokens(personality)}, 'reasoning':question_results, 'chat_summary':reduce_tokens(chat_summary),}
    elif chat_tool == "websearch":
        system_context = {'system': {'priority':reduce_tokens(str(fast_personality)), 'secondary':reduce_tokens(personality)}, 'search':get_local_search_results(promt_message, 4), 'chat_summary':reduce_tokens(chat_summary),}
    elif chat_tool == "local_files":
        system_context = {'system': {'priority':reduce_tokens(str(reasoning_personality)), 'secondary':reduce_tokens(personality)}, 'local files':check_files(user_request), 'chat_summary':reduce_tokens(chat_summary),}
    
    user_prompt = ChatPromptTemplate.from_messages([("human", "{system_context}\n\nUser Request: {promt_message}"),])
    
    chain = user_prompt | run_model
    response = chain.invoke({"promt_message": promt_message, "system_context": system_context})
    return response


def send_message_to_model(promt_message, user_request, chat_summary="", chat_tool="fast", personality="",
                        model_base="http://127.0.0.1:8080", model_name="local-model", model_api_key="dummy_key",  
                        chat_history_list=None, run_tempereature=0.75, top_p=0.9, run_maxtokens=500):
    
    run_model = ChatOpenAI( base_url=model_base, api_key=model_api_key, model=model_name, temperature=run_tempereature, top_p=top_p,)
        
    if isinstance(chat_history_list, pd.DataFrame):
        chat_history = []

        if len(chat_history_list) == 1:
            chat_history = []
        else:
            chat_history_list = chat_history_list[:-1]
            chat_history_list = chat_history_list.sort_values('date_created')
            
            system_msgs = chat_history_list[chat_history_list['chat_sender'] == "system"]
            chat_history_list = chat_history_list[chat_history_list['chat_sender'] != "system"]
            system_content = "\n\n".join(system_msgs['chat_message'].tolist()) if not system_msgs.empty else ""

            for i_message, e_message in chat_history_list.iterrows():
                role = e_message['chat_sender']
                content = e_message['chat_message']
                
                if not chat_history and role == "user" and system_content:
                    content = f"{system_content}\n\n{content}"

                if chat_history:
                    last_msg = chat_history[-1]
                    if (role == "user" and isinstance(last_msg, HumanMessage)) or (role == "model" and isinstance(last_msg, AIMessage)):
                        last_msg.content += f"\n\n{content}"
                        continue

                if role == "user":
                    #chat_history.append(HumanMessage(content=content))
                    chat_history.append(HumanMessage(content=reduce_tokens(content)))
                elif role == "model":
                    #chat_history.append(AIMessage(content=content))
                    chat_history.append(AIMessage(content=reduce_tokens(content)))
    
    if chat_tool == "fast":

        system_context = {'system': {'priority':reduce_tokens(fast_personality), 'secondary':reduce_tokens(personality),}, 'chat_summary':reduce_tokens(chat_summary),}
    elif chat_tool == "thinking":
        class ReasoningQuestions(BaseModel):
            questions: List[str] = Field(description="A list of 2-5 trageted reasoning questions to help answer the user prompt.")
        
        temp_prompt = ( "You are an AI assitant being obeserved for your efficiency and performance, analyze the user prompt and generate 2 to 5 deep reasoning questions that break down the complexity of the user prompt." )
        run_model_w_struct = run_model.with_structured_output(ReasoningQuestions)
        questions_list = run_model_w_struct.invoke(f"{temp_prompt}\\n\\n User Prompt:{promt_message}")
        
        questions_dict = []
        for i, q in enumerate(questions_list.questions):
            questions_dict.append({'question':q})
        
        temp_batch_promt = ChatPromptTemplate.from_template("{question}")
        temp_chain = temp_batch_promt | run_model | StrOutputParser()
        question_results = temp_chain.batch(questions_dict, config={"max_concurrency":5})
        system_context = {'system': {'priority':reduce_tokens(reasoning_personality), 'secondary':reduce_tokens(personality)}, 'reasoning':question_results, 'chat_summary':reduce_tokens(chat_summary),}
    elif chat_tool == "websearch":
        system_context = {'system': {'priority':reduce_tokens(fast_personality), 'secondary':reduce_tokens(personality)}, 'search':get_local_search_results(promt_message, 4), 'chat_summary':reduce_tokens(chat_summary),}
    elif chat_tool == "local":
        system_context = {'system': {'priority':reduce_tokens(fast_personality), 'secondary':reduce_tokens(personality)}, 'local files':check_files(user_request), 'chat_summary':reduce_tokens(chat_summary),}


    user_prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"), 
    ("human", "{system_context}\n\nUser Request: {promt_message}"),])
    
    chain = user_prompt | run_model
    response = chain.invoke({"promt_message": promt_message, "system_context": system_context, "chat_history":chat_history})
    return response

def summarize_chat(model_chat_id):

    if model_chats.objects.filter(id=model_chat_id).exists:
        print('yes')
        model_chats_to_sum = pd.DataFrame(model_chats.objects.filter(id=model_chat_id).values())
        chat_model_connection = pd.DataFrame(model_connection.objects.filter(id=model_chats_to_sum['model_connection_name_id'].iloc[0]).values())
        chat_messages_to_sum = pd.DataFrame(chat_messages.objects.filter(message_model_chats_id=model_chat_id).values())
        
        check_chat_history = pd.DataFrame(chat_message_summarized.objects.filter(chat_message_id__in=chat_messages_to_sum['id'].to_list()).values())
        
        if check_chat_history.empty:
            checked_chat_history = chat_messages_to_sum
            chat_summary = ""           
        else:
            check_chat_history = check_chat_history[check_chat_history['chat_summarized']==True]
            checked_chat_history = chat_messages_to_sum[~chat_messages_to_sum['id'].isin(check_chat_history['chat_message_id'])]

            chat_summary = pd.DataFrame(model_chats_summary.objects.filter(model_chat_id=model_chat_id).values())
        run_model = ChatOpenAI(
            base_url=chat_model_connection['model_base'].iloc[0],
            api_key=chat_model_connection['model_api_key'].iloc[0],
            model=chat_model_connection['model_name'].iloc[0],
            temperature=0.1, top_p=0.1)
        
        chat_history_list = checked_chat_history
        if isinstance(chat_history_list, pd.DataFrame):
            chat_history = []
            chat_history_list.sort_values('date_created')
            chat_history_list = chat_history_list.reset_index()
            for i_message, e_message in chat_history_list.iterrows():
                role = e_message['chat_sender']
                content = e_message['chat_message']

                if chat_history:
                    last_msg = chat_history[-1]
                    if (role == "user" and isinstance(last_msg, HumanMessage)) or (role == "model" and isinstance(last_msg, AIMessage)):
                        last_msg.content += f"\n\n{content}"

                if role == "user":
                    chat_history.append(HumanMessage(content=content))
                elif role == "model":
                    chat_history.append(AIMessage(content=content))
        else:
            chat_history = []
                
        class ReasoningQuestions(BaseModel):
            general_summary: str = Field(description="Summary of relevant information found in chat history.")
            private_summary: str = Field(description="All private information from chat history.")
        
        temp_prompt = ( "You are an AI assitant being obeserved for your efficiency and performance, analyze the chat historyt and create a detailed summary of relevant information;"
        "Be sure to keep all private and personal information only in the private summary." )
        run_model_w_struct = run_model.with_structured_output(ReasoningQuestions)
        user_prompt = ChatPromptTemplate.from_messages([("system", "{system_context}"), MessagesPlaceholder(variable_name="chat_history"), ("human", "{promt_message}"),])
        chain = user_prompt | run_model_w_struct
        summaries_list = chain.invoke({"promt_message": temp_prompt, "system_context": summary_personality, "chat_history":chat_history})

        try:
            new_chat_summary = model_chats_summary( 
                                      model_chat= model_chats.objects.get(id=model_chat_id),
                                      chat_summary = summaries_list.general_summary)
            new_chat_summary.save()

            new_private_summary = chat_message_private_summary( 
                                      model_chat= model_chats.objects.get(id=model_chat_id),
                                      chat_private_summary = summaries_list.private_summary)
            new_private_summary.save()

        except:
            temp_mod_sum = model_chats_summary.objects.filter(model_chat= model_chats.objects.get(id=model_chat_id)).update(chat_summary=summaries_list.general_summary)
            temp_mod_sum_priv =chat_message_private_summary.objects.filter(model_chat= model_chats.objects.get(id=model_chat_id)).update(chat_private_summary=summaries_list.private_summary)
 
        checked_chat_history_check = pd.DataFrame()
        checked_chat_history_check['chat_message'] = [chat_messages.objects.get(id=x) for x in checked_chat_history['id']]
        checked_chat_history_check['date_summairzed'] = timezone.now()
        checked_chat_history_check['chat_summarized'] = True

        instances = [chat_message_summarized(**row) for row in checked_chat_history_check.to_dict('records')]
        chat_message_summarized.objects.bulk_create(instances)


class create_model_connection(View):
    def get(self, request):
        if check_authentication(request) != None:
            return check_authentication(request)

        model_connection_form = create_model_connection_form(request.GET or None)
        context = {'model_connection_form':model_connection_form}
        return render(request, 'bots/create_model_connection.html', context)
    
    def post(self, request):
        if check_authentication(request) != None:
            return check_authentication(request)
        
        model_connection_form = create_model_connection_form(data=request.POST or None)

        if model_connection_form.is_valid():
            new_model_connection = model_connection_form.save(commit=False)
            new_model_connection.created_date = timezone.now()
            new_model_connection.save()
            context = {'new_model_connection':new_model_connection}
            messages.success(request, 'model created')
            return redirect('/bots/new_model/')
            

        model_connection_form = create_model_connection_form(request.GET or None)
        context = {'model_connection_form':model_connection_form}
        return render(request, 'bots/create_model_connection.html', context)
    
    def get_api(request):
        if check_authentication(request) != None:
            return check_authentication(request)
        
        model_connection_form = create_model_connection_form()
        model_connection_form = form_to_json_schema(model_connection_form)
        json_form = {'message':'This form is used to create a new model connection, you will find the relevant item(s) below. Please make sure your response follows the format provided below.',
                     'items':[
                         {'name': 'Model Connection Creation Form', 
                          'description':'This form is used to create model connections. All fields must be filled for the form to be submitted.', 
                          'form':model_connection_form,
                          'format':{'Model Connection Creation Form': {
                        'model_connection_name':'a unique name for project',
                        'model_name':'name of model to be used',
                        'model_base':'model base/url',
                        'model_api_key':'your unique for the api connection, leave field blank for local models',
                        'input_cost':'cost per input token, leave 0.00 for local and free models',
                        'output_cost':'cost per output token, leave as 0.00 for local and free models',
                        
                        }}},
                     ]}
        return JsonResponse(json_form)
    
    @csrf_exempt
    def post_api(request):
        if check_authentication(request) != None:
            return check_authentication(request)

        data = json.loads(request.body.decode('utf-8'))
        new_model_connection_data = data['Model Connection Creation Form']
        if all(key in new_model_connection_data for key in ['model_connection_name', 'model_name', 'model_base', 'model_api_key', 'input_cost', 'output_cost',]):
            model_connection_form = create_model_connection_form(new_model_connection_data)
            
            if model_connection_form.is_valid():
                new_model_connection = model_connection_form.save(commit=False)
                new_model_connection.created_date = timezone.now()
                new_model_connection.save()
                context = {'new_model_connection':new_model_connection}
                data = {'message':'new model connection has been created.'}
                return JsonResponse(data)
            else:
                context = {'errors':model_connection_form.errors}
                print(model_connection_form.errors)
        
        print('model connection not created')
        data = {'message':'An error has occured, to create a model connection, please ensure your request follows the format below.',
                    'format':{'Model Connection Creation Form': {
                        'model_connection_name':'a unique name for project',
                        'model_name':'name of model to be used',
                        'model_base':'model base/url',
                        'model_api_key':'your unique for the api connection, leave field blank for local models',
                        'input_cost':'cost per input token, leave 0.00 for local and free models',
                        'output_cost':'cost per output token, leave as 0.00 for local and free models',
                        
                        }}}
        return JsonResponse(data)
    
    @csrf_exempt
    def delete_model_connection(request, model_connection_id):
        if check_authentication(request) != None:
            return check_authentication(request)
        
        if model_connection.objects.filter(id=model_connection_id).exists():
            model_connection_to_delete = model_connection.objects.get(id=model_connection_id)
            model_connection_to_delete.delete()
            
        messages.success(request, 'model deleted')
        return redirect('/bots/new_model/')

class create_model_chats(View):
    def get(self, request):
        if check_authentication(request) != None:
            return check_authentication(request)

        model_chats_form = create_model_chats_form(request.GET or None)
        context = {'model_chats_form':model_chats_form}
        return render(request, 'bots/create_model_chat.html', context)
    
    def post(self, request):
        if check_authentication(request) != None:
            return check_authentication(request)
        
        model_chats_form = create_model_chats_form(data=request.POST or None)

        if model_chats_form.is_valid():
            new_model_chat = model_chats_form.save(commit=False)
            new_model_chat.created_date = timezone.now()
            new_model_chat.save()
            context = {'new_model_chat':new_model_chat}
            messages.success(request, 'model chat created')
            return redirect('/bots/new_model_chat/')
            

        model_chats_form = create_model_chats_form(request.GET or None)
        context = {'model_chats_form':model_chats_form}
        return render(request, 'bots/create_model_chat.html', context)
    
    def get_api(request):
        if check_authentication(request) != None:
            return check_authentication(request)
        
        model_chats_form = create_model_chats_form()
        model_chats_form = form_to_json_schema(model_chats_form)
        json_form = {'message':'This form is used to create new model chats, you will find the relevant item(s) below. Please make sure your response follows the format provided below.',
                     'items':[
                         {'name': 'Model Chats Creation Form', 
                          'description':'This form is used to create model chats. All fields must be filled for the form to be submitted.', 
                          'form':model_chats_form,
                          'format':{'Model Chats Creation Form': {
                        'model_connection_name':'id of connection model to use',
                        'chat_user':'id of chat user',
                        'chat_type':'type of chat; pick from list',
                        }}},
                     ]}
        return JsonResponse(json_form)
    
    @csrf_exempt
    def post_api(request):
        if check_authentication(request) != None:
            return check_authentication(request)

        data = json.loads(request.body.decode('utf-8'))
        new_model_chats_data = data['Model Chats Creation Form']
        if all(key in new_model_chats_data for key in ['model_connection_name', 'chat_user', 'chat_type',]):
            model_chats_form = create_model_chats_form(new_model_chats_data)
            
            if model_chats_form.is_valid():
                new_model_chats = model_chats_form.save(commit=False)
                new_model_chats.created_date = timezone.now()
                new_model_chats.save()
                context = {'new_model_chats':new_model_chats}
                data = {'message':'new model chat has been created.'}
                return JsonResponse(data)
            else:
                context = {'errors':model_chats_form.errors}
                print(model_chats_form.errors)
        
        print('model chat not created')
        data = {'message':'An error has occured, to create a model chat, please ensure your request follows the format below.',
                    'format':{'Model Chats Creation Form': {
                        'model_connection_name':'id of connection model to use',
                        'chat_user':'id of chat user',
                        'chat_type':'type of chat; pick from list',
                        }}}
        return JsonResponse(data)
    
    @csrf_exempt
    def delete_model_chats(request, model_chats_id):
        if check_authentication(request) != None:
            return check_authentication(request)
        
        if model_chats.objects.filter(id=model_chats_id).exists():
            model_chats_to_delete = model_chats.objects.get(id=model_chats_id)
            model_chats_to_delete.delete()
            
        messages.success(request, 'model deleted')
        return redirect('/bots/new_model_chat/')

class create_model_personality(View):
    def get(self, request):
        if check_authentication(request) != None:
            return check_authentication(request)

        model_personality_form = create_model_personality_form(request.GET or None)
        context = {'model_personality_form':model_personality_form}
        return render(request, 'bots/create_model_personality.html', context)
    
    def post(self, request):
        if check_authentication(request) != None:
            return check_authentication(request)
        
        model_personality_form = create_model_personality_form(data=request.POST or None)

        if model_personality_form.is_valid():
            new_model_personlaity = model_personality_form.save(commit=False)
            new_model_personlaity.created_date = timezone.now()
            new_model_personlaity.save()
            context = {'new_model_personlaity':new_model_personlaity}
            messages.success(request, 'model personality created')
            return redirect('/bots/new_model_personality/')
            

        model_personality_form = create_model_personality_form(request.GET or None)
        context = {'model_personality_form':model_personality_form}
        return render(request, 'bots/create_model_personality.html', context)
    
    def get_api(request):
        if check_authentication(request) != None:
            return check_authentication(request)
        
        model_personality_form = create_model_personality_form()
        model_personality_form = form_to_json_schema(model_personality_form)
        json_form = {'message':'This form is used to create new model chats, you will find the relevant item(s) below. Please make sure your response follows the format provided below.',
                     'items':[
                         {'name': 'Model Personality Creation Form', 
                          'description':'This form is used to create model personalities. All fields must be filled for the form to be submitted.', 
                          'form':model_personality_form,
                          'format':{'Model Chats Creation Form': {
                        'personality_name':'unique name for personality',
                        'personality_description':'detailed version of what your agents personality is',
                        'personality_type':'type of personalities; pick from list',
                        }}},
                     ]}
        return JsonResponse(json_form)
    
    @csrf_exempt
    def post_api(request):
        if check_authentication(request) != None:
            return check_authentication(request)

        data = json.loads(request.body.decode('utf-8'))
        new_model_personalities_data = data['Model Personality Creation Form']
        if all(key in new_model_personalities_data for key in ['personality_name', 'personality_description', 'personality_type',]):
            model_personality_form = create_model_personality_form(new_model_personalities_data)
            
            if model_personality_form.is_valid():
                new_model_personlaity = model_personality_form.save(commit=False)
                new_model_personlaity.created_date = timezone.now()
                new_model_personlaity.save()
                context = {'new_model_personlaity':new_model_personlaity}
                data = {'message':'new model personality has been created.'}
                return JsonResponse(data)
            else:
                context = {'errors':model_personality_form.errors}
                print(model_personality_form.errors)
        
        print('model personality not created')
        data = {'message':'An error has occured, to create a model personality, please ensure your request follows the format below.',
                    'format':{'Model Chats Creation Form': {
                        'personality_name':'unique name for personality',
                        'personality_description':'detailed version of what your agents personality is',
                        'personality_type':'type of personalities; pick from list',
                        }}}
        return JsonResponse(data)
    
    @csrf_exempt
    def delete_model_personality(request, model_personality_id):
        if check_authentication(request) != None:
            return check_authentication(request)
        
        if model_personality.objects.filter(id=model_personality_id).exists():
            model_personality_to_delete = model_personality.objects.get(id=model_personality_id)
            model_personality_to_delete.delete()
            
        messages.success(request, 'personality deleted')
        return redirect('/bots/new_model_personality/')

class initiate_models(View):
    def get(self, request):
        if check_authentication(request) != None:
            return check_authentication(request)
        
        models_to_initiate = pd.DataFrame(model_intiate.objects.all().values())

        context = {'models_to_initiate':models_to_initiate.to_dict('records')}
        return render(request, 'bots/initiate_model.html', context)
    
    def post(self, request):
        if check_authentication(request) != None:
            return check_authentication(request)
        context = {}
        
        if model_intiate.objects.filter(id=request.POST['models_to_initiate']).exists:
            if request.POST['start_stop'] == "start":
                command_response = call_command('testin_initiate', 1)
                context['message'] = command_response
            elif request.POST['start_stop'] == "stop":
                subprocess.Popen(["pkill", "-f", "llama-server"]) 

        models_to_initiate = pd.DataFrame(model_intiate.objects.all().values())
        context['models_to_initiate'] = models_to_initiate.to_dict('records')        
        return render(request, 'bots/initiate_model.html', context)

class view_edit_summary(View):
    def get(self, request, models_chat_id):
        if check_authentication(request) != None:
            return check_authentication(request)
        
        if model_chats.objects.filter(id=models_chat_id).exists():
            model_chats_to_see = model_chats.objects.get(id=models_chat_id)
            if model_chats_summary.objects.filter(model_chat=model_chats_to_see):
                chat_summary = model_chats_summary.objects.get(model_chat=model_chats_to_see)
                chat_summary_str = chat_summary.chat_summary
                chat_summary_str = markdown.markdown(chat_summary_str)
        
        else:
            redirect(f'/bots/model_chat_messages/{models_chat_id}')

        context = {'chat_summary':chat_summary_str}
        return render(request, 'bots/summary_view.html', context)
    
    def post(self, request, models_chat_id):
        if check_authentication(request) != None:
            return check_authentication(request)
        context = {}
        form_initial = {}
        
        if model_chats.objects.filter(id=models_chat_id).exists():
            model_chats_to_see = model_chats.objects.get(id=models_chat_id)
            form_initial['model_chat'] = model_chats_to_see

            if model_chats_summary.objects.filter(model_chat=model_chats_to_see):
                chat_summary = model_chats_summary.objects.get(model_chat=model_chats_to_see)
                chat_summary_str = chat_summary.chat_summary
                form_initial['chat_summary'] = chat_summary_str

                user_summary_form = create_model_summary(data=request.POST or None)

                if user_summary_form.is_valid():
                    new_chat_summary = user_summary_form.save(commit=False)
                    chat_summary_val = model_chats_summary.objects.filter(model_chat=model_chats_to_see)
                    chat_summary_val.update(chat_summary=new_chat_summary.chat_summary)
                
                    return redirect('chat_summary_view', models_chat_id=models_chat_id)

            else:
                return redirect(f'/bots/model_chat_messages/{models_chat_id}')
        
        else:
            return redirect(f'/bots/model_chat_messages/')

        chat_summary_form = create_model_summary(initial=form_initial)
        context['summary_form'] = chat_summary_form
        return render(request, 'bots/summary_view.html', context)

class view_edit_private_summary(View):
    def get(self, request, models_chat_id):
        if check_authentication(request) != None:
            return check_authentication(request)
        
        if model_chats.objects.filter(id=models_chat_id).exists():
            model_chats_to_see = model_chats.objects.get(id=models_chat_id)
            if chat_message_private_summary.objects.filter(model_chat=model_chats_to_see):
                chat_summary = chat_message_private_summary.objects.get(model_chat=model_chats_to_see)
                chat_summary_str = chat_summary.chat_private_summary
                chat_summary_str = markdown.markdown(chat_summary_str)
        
        else:
            redirect(f'/bots/model_chat_messages/{models_chat_id}')

        context = {'chat_summary':chat_summary_str}
        return render(request, 'bots/summary_view.html', context)
    
    def post(self, request, models_chat_id):
        if check_authentication(request) != None:
            return check_authentication(request)
        context = {}
        form_initial = {}
        
        if model_chats.objects.filter(id=models_chat_id).exists():
            model_chats_to_see = model_chats.objects.get(id=models_chat_id)
            form_initial['model_chat'] = model_chats_to_see

            if chat_message_private_summary.objects.filter(model_chat=model_chats_to_see):
                chat_summary = chat_message_private_summary.objects.get(model_chat=model_chats_to_see)
                chat_summary_str = chat_summary.chat_private_summary
                form_initial['chat_private_summary'] = chat_summary_str

                user_summary_form = create_model_private_summary(data=request.POST or None)

                if user_summary_form.is_valid():
                    new_chat_summary = user_summary_form.save(commit=False)
                    chat_summary_val = chat_message_private_summary.objects.filter(model_chat=model_chats_to_see)
                    chat_summary_val.update(chat_private_summary=new_chat_summary.chat_private_summary)
                
                    return redirect('chat_private_summary_view', models_chat_id=models_chat_id)

            else:
                return redirect(f'/bots/model_chat_messages/{models_chat_id}')
        
        else:
            return redirect(f'/bots/model_chat_messages/')

        chat_summary_form = create_model_private_summary(initial=form_initial)
        context['summary_form'] = chat_summary_form
        return render(request, 'bots/summary_view.html', context)

class manage_model_messages(View):
    def get(self, request, model_chats_id):
        if check_authentication(request) != None:
            return check_authentication(request)
        context = {}
        
        if model_chats.objects.filter(chat_user=request.user).exists():
            model_chats_list = pd.DataFrame(model_chats.objects.filter(chat_user=request.user).values())
            model_connections = pd.DataFrame()
            for i_model_chat, e_model_chat in enumerate(model_chats_list['model_connection_name_id'].unique()):
                temp_connection = pd.DataFrame(model_connection.objects.filter(id=e_model_chat).values())
                model_connections = pd.concat([temp_connection, model_connections], axis=0)
            model_chats_list = pd.merge(model_chats_list, model_connections, left_on='model_connection_name_id', right_on='id', how='left')
            context['model_chats_list'] = model_chats_list.to_dict('records')
        else:
            messages.success(request, 'user does not have any model chats')
            return redirect('/bots/new_model_chat/')
        
        if chat_messages.objects.filter(message_model_chats_id=model_chats_id).exists():
            chat_messages_list = chat_messages.objects.filter(message_model_chats_id=model_chats_id).values()            
            chat_messages_list_df = pd.DataFrame(chat_messages_list)
            chat_messages_list_df['chat_message'] = chat_messages_list_df['chat_message'].apply(markdown.markdown)

            context['chat_messages_list'] = chat_messages_list_df.to_dict('records')
        
        personalities_list = pd.DataFrame(model_personality.objects.all().values())
        context['personalities'] = personalities_list.to_dict('records')

        model_agent_list = pd.DataFrame(model_connection.objects.all().values())
        context['model_agent'] = model_agent_list.to_dict('records')

        chat_messages_form = create_chat_messages_form(request.GET or None)
        context['chat_messages_form'] = chat_messages_form
        context['tools'] = {"fast":{"icon":'<i class="bi bi-fast-forward-btn"></i>', "value":"fast"}, 
                            "thinking":{"icon":'<i class="bi bi-cpu"></i>', "value":"thinking"}, 
                            "websearch":{"icon":'<i class="bi bi-search"></i>', "value":"websearch"},
                            "local files":{"icon":'<i class="bi bi-file-arrow-down"></i>', "value":"local_files"}}
        context['model_chats_id'] = model_chats_id
        return render(request, 'bots/manage_model_chats.html', context)
    
    def post(self, request, model_chats_id):
        if check_authentication(request) != None:
            return check_authentication(request)
        context = {}
        if model_chats.objects.filter(chat_user=request.user).exists():
            model_chats_list = pd.DataFrame(model_chats.objects.filter(chat_user=request.user).values())
            if model_chats_id in model_chats_list['id'].astype(str).to_list():
                model_chats_connection_id = model_chats_list[model_chats_list['id'].astype(str)==model_chats_id]['model_connection_name_id'][:]
                if model_connection.objects.filter(id=request.POST['model_agent']).exists():
                    run_model_connection = model_connection.objects.get(id=request.POST['model_agent'])
                else:
                    run_model_connection = model_connection.objects.get(id=model_chats_connection_id)

                if model_personality.objects.filter(id=request.POST['personalities']).exists():
                    chat_personality = model_personality.objects.filter(id=request.POST['personalities']).values()
                else:
                    chat_personality = ""
                                
                chat_messages_form = create_chat_messages_form(data=request.POST or None)
                user_message = None

                if chat_messages_form.is_valid():
                    new_chat_messages = chat_messages_form.save(commit=False)
                    user_message = new_chat_messages.chat_message
                    new_chat_messages.created_date = timezone.now()
                    new_chat_messages.message_model_chats = model_chats.objects.get(id=model_chats_id)
                    new_chat_messages.chat_sender = 'user'
                    new_chat_messages.chat_meta = ''
                    new_chat_messages.save()
                
                chat_history = []

#### check if there is chat hitory only embed in chat history not in summary, feed summary as context

                if chat_messages.objects.filter(message_model_chats_id=model_chats_id).exists():
                    chat_history = pd.DataFrame(chat_messages.objects.filter(message_model_chats_id=model_chats_id).values())
                    check_chat_history = pd.DataFrame(chat_message_summarized.objects.filter(chat_message_id__in=chat_history['id'].to_list()).values())
                    if check_chat_history.empty:
                        checked_chat_history = chat_history                   
                    else:
                        check_chat_history = check_chat_history[check_chat_history['chat_summarized']==True]
                        checked_chat_history = chat_history[~chat_history['id'].isin(check_chat_history['chat_message_id'])]
                    
                    if model_chats_summary.objects.filter(model_chat_id=model_chats_id).exists():
                        chat_summary_obj = model_chats_summary.objects.filter(model_chat_id=model_chats_id).values()
                    else:
                        chat_summary_obj = ""
                                
                run_model_reponse = send_message_to_model(user_message,
                            user_request=request,
                            chat_summary=chat_summary_obj,
                            personality=chat_personality,
                            chat_tool=request.POST['tools'],
                            model_base=run_model_connection.model_base,
                            model_name=run_model_connection.model_name, 
                            model_api_key=run_model_connection.model_api_key,
                            chat_history_list=checked_chat_history,)
                model_message_response = chat_messages.objects.create(
                    date_created = timezone.now(),
                    message_model_chats = model_chats.objects.get(id=model_chats_id),
                    chat_sender = 'model',
                    chat_meta = run_model_reponse.response_metadata,
                    chat_message = run_model_reponse.content,)

        if model_chats.objects.filter(chat_user=request.user).exists():
            model_chats_list = pd.DataFrame(model_chats.objects.filter(chat_user=request.user).values())
            model_connections = pd.DataFrame()
            for i_model_chat, e_model_chat in enumerate(model_chats_list['model_connection_name_id'].unique()):
                temp_connection = pd.DataFrame(model_connection.objects.filter(id=e_model_chat).values())
                model_connections = pd.concat([temp_connection, model_connections], axis=0)
            model_chats_list = pd.merge(model_chats_list, model_connections, left_on='model_connection_name_id', right_on='id', how='left')
            context['model_chats_list'] = model_chats_list.to_dict('records')
        else:
            messages.success(request, 'user does not have any model chats')
            return redirect('/bots/new_model_chat/')
        
        if chat_messages.objects.filter(message_model_chats_id=model_chats_id).exists():
            chat_messages_list = chat_messages.objects.filter(message_model_chats_id=model_chats_id).values()            
            chat_messages_list_df = pd.DataFrame(chat_messages_list)
            chat_messages_list_df['chat_message'] = chat_messages_list_df['chat_message'].apply(markdown.markdown)

            context['chat_messages_list'] = chat_messages_list_df.to_dict('records')

        personalities_list = pd.DataFrame(model_personality.objects.all().values())
        context['personalities'] = personalities_list.to_dict('records')

        model_agent_list = pd.DataFrame(model_connection.objects.all().values())
        context['model_agent'] = model_agent_list.to_dict('records')

        chat_messages_form = create_chat_messages_form(request.GET or None)
        context['chat_messages_form'] = chat_messages_form
        context['tools'] = {"fast":{"icon":"", "value":"fast"}, 
                            "thinking":{"icon":"", "value":"thinking"}, 
                            "websearch":{"icon":"", "value":"websearch"},
                            "local files":{"icon":"", "value":"local_files"}}
        context['model_chats_id'] = model_chats_id
        return render(request, 'bots/manage_model_chats.html', context)
    
    def summarize_chat_button(request, model_chats_id):
        summarize_chat(model_chat_id=model_chats_id)
        return redirect(f'/bots/model_chat_messages/{model_chats_id}')
    
    def get_api(request, model_chats_id):
        if check_authentication(request) != None:
            return check_authentication(request)
        
        context = {}
        
        if model_chats.objects.filter(chat_user=request.user).exists():
            model_chats_list = pd.DataFrame(model_chats.objects.filter(chat_user=request.user).values())
            context['model_chats_list'] = model_chats_list.to_dict('records')
        else:
            messages.success(request, 'user does not have any model chats')
            return redirect('/bots/new_model_chat/')
        
        if chat_messages.objects.filter(message_model_chats_id=model_chats_id).exists():
            chat_messages_list = pd.DataFrame(chat_messages.objects.filter(message_model_chats_id=model_chats_id).values())
            context['chat_messages_list'] = chat_messages_list.to_dict('records')

        chat_messages_form = create_chat_messages_form()
        context['chat_messages_form'] = chat_messages_form
        json_form = {'message':'This form is used to send messages to models',
                     'items':[
                         {'name': 'Chat Message Form', 
                          'description':'This form is used to create projects. All fields must be filled for the form to be submitted.', 
                          'form':chat_messages_form,
                          'format':{'Chat Message Form': {'chat_message':'message to send to model',}},
                          'context': context,}]}

        return JsonResponse(json_form)
    
    @csrf_exempt
    def post_api(request, model_chats_id):
        if check_authentication(request) != None:
            return check_authentication(request)
        data = json.loads(request.body.decode('utf-8'))
        new_message = data['Chat Message Form']

        context = {}

        if model_chats.objects.filter(chat_user=request.user).exists():
            model_chats_list = pd.DataFrame(model_chats.objects.filter(chat_user=request.user).values())
            if model_chats_id in model_chats_list['id'].astype(str).to_list():
                model_chats_connection_id = model_chats_list[model_chats_list['id'].astype(str)==model_chats_id]['model_connection_name_id'][:]
                run_model_connection = model_connection.objects.get(id=model_chats_connection_id)

                if all(key in new_message for key in ['chat_message',]):
                    chat_messages_form = create_chat_messages_form(new_message)
                
                    user_message = None

                    if chat_messages_form.is_valid():
                        new_chat_messages = chat_messages_form.save(commit=False)
                        user_message = new_chat_messages.chat_message
                        new_chat_messages.created_date = timezone.now()
                        new_chat_messages.message_model_chats = model_chats.objects.get(id=model_chats_id)
                        new_chat_messages.chat_sender = 'user'
                        new_chat_messages.chat_meta = ''
                        new_chat_messages.save()
                    
                    chat_history = []
                    if chat_messages.objects.filter(message_model_chats_id=model_chats_id).exists():
                        chat_history = pd.DataFrame(chat_messages.objects.filter(message_model_chats_id=model_chats_id).values())
                    
                    run_model_reponse = send_message_to_model(user_message, 
                            model_base=run_model_connection.model_base,
                            model_name=run_model_connection.model_name, 
                            model_api_key=run_model_connection.model_api_key,
                            chat_history_list=chat_history,)
                    
                    model_message_response = chat_messages.objects.create(
                        date_created = timezone.now(),
                        message_model_chats = model_chats.objects.get(id=model_chats_id),
                        chat_sender = 'model',
                        chat_meta = run_model_reponse.usage_metadata,
                        chat_message = run_model_reponse,)
                    
                    data = {'model_response':str(run_model_reponse)}
                    return JsonResponse(data)
                
                else:
                    data = {'message':'An error has occured, to send a message to a model, please ensure your request follows the format below.',
                    'format':{'Chat Message Form': {'chat_message':'message to send to model',}}}
                    return JsonResponse(data)
    



'''
        if model_chats.objects.filter(chat_user=request.user).exists():
            model_chats_list = pd.DataFrame(model_chats.objects.filter(chat_user=request.user).values())
            if model_chats_id in model_chats_list['id'].astype(str).to_list():
                model_chats_connection_id = model_chats_list[model_chats_list['id'].astype(str)==model_chats_id]['model_connection_name_id'][:]
                run_model_connection = model_connection.objects.get(id=model_chats_connection_id)
                chat_messages_form = create_chat_messages_form(data=request.POST or None)
                user_message = None

                if chat_messages_form.is_valid():
                    new_chat_messages = chat_messages_form.save(commit=False)
                    user_message = new_chat_messages.chat_message
                    new_chat_messages.created_date = timezone.now()
                    new_chat_messages.message_model_chats = model_chats.objects.get(id=model_chats_id)
                    new_chat_messages.chat_sender = 'user'
                    new_chat_messages.chat_meta = ''
                    new_chat_messages.save()
                
                chat_history = []
                if chat_messages.objects.filter(message_model_chats_id=model_chats_id).exists():
                    chat_history = pd.DataFrame(chat_messages.objects.filter(message_model_chats_id=model_chats_id).values())
                
#### check response info to handle different messages and add personality

                run_model_reponse = send_message_to_model(user_message, 
                          model_base=run_model_connection.model_base,
                          model_name=run_model_connection.model_name, 
                          model_api_key=run_model_connection.model_api_key,
                          chat_history_list=chat_history,)
                
                model_message_response = chat_messages.objects.create(
                    date_created = timezone.now(),
                    message_model_chats = model_chats.objects.get(id=model_chats_id),
                    chat_sender = 'model',
                    chat_meta = run_model_reponse.usage_metadata,
                    chat_message = run_model_reponse,)
        
            model_chats_list = pd.DataFrame(model_chats.objects.filter(chat_user=request.user).values())
            model_connections = pd.DataFrame()
            for i_model_chat, e_model_chat in enumerate(model_chats_list['model_connection_name_id'].unique()):
                temp_connection = pd.DataFrame(model_connection.objects.filter(id=e_model_chat).values())
                model_connections = pd.concat([temp_connection, model_connections], axis=0)
            model_chats_list = pd.merge(model_chats_list, model_connections, left_on='model_connection_name_id', right_on='id', how='left')
            context['model_chats_list'] = model_chats_list.to_dict('records')
        else:
            messages.success(request, 'user does not have any model chats')
            return redirect('/daemon/new_model_chat/')



        if chat_messages.objects.filter(message_model_chats_id=model_chats_id).exists():
            chat_messages_list = pd.DataFrame(chat_messages.objects.filter(message_model_chats_id=model_chats_id).values())
            context['chat_messages_list'] = chat_messages_list.to_dict('records')
        
        chat_messages_form = create_chat_messages_form(request.GET or None)
        context['tools'] = {"fast", "thinking", "websearch", "local files"}
        context['personalities'] = {'agent', 'master'}
        context['chat_messages_form'] = chat_messages_form
        context['model_chats_id'] = int(model_chats_id)
        return render(request, 'bots/manage_model_chats.html', context)'''