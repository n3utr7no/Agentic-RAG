from langchain_groq import ChatGroq

light_model = ChatGroq(
    model='openai/gpt-oss-20b',
    temperature=0.0
)

good_model = ChatGroq(
    model='llama-3.3-70b-versatile',
    temperature=0.0
)
