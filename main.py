from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import pandas as pd
import chromadb
import uuid
import os
from dotenv import load_dotenv
load_dotenv()
llm = ChatGroq(
    temperature = 0,
    groq_api_key=os.environ["GROG_API_KEY"],
    model_name = "llama-3.1-70b-versatile"
)
# urlext = "https://odolution.com/jobs/detail/python-developer-interns-lead-to-permanent-job-87"
def pageExt(urlext):
    loader = WebBaseLoader(urlext)
    page_data = loader.load().pop().page_content

    promptScrape = PromptTemplate.from_template(
    """
        ### SCRAPED TEXT FROM WEBSITE:
        {page_data}
        ### INSTRUCTION:
        The scraped text is from the career's page of a website.
        Your job is to extract the job postings and return them in JSON format containing the 
        following keys: `role`, `experience`, `skills` and `description`.
        Only return the valid JSON.
        ### VALID JSON (NO PREAMBLE):    
        """
    )
    chainScrape = promptScrape | llm 
    res = chainScrape.invoke(input={'page_data':page_data})
    # print(page_data)
    jsonparser = JsonOutputParser()
    jsonRes = jsonparser.parse(res.content)

    if type(jsonRes) == list:
        return jsonRes[0]
    else:
        return jsonRes
# fileurl = "portfolio.csv"
def portfoliodb(fileurl):
    """make sure to put csv in file path"""
    df = pd.read_csv(fileurl)
    
    client = chromadb.PersistentClient("vectordb")
    collection = client.get_or_create_collection(name="portfolio")

    if not collection.count():
        for _, row in df.iterrows():
            collection.add(documents=row["Techstack"],
                        metadatas={"links": row["Links"]},
                        ids=[str(uuid.uuid4())])

    


def coldEmailGen(jsonobj):
    client = chromadb.PersistentClient("vectordb")
    collection = client.get_or_create_collection(name="portfolio")
    links = collection.query(query_texts=jsonobj['skills'], n_results=2).get('metadatas', [])
    prompt_email = PromptTemplate.from_template(
        """
        ### JOB DESCRIPTION:
        {job_description}
        
        ### INSTRUCTION:
        You are Hamza Ali, AI\ML Engineer at Techyaim. Techyaim is an AI & Software Consulting company dedicated to facilitating
        the seamless integration of business processes through automated tools. 
        Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
        process optimization, cost reduction, and heightened overall efficiency. 
        Your job is to write a cold email to the client regarding the job mentioned above describing the capability of Techyaim 
        in fulfilling their needs.
        Also add the most relevant ones from the following links to showcase Techyaim's portfolio: {link_list}
        Remember you are Hamza, AI\ML Engineer at Techyaim. 
        Do not provide a preamble.
        ### EMAIL (NO PREAMBLE):
        
        """
        )

    chain_email = prompt_email | llm
    res = chain_email.invoke({"job_description": str(jsonobj), "link_list": links})
    # print(res.content)
    return res.content

import re

def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]*?>', '', text)
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    # Remove special characters
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s{2,}', ' ', text)
    # Trim leading and trailing whitespace
    text = text.strip()
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

if __name__ == "__main__":
    fileurl = "my_portfolio.csv"
    portfoliodb(fileurl)

