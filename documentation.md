# **Daemon: Technical Documentation**
*Django Framework for Large Language Model Integration and Chat-Based AI Interactions*
---
## **1. Project Overview**
Daemon is an Open Source **Django-based framework** designed to seamlessly integrate **Large Language Models (LLMs)** such as Llama.cpp and VLLM into Django applications. It provides tools for managing LLM connections, tracking chat sessions, logging messages, and generating AI-driven summaries—all while ensuring scalability, security, and maintainability.
The system is built with **modularity** in mind, allowing developers to extend functionality for custom use cases such as AI-driven project management, customer support automation, or internal knowledge assistants.
---
## **2. Core Features**
### **2.1 Model Management**
- **LLM Connection Management**:
  - Store and manage API keys, pricing, and server configurations for various LLMs (e.g., Mistral, Llama).  
  - Supports multiple server types (`llama.cpp`, `vllm`) for flexible deployment.
- **Dynamic Model Instantiation**:
  - Instantiate models with configurable settings (e.g., temperature, top-p, personality).
- **Personality Customization**:
  - Define AI behavior profiles (e.g., planning, summarization) to tailor responses.

### **2.2 Chat & Interaction**
- **End-to-End Chat Sessions**:
  - Track conversations, user roles, and message metadata.
- **Message Logging**:
  - Log all interactions with timestamps, context, and sender metadata.
- **Summarization & Private Notes**:
  - Generate AI-driven summaries for chat sessions.
  - Store private AI notes for sensitive or internal use.
### **2.3 Security & Access Control**
- **Authentication**:
  - Built-in Django authentication with role-based access control (RBAC).  
  - Supports user roles such as `admin`, `support`, and `user`.
- **Data Protection**:
  - Encryption for sensitive data (e.g., API keys, private summaries).  
  - Secure handling of user inputs and model outputs.

### **2.4 Scalability & Performance**
- **Optimized Queries**:
  - Uses Django’s ORM with `select_related` and `prefetch_related` to avoid N+1 query issues.
- **Asynchronous Task Processing**:
  - Celery for background tasks (e.g., summarization, file processing).
- **Caching**:
  - Redis for caching frequently accessed data (e.g., chat history, model responses).
---
## **3. Technical Architecture**
### **3.1 High-Level Architecture**

Daemon follows a **Model-View-Form (MVF)** architecture, with a focus on modularity and scalability:

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │             │    │             │    │             │    │             │     │
│  │  models.py  │───▶│  forms.py   │───▶│  views.py   │───▶│  templates  │     │
│  │             │    │             │    │             │    │             │     │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                         │  │
│  │┌─────────────┐    ┌─────────────┐    ┌───────────────────────────────┐  │  │  
│  ││             │    │             │    │                               │  │  │  
│  ││  Database   │◀───┤  LangChain  │    │  Celery + Redis (Async Tasks) │  │  │  
│  ││  (Postgres) │    │  (LLM API)  │    │                               │  │  │  
│  ││             │    │             │    └───────────────────────────────┘  │  │  
│  │└─────────────┘    └─────────────┘                                       │  │  
│  │                                                                         │  │  
│  └─────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
```

### **3.2 Key Components**
#### **A. Database Models (`models.py`)**
- **`model_connection`**: Stores LLM API keys, pricing, and connection details.
- **`model_intiate`**: Manages model instances (e.g., `server_type`, `path_to_build`).
- **`model_chats`**: Tracks chat sessions with metadata (e.g., `chat_type`, `chat_user`).
- **`chat_messages`**: Logs individual messages with sender metadata.
- **`model_chats_summary`**: Stores AI-generated summaries of chat sessions.
- **`chat_message_private_summary`**: Stores private AI notes.
- **`message_attachment`**: Handles file attachments (e.g., PDFs, images).

#### **B. Forms (`forms.py`)**
- **Dynamic Forms**: Uses Django’s `ModelForm` to create and validate user inputs.
- **ModelChoiceField**: Dynamically populates dropdowns (e.g., for selecting `model_connection`).
- **Excluded Fields**: Forms exclude non-essential fields (e.g., `date_created`) to simplify data entry.

#### **C. Views (`views.py`)**
- **Core Logic**: Handles HTTP requests (GET/POST) and interacts with models and forms.
- **Authentication**: Uses `check_authentication` to protect routes.
- **Message Processing**: Sends user messages to LLMs via `send_message_to_model` (LangChain integration).
- **Summarization**: Generates AI-driven summaries using `summarize_chat`.
#### **D. External Dependencies**
- **LangChain**: For interacting with LLMs (e.g., Llama.cpp, VLLM).
- **Celery + Redis**: For asynchronous task processing (e.g., summarization, file handling).
- **Django ORM**: For database operations (PostgreSQL/MySQL).
- **Django Channels**: For real-time features (if applicable).
---
## **4. Unique Technical Specifications**
### **4.1 Dynamic Model Instantiation**
- **Purpose**: Allows users to instantiate LLMs with custom configurations.
- **Implementation**:
  - Users select a `model_connection` (e.g., API key for Llama.cpp).  
  - Users specify `server_type` (`llama.cpp` or `vllm`) and other settings.
- **Example**:  ```python  # In views.py:  models_to_initiate = pd.DataFrame(model_intiate.objects.all().values())  ```  → Fetches all model instances dynamically.

### **4.2 Message Processing with LangChain**
- **Purpose**: Enables AI-driven responses to user messages.
- **Implementation**:
  - User submits a message via `create_chat_messages_form`.  
  - The message is sent to the LLM via `send_message_to_model`.  
  - The LLM’s response is logged in `chat_messages`.
- **Example**:  ```python  # In views.py:  run_model_reponse = send_message_to_model(      user_message,      model_base=run_model_connection.model_base,      chat_history_list=chat_history,      chat_tool=request.POST["tools"],  )  ```

### **4.3 Summarization Workflow**
- **Purpose**: Generates AI-driven summaries of chat sessions.
- **Implementation**:
  - Summaries are stored in `model_chats_summary` (public) and `chat_message_private_summary` (private).  
  - Uses LangChain to generate summaries based on chat history.
- **Example**:  ```python  # In views.py:  summaries = chain.invoke(...)  # LangChain summarization  model_chats_summary.objects.filter(model_chat=model_chat_id).update(chat_summary=summaries.general_summary)  ```

### **4.4 File Attachment Handling**
- **Purpose**: Stores files (e.g., PDFs) alongside chat messages.
- **Implementation**:
  - Files are stored in `message_attachment` as base64-encoded data or raw file data.  
  - Future enhancements could include direct file uploads via forms.

### **4.5 Personality Customization**
- **Purpose**: Tailors AI behavior (e.g., planning, summarization).
- **Implementation**:
  - Users configure `model_personality` with settings like `personality_temp` and `personality_top_p`.  
  - These settings are passed to the LLM during message processing.

---
## **5. Security Considerations**
### **5.1 Authentication & Authorization**
- **Django’s Built-in Auth**: Protects routes with `@login_required` and role-based permissions.
- **Role-Based Access Control (RBAC)**:
  - `admin`: Full access to model management and chat sessions.  
  - `support`: Limited to chat sessions.  
  - `user`: Basic chat functionality.

### **5.2 Data Encryption**
- **API Keys**: Stored securely in `model_connection` (avoid plaintext storage).
- **Private Summaries**: Encrypted at rest for sensitive data.
### **5.3 Input Validation**
- **Forms**: Validate user inputs (e.g., `chat_message` length, `model_api_key` format).
- **Sanitization**: Prevents SQL injection and XSS attacks.
---
## **6. Performance Optimization**
### **6.1 Database Optimization**
- **Indexes**: Added for frequently queried fields (e.g., `model_connection_name`).
- **Query Optimization**: Uses `select_related` and `prefetch_related` to avoid N+1 queries.
### **6.2 Caching**- **Redis**: Caches frequently accessed data (e.g., chat history, model responses).
- **TTL Policies**: Set for cache invalidation (e.g., 30-minute TTL for chat summaries).

### **6.3 Asynchronous Processing**
- **Celery**: Handles background tasks (e.g., summarization, file processing).
- **Retry Logic**: Implements exponential backoff for failed tasks.---## **7. Deployment & Configuration**

### **7.1 Prerequisites**
- **Python**: 3.9+
- **Django**: 4.x+
- **Database**: PostgreSQL/MySQL
- **Redis**: For caching and Celery
- **LangChain**: For LLM interactions
- **Celery**: For async tasks

### **7.2 Setup Instructions**
1. **Clone the Repository**:   ```bash   git clone https://github.com/your-repo/llmassist.git   cd lmassist   ```
2. **Install Dependencies**:   ```bash   pip install -r requirements.txt   ```
3. **Configure Database**:   ```python   # settings.py   DATABASES = {       'default': {           'ENGINE': 'django.db.backends.postgresql',           'NAME': 'llm_db',           'USER': 'db_user',           'PASSWORD': 'db_password',           'HOST': 'localhost',       }   }   ```
4. **Run Migrations**:   ```bash   python manage.py migrate   ```
5. **Start the Development Server**:   ```bash   python manage.py runserver   ```
6. **Run Celery Worker**:   ```bash   celery -A lmassist worker --loglevel=info   ```
---

## **8. Example Workflow**

### **8.1 Adding a Model Connection**
1. User submits a `POST` request to `/bots/new_model_connection`.
2. Form validates inputs and saves to `model_connection`.
3. Database updates reflect the new connection.

### **8.2 Starting a Chat Session**
1. User selects a `model_connection` and a `chat_type` (e.g., `admin`).
2. Form saves to `model_chats` with metadata (e.g., `chat_user`).
3. Chat session is logged in `chat_messages`.

### **8.3 Sending a Message to an LLM**
1. User submits a message via `create_chat_messages_form`.
2. Message is sent to the LLM via `send_message_to_model`.
3. LLM’s response is logged in `chat_messages`.

### **8.4 Generating a Summary**

1. User requests a summary via `/bots/summary/{id}`.
2. LangChain generates a summary using chat history.
3. Summary is stored in `model_chats_summary`.

---

## **9. Technical Challenges & Solutions**

| **Challenge**                          | **Solution**                                                                 |
|----------------------------------------|-----------------------------------------------------------------------------|
| N+1 Query Issues                       | Use `select_related` and `prefetch_related` in ORM queries.                 |
| API Key Security                        | Store keys securely in environment variables or Django secrets.            |
| Summarization Latency                  | Use Celery for async summarization.                                         |
| File Attachment Handling                | Store files as base64-encoded data or use cloud storage (e.g., AWS S3).    |
| Scalability                             | Deploy with Kubernetes for horizontal scaling.                              |
| Real-Time Updates                       | Use Django Channels for WebSocket-based chat updates.                      |

---
## **10. Future Enhancements**
1. **File Upload Support**: Extend `create_chat_messages_form` to include direct file uploads.
2. **Incremental Summarization**: Update summaries dynamically as new messages are added.
3. **Rate Limiting**: Add API rate limiting for `send_message_to_model`.
4. **Multi-Tenancy**: Support for shared database with tenant isolation.
5. **Webhook Integration**: Enable real-time updates via webhooks.
---
## **11. API Reference**

### **11.1 Endpoints**

| **Endpoint**                     | **Method** | **Description**                                      |
|----------------------------------|------------|------------------------------------------------------|
| `/bots/new_model_connection`     | POST       | Add a new LLM connection.                            |
| `/bots/new_chat`                 | POST       | Start a new chat session.                            |
| `/bots/chat/{id}`                | GET/POST   | Fetch or send messages to a chat session.            |
| `/bots/summary/{id}`             | POST       | Generate a summary for a chat session.               |
| `/bots/personality`              | GET/POST   | Configure AI personalities.                          |

### **11.2 Example Request**
```json# POST /bots/send_message{  "model_connection_name": "mistral-7b",  "chat_message": "What can I do today?"}```

---
## **12. Conclusion**

Daemon is an Open Source **modular, scalable, and secure** framework for integrating LLMs into Django applications. Its focus on **dynamic model management, chat sessions, and AI-driven summarization** makes it ideal for use cases such as AI assistants, customer support automation, and internal knowledge tools.By following this documentation, developers can **deploy, extend, and maintain** the system effectively while ensuring **performance, security, and scalability**.---**Need further clarification?** Visit the [GitHub Repository](https://github.com/your-repo) or contact the support team.