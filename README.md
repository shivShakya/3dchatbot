# 3D Interactive AI Agent with Agentic Workflow & RAG

A high-performance, interactive 3D chatbot featuring an agentic workflow for real-time web intelligence. The system combines visual perception, lip-syncing, and Retrieval-Augmented Generation (RAG) to provide a deeply immersive conversational experience.

By leveraging **Google Gemini Flash** and optimized speech APIs, the system achieves near-instant response times (~0.5s for standard queries).

---

## Technical Architecture

The system operates on an **Agentic Workflow**, allowing the LLM to decide when to fetch real-time data or query the internal RAG database.



### Core Components:
* **3D Rendering Engine**: Built with Three.js and WebGL for realistic character models.
* **Speech & Lip-Sync**: Integrated Unreal API for low-latency voice generation with synchronized facial movements.
* **Visual Perception**: Enables the chatbot to "see" and respond to the user's environment.
* **Generalized RAG Pipeline**: Users can upload custom documents to create specialized knowledge bases accessible via unique Iframe IDs.

---

## Key Features

* **Real-Time Intelligence**: Agentic workflow capable of performing web searches for up-to-the-minute information.
* **Optimized Performance**: Standard responses delivered in ~0.5s; complex web-searches in 2–3s.
* **Immersive Interaction**: Real-time lip-sync, custom animations, and gesture support.
* **Customizable Content**: Upload stories or documents to personalize the chatbot’s persona and knowledge.
* **Seamless Integration**: Generates embeddable Iframes with authorized domain control.
* **Multi-Modal**: Supports both voice and text-based interactions across Web and VR platforms.

---

## Technology Stack

| Layer | Technology |
| :--- | :--- |
| **LLM** | Google Gemini Flash |
| **Orchestration** | LangChain (Agentic Workflow & RAG) |
| **3D Engine** | Three.js & WebGL |
| **Backend** | Python (FastAPI / Flask) |
| **Voice Synthesis** | Unreal API |
| **Data Processing** | Vector Databases for RAG |

---

## Use Cases

* **Next-Gen Customer Support**: Embeddable 3D agents that handle real-time booking and form-filling.
* **Immersive Education**: Interactive tutors that utilize uploaded curriculum for personalized training.
* **Interactive Storytelling**: RPG-style experiences where the chatbot adapts its personality based on uploaded lore.
* **VR/AR Assistants**: Spatial agents for virtual reality environments.

---

## Deployment & Integration

The system features a **Generalized Training Pipeline**:
1.  **Upload**: Provide a PDF, TXT, or URL.
2.  **Process**: The RAG pipeline indexes the content.
3.  **Embed**: Receive a unique ID and Iframe code.
4.  **Authorize**: Secure the widget by whitelisting specific domains.

---
