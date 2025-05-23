I built a 3D chatbot with an agentic workflow that can fetch real-time information through web searches. It features real-time lip-sync and the ability to visually perceive the user.

For speech generation, I’ve integrated Unreal’s nearly free API, and I use Google’s Gemini model—specifically Gemini Flash—as the LLM. After experimenting with various free models, I found Gemini Flash to offer the best performance, especially for tool calling.

I’ve optimized the system to minimize latency, achieving around 0.5 seconds for standard responses. For longer sentences or web searches, the response time is approximately 2–3 seconds.

Additionally, I implemented a RAG (Retrieval-Augmented Generation) system along with a generalized training pipeline. You can simply upload a story or custom content, and the system will generate a unique iframe with an associated ID. This iframe can be embedded on any domain, while domain-level security checks ensure that only authorized domains can use it. This allows the same 3D chatbot to be easily personalized with your own data—just by uploading your content.

Langchain 
Agentic Rag 
Real Time Booking System .
Real Time Form Filling System. 
Visual Capabilties.
Web Search .
