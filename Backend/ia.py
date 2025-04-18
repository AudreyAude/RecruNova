from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import *
from langchain_core.runnables import RunnableParallel,RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import Docx2txtLoader
from sklearn.metrics.pairwise import cosine_similarity

from dotenv import load_dotenv
import os


def cv_matching(path,response):

        embeddings=OpenAIEmbeddings(model="text-embedding-ada-002", api_key=os.getenv("ApiKey"))
                #cv 
        path_cv=rf"{path}"
        loader_cv=Docx2txtLoader(path_cv)
        text_cv=loader_cv.load()
        text_cv_content=text_cv[0].page_content

        #offre
        
        text_offre=response
        text_offre_content=text_offre

        #embeddings

        cv_embeddings=embeddings.embed_documents([text_cv_content])
        offre_embeddings=embeddings.embed_documents([text_offre_content])

        #similarite

        similarite=cosine_similarity([cv_embeddings[0]],[offre_embeddings[0]])[0][0]
        
        return(similarite)