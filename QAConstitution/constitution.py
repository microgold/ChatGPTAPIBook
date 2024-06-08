import openai
import os
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from PyPDF2 import PdfReader


load_dotenv()
# Set your OpenAI API key

# Function to extract text from a PDF file


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


# Path to the PDF of the Constitution
pdf_path = 'c:\\temp\\constitution.pdf'

# Extract text from the PDF
constitution_text = extract_text_from_pdf(pdf_path)

# Initialize OpenAI LLM
llm = OpenAI()

# Create embeddings
embeddings = OpenAIEmbeddings()

# Create a text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=100)

# Split the text into chunks
texts = text_splitter.split_text(constitution_text)

# Create a vectorstore index
vectorstore = FAISS.from_texts(texts, embeddings)
print("Number of Embeddings created.",
      embeddings.embed_documents(texts).__len__())

# Create RetrievalQA
qa_chain = RetrievalQA.from_chain_type(
    llm, chain_type="stuff", retriever=vectorstore.as_retriever())

# Function to answer questions


def answer_question(question):
    answer = qa_chain.invoke(question)
    return answer


# Example usage
# question = "What is the purpose of the preamble of the Constitution?"
# answer = answer_question(question)
# print(f"Question: {question}\nAnswer: {answer}")

# question = "What does the constitution say about slavery?"
# answer = answer_question(question)
# print(f"Question: {question}\nAnswer: {answer}")

# question = "Give me a clear explanation for the second amendment."
# answer = answer_question(question)
# print(f"Question: {question}\nAnswer: {answer}")

# question = "Create a Quiz with 10 multiple choice questions about the constitution in json"
# answer = answer_question(question)
# print(f"Question: {question}\nAnswer: {answer}")

question = "What does the constitution say about exports and taxation?"
answer = answer_question(question)
print(f"Question: {question}\nAnswer: {answer}")
