
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_groq import ChatGroq

load_dotenv()

def get_llm():
    return(ChatGroq(model = 'openai/gpt-oss-120b' ,temperature= 0.3))

def split_transcript(transcript: str) -> list:
    splitter =RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap =100
    )

    return splitter.split_text(transcript)

def summarize(transcript :str ) -> str :
    llm =get_llm()

    map_prompt =ChatPromptTemplate.from_messages([
        ('system', 'summarize this portion of a meeting transcript concisely'),
        ('human' , '{text}'), 
    ])

    map_chain = map_prompt | llm | StrOutputParser()
    chunks = split_transcript(transcript)

    chunk_summarize =[map_chain.invoke({'text' : chunk}) for chunk in chunks]

    combined ='\n\n'.join(chunk_summarize)

    combined_prompt =ChatPromptTemplate.from_messages([
        ('system' , "you are an expert meeting summarizer.combine these partial summaries into one final professional  meeting summary in bullet points." ),
         ('human' , '{text}')
    ])

    combined_chain = (
        RunnablePassthrough() | RunnableLambda(lambda x : {'text' : x}) | combined_prompt | llm |StrOutputParser()
    )
    return combined_chain.invoke(combined)

def generate_title(transcript : str) -> str :
    llm = get_llm()

    title_chain = (
        RunnablePassthrough() | RunnableLambda(lambda x : {'text' : x}) | 
        ChatPromptTemplate.from_messages([
            ('system' , """
             'based on the meeting transcript, generate a short professional meeting title
             (max 8 words).only return the title, nothing else.           
             """),
             ('human' , '{text}')
        ])
        | llm | StrOutputParser()
    )

    return title_chain.invoke(transcript[:1000])
