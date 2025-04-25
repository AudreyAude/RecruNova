from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import *
from langchain_core.runnables import RunnableParallel,RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import Docx2txtLoader,PyPDFLoader
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

from dotenv import load_dotenv
import os
from io import BytesIO



def cv_matching(path,response):

        embeddings=OpenAIEmbeddings(model="text-embedding-ada-002", api_key=os.getenv("ApiKey"))
                #cv 
        path_cv=rf"{path}"
        path=Path(path_cv)
        extension=os.path.splitext(path)[1].lower()
        
        
        if extension==".docx":
                

                loader_cv=Docx2txtLoader(path)
                text_cv=loader_cv.load()
                text_cv_content=text_cv[0].page_content
        
        if extension==".pdf":
           loader = PyPDFLoader(path)
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

    pdf_bytes = pdf.output(dest='S').encode('latin1')  

  
    pdf_buffer = BytesIO(pdf_bytes)
    pdf_buffer.seek(0)
    return pdf_buffer

def chat(path,response,question):
        model=ChatOpenAI(model="gpt-3.5-turbo",temperature=0.0,api_key=os.getenv("ApiKey"))

        parser=StrOutputParser()
        chain=model|parser

        template= """
                tu t appeles Audrey toujours te presenter
                CONTEXTE OBLIGATOIRE :
                1. CV du candidat ({cv})
                - Extraire exhaustivement :
                * Compétences techniques
                * Expériences professionnelles
                * Formations
                * Certifications
                * Réalisations significatives

                2. Offre d'emploi ({offre_emploi})
                - Identification précise :
                * Intitulé du poste
                * Missions principales
                * Compétences techniques requises
                * Compétences comportementales
                * Prérequis et profil recherché

                3. Question de l'utilisateur ({question})
                - Analyse du besoin spécifique
                - Intention de la demande
                - Contexte de la requête

                MÉCANISME DE TRAITEMENT :
                - Mapping compétences à 100%
                - Scoring de correspondance
                - Identification des écarts et opportunités
                - Réponse ultraPersonnalisée

                RÈGLES DE GÉNÉRATION :
                - 90% des informations proviennent du contexte
                - Zéro invention
                - Langage précis et professionnel
                - Justification systématique

                ALGORITHME DE RÉPONSE :
                - Correspondance > 80% : Valorisation
                - Correspondance < 80% : Recommandations de développement
                - Traçabilité des éléments de réponse

                TON :
                - Expert
                - Bienveillant
                - Constructif
                - Orienté solution
                """
        prompt=ChatPromptTemplate.from_template(template)


        chain=prompt|model|parser

        #cv 
        path_cv=rf"{path}"
        extension=os.path.splitext(path_cv)[1].lower()
        
        if extension==".docx":
                

                loader_cv=Docx2txtLoader(path_cv)
                text_cv=loader_cv.load()
                
        
        if extension==".pdf":
           loader = PyPDFLoader(path_cv)
           text_cv = loader.load()
           
        # loader_cv=Docx2txtLoader(path_cv)
        # text_cv=loader_cv.load()
        text_split_cv=RecursiveCharacterTextSplitter(chunk_size=100,chunk_overlap=20)
        doc_cv=text_split_cv.split_documents(text_cv)
        #offre
        text_split_offre=RecursiveCharacterTextSplitter(chunk_size=100,chunk_overlap=20)
        doc_offre=text_split_offre.split_text(response)

        embeddings=OpenAIEmbeddings(model="text-embedding-ada-002", api_key=os.getenv("ApiKey"))

        VectorStore_cv= DocArrayInMemorySearch.from_documents(doc_cv,embedding=embeddings)
        VectorStore_offre= DocArrayInMemorySearch.from_texts(doc_offre,embedding=embeddings)

        chunks_retriever_cv=VectorStore_cv.as_retriever()
        chunks_retriever_offre=VectorStore_offre.as_retriever()
       
        setup=RunnableParallel(cv=chunks_retriever_cv, offre_emploi=chunks_retriever_offre ,question=RunnablePassthrough())

        chain=setup|prompt|model|parser
        x=chain.invoke(question)
        return x

def chatE(path,response,question):
        model=ChatOpenAI(model="gpt-3.5-turbo",temperature=0.0,api_key=os.getenv("ApiKey"))

        parser=StrOutputParser()
        chain=model|parser

        template = """
Tu t'appelles Audrey, une assistante RH experte. Toujours te présenter brièvement comme telle.

CONTEXTE ESSENTIEL :
1. CV du candidat ({cv})
- Extraire et structurer :
  * Compétences techniques et transversales
  * Expériences professionnelles (postes, missions, résultats)
  * Formations et diplômes
  * Certifications et reconnaissances
  * Réalisations marquantes et projets

2. Offre d'emploi ({offre_emploi})
- Identifier précisément :
  * Titre du poste
  * Responsabilités principales
  * Compétences techniques et humaines requises
  * Profil recherché (expérience, niveau d’étude, qualités)
  * Critères obligatoires ou différenciateurs

3. Question de l'employeur ({question})
- Comprendre l’intention (évaluation, doute, curiosité, vérification)
- Mettre en lien avec les éléments du CV et de l’offre
- Fournir une réponse orientée décision et justifiée

MÉCANISME D’ANALYSE :
- Matching précis entre le CV et les exigences du poste
- Taux de couverture des compétences et expériences
- Analyse des écarts et propositions de valorisation ou de développement
- Identification de tout signal fort ou faible du profil

RÈGLES DE GÉNÉRATION DE LA RÉPONSE :
- 90% minimum des données doivent venir du contexte fourni
- Aucune supposition non justifiée
- Langage professionnel, clair, structuré
- Réponse toujours justifiée par des éléments concrets du CV ou de l’offre

TON :
- Professionnel
- Respectueux
- Neutre et objectif
- Orienté décision pour l’employeur

OBJECTIF :
- Aider l’employeur à évaluer rapidement la pertinence du candidat
- Fournir des éléments fiables et exploitables pour la prise de décision
- Valoriser le profil ou proposer des pistes d’amélioration si nécessaire
"""

        prompt=ChatPromptTemplate.from_template(template)


        chain=prompt|model|parser

        #cv 
        path_cv=rf"{path}"
        extension=os.path.splitext(path_cv)[1].lower()
        
        if extension==".docx":
                

                loader_cv=Docx2txtLoader(path_cv)
                text_cv=loader_cv.load()
                
        
        if extension==".pdf":
           loader = PyPDFLoader(path_cv)
           text_cv = loader.load()
           
        # loader_cv=Docx2txtLoader(path_cv)
        # text_cv=loader_cv.load()
        text_split_cv=RecursiveCharacterTextSplitter(chunk_size=100,chunk_overlap=20)
        doc_cv=text_split_cv.split_documents(text_cv)
        #offre
        text_split_offre=RecursiveCharacterTextSplitter(chunk_size=100,chunk_overlap=20)
        doc_offre=text_split_offre.split_text(response)

        embeddings=OpenAIEmbeddings(model="text-embedding-ada-002", api_key=os.getenv("ApiKey"))

        VectorStore_cv= DocArrayInMemorySearch.from_documents(doc_cv,embedding=embeddings)
        VectorStore_offre= DocArrayInMemorySearch.from_texts(doc_offre,embedding=embeddings)

        chunks_retriever_cv=VectorStore_cv.as_retriever()
        chunks_retriever_offre=VectorStore_offre.as_retriever()
       
        setup=RunnableParallel(cv=chunks_retriever_cv, offre_emploi=chunks_retriever_offre ,question=RunnablePassthrough())

        chain=setup|prompt|model|parser
        x=chain.invoke(question)
        return x


 



