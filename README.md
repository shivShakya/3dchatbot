I built a 3D chatbot with an agentic workflow that can fetch real-time information through web searches. It also features real-time lip-sync and the ability to visually perceive the user.

For speech generation, I’ve integrated Unreal's nearly free API, and I use Google’s Gemini model—specifically Gemini Flash—for the LLM. After experimenting with various free models, I found Gemini Flash to deliver the best results for tool calling and overall performance.

I’ve optimized the system to minimize latency, which is now around 0.5 seconds for standard responses. For longer sentences or web searches, the response time is approximately 2–3 seconds.
