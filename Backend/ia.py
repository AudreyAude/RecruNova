from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import *
from langchain_core.runnables import RunnableParallel,RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import Docx2txtLoader,PyPDFLoader
from sklearn.metrics.pairwise import cosine_similarity

from dotenv import load_dotenv
import os
import io



def cv_matching(path,response):

        embeddings=OpenAIEmbeddings(model="text-embedding-ada-002", api_key=os.getenv("ApiKey"))
                #cv 
        path_cv=rf"{path}"
        extension=os.path.splitext(path_cv)[1].lower()
        
        if extension==".docx":
                

                loader_cv=Docx2txtLoader(path_cv)
                text_cv=loader_cv.load()
                text_cv_content=text_cv[0].page_content
        
        if extension==".pdf":
           loader = PyPDFLoader(path_cv)
           documents = loader.load()
           text_cv_content=documents[0].page_content

           

        #offre
        
        text_offre=response
        text_offre_content=text_offre

        #embeddings

        cv_embeddings=embeddings.embed_documents([text_cv_content])
        offre_embeddings=embeddings.embed_documents([text_offre_content])

        #similarite

        similarite=cosine_similarity([cv_embeddings[0]],[offre_embeddings[0]])[0][0]
        
        return(similarite)


def lettre_motivation(reponse):
        model=ChatOpenAI(model="gpt-3.5-turbo",temperature=0.0,api_key=os.getenv("ApiKey"))

        parser=StrOutputParser()
        chain=model|parser

        
        template= """
       Rédige une lettre de motivation 100 % personnalisée à partir de l'offre d'emploi ci-dessus :
        {offre_emploi}

        et en suivant ces règles :

        1. Personnaliser 100% à partir des informations de l'offre
        2. Structure classique : introduction, compétences techniques, compétences comportementales, conclusion
        3. Ton professionnel et enthousiaste
        4. Ne pas inventer d'informations non présentes dans l'offre
        Fais en sorte que la lettre semble écrite sur mesure pour ce poste
        """ 
        prompt=ChatPromptTemplate.from_template(template)


        chain=prompt|model|parser


        text_split_offre=RecursiveCharacterTextSplitter(chunk_size=100,chunk_overlap=20)
        doc_offre=text_split_offre.split_text(reponse)

        embeddings=OpenAIEmbeddings(model="text-embedding-ada-002", api_key=os.getenv("ApiKey"))

        VectorStore_offre= DocArrayInMemorySearch.from_texts(doc_offre,embedding=embeddings)

        chunks_retriever_offre=VectorStore_offre.as_retriever()

        setup=RunnableParallel(offre_emploi=chunks_retriever_offre ,question=RunnablePassthrough())

        chain=setup|prompt|model|parser
        question = ("Génère une lettre de motivation ultra personnalisée pour ce poste, en suivant rigoureusement les exigences "
    "de l'offre. Appuie-toi uniquement sur les infos présentes dans l'offre pour formuler la lettre comme si elle "
    "était écrite par un vrai candidat qui répond point par point aux attentes de l'entreprise.")

        # question="genere moi une lettre de motivation en fonction de l offre d'emploi"
        x=chain.invoke(question)
      
        return(x)


from fpdf import FPDF

def save_text_to_pdf(text, filename="lettre_de_motivation.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    lines = text.split('\n')
    for line in lines:
        pdf.multi_cell(0, 10, txt=line)

   
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
 



