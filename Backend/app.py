from fastapi import FastAPI,Request,Form
import uvicorn
import os,sys
import snowflake.connector as sc
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from .model import User,log,offre
from .function import password_hash,password_verify
from datetime import datetime


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
app=FastAPI()
load_dotenv()
app.add_middleware(SessionMiddleware,Secret_key=os.getenv("secret_key"),max_age=60)
templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"templates"))
templates=Jinja2Templates(directory=templates_dir)

#static
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"static"))
app.mount("/static",StaticFiles(directory=static_dir))


Connect = sc.connect(
    user= os.getenv("snowflake_user"),
    password= os.getenv("snowflake_password"),
    account=os.getenv("snowflake_account"),
    database=os.getenv("snowflake_database"),
)

cursor=Connect.cursor() 

@app.get("/home")
async def home_page(request:Request):
    
    return templates.TemplateResponse("home.html",{"request":request })


@app.get("/sing_up")
async def  connect_emp(request:Request):
    
    return templates.TemplateResponse("User.html",{"request":request })


@app.post("/sing_up")
async def connect_empl(request:Request, E:User):
    sql = "SELECT * FROM  Recrunova.Recrut.Users where Email=%s"
    params=[E.Email]
    cursor.execute(sql,params)
    resultat=cursor.fetchone()


    if resultat:
        return templates.TemplateResponse("User.html",{"request":request })
    else:
        
       y= password_hash(E.password)

       E.date_inscription = datetime.now()
       sql =""" 
       INSERT INTO  Recrunova.Recrut.Users ( nom,prenom,nom_entreprise,role,password,Tel,date_inscription,Email,Cv )
       values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
       
       """
       params=[E.nom,E.prenom,E.nom_entreprise,E.role,y,E.Tel,E.date_inscription,E.Email]
       x=cursor.execute(sql,params)


       return templates.TemplateResponse("User.html",{"request":request })
    

@app.get("/login")
async def  Login (request:Request):
    error=request.session.get("error",None)
    if error:
        return templates.TemplateResponse("login.html",{"request":request,"error":error})
    return templates.TemplateResponse("login.html",{"request":request})


@app.post("/login")

async def Login(L:log,request:Request):
    sql="SELECT *  FROM  Recrunova.Recrut.Users where Email=%s"
    params=[L.Email]
    cursor.execute(sql,params)
    resultat=cursor.fetchone()
    
    if resultat:
        x= password_verify(L.password,resultat[5])

        if x :
          s={
              "nom":resultat[1],
              "prenom":resultat[2],
              "Email":resultat[8],
              "Role":resultat[4],
            }
          response = RedirectResponse(url='/', status_code=302)
          
          request.session["user"] = s
          
          return response
        
        else:
          request.session["error"] = "mot de passe incorrect"
          
        return RedirectResponse(url='/login', status_code=302)
      
    else: 
        request.session["error"] = "email introuvable "

        return RedirectResponse(url='/login', status_code=302)
    

@app.get("/ajout_offre")
async def Ajout_offre(A:offre,request:Request):
    sql=" INSERT INTO Recrunova.Recrut.Offres( titre,langue,salaire,description,competences,type_poste,horaire,avantages)" \
    " values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    params=[ A.titre,A.langue,A.salaire,A.description,A.competences,A.type_poste,A.horaire,A.avantages]
    cursor.execute(sql,params)

    return templates.TemplateResponse("")






















if __name__=="__main__":
    uvicorn.run(app,host='0.0.0.0', port=8002, workers=1)