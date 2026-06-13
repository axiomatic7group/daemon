# **🔥 Daemon: Your Private AI Chat Companion**
### *Part of the **Axiom Suite** – The Governance, Semantic, Action & Reasoning Layer for Digital Labor*

![Daemon](https://img.shields.io/badge/Daemon-Project%20Management-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Django](https://img.shields.io/badge/Django-4.2%2B-green)


![Daemon is a privacy-first reasoning engine designed for executives and professionals that refuse to trade their private information for innovation](https://github.com/axiomatic7group/daemon/raw/main/assets/deamon_img_doodle.png)

---

## **What is Daemon?**
**Daemon** is a **secure, private AI chat assistant** designed to act as your **"second brain"**—organizing, reasoning, and executing tasks while maintaining **organizational memory** and **strict privacy controls**. Built as part of the **Axiom Suite**, Daemon integrates seamlessly with your workflows, ensuring AI interactions are **auditable, secure, and efficient**.

🔹 **Why "Daemon"?**
In computing, a daemon is a background process that runs continuously—just like your AI assistant, always ready to help, **without overstepping bounds**.

---
## Key Features:

- **Multi-modal**: Use any model across any chat, change the model you use with every message you send;
  
- **Local-first**: Natively supports locally deployed AI models for privacy and data protection

- **Chat Personalities**: Create personalities for your agents with custom prompts, temperature and top_p settings to control your desired outputs

- **Background "Second-Brain"**: Organize all your chats, notes, brainstorms, and plans with backgorund agents that organize, manage, and maintain your thoughts and ideas in one place

- **Summaries and Private Information**: Automatically summarize chat history to minimize token context costs and to separate private information when using cloud-hosted models

- **Tools**: search the web, bring in local files, and more 


## **Technical Features**

### **Private & Secure**
- **No Data Leaks**: All conversations stay **local or private**—no external API calls unless explicitly allowed.

- **User-Level Attribution**: Every action is tied to a user’s security clearance (ABAC), preventing **"Shadow AI"** risks.

- **Fail-to-Human Escalation**: If Daemon hits an edge case, it **hands off to a human**—ensuring **0% hallucinations in critical paths**.

### **Smart Reasoning**
- **Context-Aware**: Remembers past interactions (organizational memory) to provide **consistent, intelligent responses**.
- **Task Automation**: Helps break down complex tasks into **actionable steps** (e.g., project planning, knowledge retrieval).
- **Personality Customization**: Adjust AI behavior (e.g., **planning mode** for project management, **summarization mode** for notes).

### **Seamless Integration**
- Works alongside **Synapse (Governance Layer)** and **Cadence (Action Layer)** for **end-to-end automation**.
- **Modular & Extensible**: Add new tools (e.g., file search, API calls) without rewriting logic.

### **Audit & Transparency**
- **Full Logs**: Every chat, action, and decision is **tracked and timestamped**.
- **No Black Boxes**: You see **exactly how Daemon works**—no hidden prompts or unpredictable behavior.

---

## **How It Works**
1. **Onboard Daemon** → Define Personalities or AI roles (e.g., project manager, knowledge assistant).

2. **Chat with Daemon** → Ask for help, brainstorm, create plans, or summarize your knowledge.

3. **Get Results** → Daemon executes **securely, efficiently, and transparently**.



---

## **Quick Start**
### **Installation**
```bash
git clone https://github.com/axiomatic7group/daemon.git
cd daemon
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### **Run with Docker (Recommended)**
```bash
docker-compose up --build
```

### **Configure Daemon**
- Set up **personality profiles** (e.g., `planning`, `summarization`).
- Define **security policies** (ABAC rules).
- Bonus: Integrate with **Synapse (Governance Layer)** for enterprise-grade permissions.

---
## **Why Choose Daemon?**

| **Feature**               | **Daemon** | **Traditional AI Chatbots** |
|---------------------------|------------|-----------------------------|
| **Privacy**               | ✅ Local/Private | ❌ Cloud-dependent |
| **Security**              | ✅ User-Level Attribution | ❌ "God Mode" risks |
| **Auditability**          | ✅ Full Logs | ❌ Black Boxes |
| **Fail-to-Human**         | ✅ Zero Hallucinations | ❌ Unpredictable |
| **Task Automation**       | ✅ Yes | ❌ Limited |

---
## **Explore the Axiom Suite**

![Daemon is a privacy-first reasoning engine designed for executives and professionals that refuse to trade their private information for innovation](https://github.com/axiomatic7group/daemon/raw/main/assets/daemon_img_hero.png)

Daemon is **one piece of the Axiom Suite**—a **complete framework for secure AI automation**:

🔹 **[Synapse](https://github.com/axiomatic7group/synapse)** → **Governance Layer** (User-Security Attribution)

🔹 **[Cadence](https://github.com/axiomatic7group/cadence)** → **Action Layer** (Task Orchestration)

🔹 **[Daemon](https://github.com/axiomatic7group/daemon)** → **Reasoning Layer** (Private AI Chat)

---
## **Join the Movement**
Daemon is **open-source**, but Axiom Suite is **proprietary**—designed for **enterprises** who need **scalable, secure AI automation**.

🔹 **Want more?**

**[Try Axiom Suite](https://axiomaticlab.com)**

**[Watch Our YouTube](https://www.youtube.com/channel/UCltGi4Su305oln_ldu-b94Q)**

**[Follow Us on LinkedIn](https://www.linkedin.com/company/axiomatic-lab/)**

---
## **License**
**Daemon** is licensed under **MIT** (Open Source).
**Axiom Suite** is proprietary; **contact us for enterprise solutions.**

---
**Ready to make AI work for you?**

**[Download Daemon](https://github.com/axiomatic7group/daemon)**

**[Explore Axiom Suite](https://axiomaticlab.com)**

------------------------------

# Axiomatic Lab

Mission: On-boarding AI that eliminates Operational Debt.

### 1. The Challenge: The "Black Box" Risk
Modern enterprises struggle with automation that is either too rigid or dangerously opaque. Standard AI implementations often lack granular security controls, creating a "clearance gap" where automated systems have more access than the employees they assist. Furthermore, when complex automated sequences fail, most systems require a total restart, leading to significant operational downtime.

### 2. The Solution: Task-Based AI Onboarding
Axiomatic Lab treats AI agents like professional hires rather than just software. We automate your business by **"onboarding"** your organizations tasks, notes, and AI chats, one at a time, alongside your staff all in one platform. Ensuring every automated action, note, and company information is collected, organized, and maintained to ensure your business operates efficiently and strategically.

**Background Knowledge Agents:** Automated background agents that will continously review all provided data from user workflows, notes, and AI chats, to relevant connected databases to create, maintain, and organize your companies operations. Automatically generating and updating Processes and Procedures, Company Guidelines, Client Notes, and much more.

**Security-Level Attribution:** Unlike generic AI, every task within our system is assigned a specific user-security level. This ensures that the AI only interacts with data and systems it is explicitly authorized to access, mimicking your internal organizational hierarchy.

**Dynamic Task Orchestration:** Our modular architecture allows for real-time auditability. Because we build processes task-by-task, our system is uniquely resilient:

-**Surgical Correction:** If an error occurs in step 5 of a 10-step process, you can correct just that specific task or adjust the subsequent steps.

-**Zero Restart Waste:** There is no need to restart the entire workflow from step 1. You save time, compute costs, and manual effort by fixing only what is broken.

### 3. Business Impact & Value
By choosing Axiomatic Lab, your organization gains:

-**Rapid Strategic Growth:** A sustainable platform that ensures your organization remains efficient and operationally sound as you scale Fast!

-**Total Oversight:** A transparent, auditable trail for every automated action.

-**Risk Mitigation:** Granular permissions that eliminate unauthorized data access.

-**Operational Agility:** The ability to modify and "hot-fix" live automations without process disruption.

### 4. Next Steps
We recommend a Phase 1 Pilot to identify your **"obvious" automation wins.**

**Discovery Call:** Review your most repetitive, high-margin tasks.

**Prototype:** Deploy a secure task-based agent within 90 days.

---

### **Join the Waitlist today: [axiomaticlab.com](https://axiomaticlab.com/)**
