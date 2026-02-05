Project Title: Agentic AI-Powered Engineering Platform Learning and Onboarding Assistant

Objectives: Design and build a personalized learning and onboarding capability as part of the existing company portal. The system will:
Recommend tailored learning paths and modules based on a user’s role, skills, and progress.
Answer questions about the engineering platform tech stack, architecture, and policies.
Track user progress and completion across modules and activities.
Under the hood, the solution combines:
A RAG (Retrieval-Augmented Generation) chatbot over internal documentation and knowledge bases.
A recommendation engine that guides users on what to learn next.

Project Details:
Build a full-stack solution that supports engineering platform users by:

Recommending personalized learning paths
Curate and recommend courses/modules based on role (e.g., platform engineer, backend engineer), prior skills, and historical progress.
Use LLM-driven logic to adapt learning paths over time, giving you exposure to multiple phases of the software development lifecycle (requirements, design, implementation, testing, deployment, and iteration).

Providing a RAG-based Q&A assistant. 

The assistant will answer questions related to:

Platform policies and guidelines
Engineering tech stack and reference architectures
Internal best practices, patterns, and playbooks
RAG connects LLMs to internal documentation using embeddings and vector databases, enabling accurate, domain-specific Q&A grounded in company knowledge rather than generic internet data.

Stack

UX & Frontend – building intuitive dashboards, learning views, and a chat interface using React
Backend – designing and implementing APIs for users, modules, progress, and recommendations using Fast API/Python
AI / Data Layer – implementing the RAG pipeline and recommendation logic using modern LLM tooling with Agentic AI using LangGraph
Databases – modeling users, curating content, quiz results, and progress in PostgreSQL