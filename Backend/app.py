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
   user = request.session.get("user")
   if user:
        return templates.TemplateResponse("home.html",{"request":request ,"username":user})
   return templates.TemplateResponse("home.html",{"request":request })


@app.get("/sing_up")
async def  connect_emp(request:Request):
    
    return templates.TemplateResponse("User.html",{"request":request })


@app.post("/sing_up")
async def connect_empl(request:Request,  nom :str = Form(...),
    prenom :str = Form(...),
    nom_entreprise:str = Form(...),
    role :str= Form(...),
    password :str = Form(...),
    Tel :str= Form(...),
    date_inscription:str = Form(...),
    Email :str = Form(...)):

    sql = "SELECT * FROM  Recrunova.Recrut.Users where Email=%s"
    params=[Email]
    cursor.execute(sql,params)
    resultat=cursor.fetchone()


    if resultat:
        return templates.TemplateResponse("User.html",{"request":request,"message" : "Cet Email existe deja "})
    else:
        
       y= password_hash(password)

       date_inscription = datetime.now()
       sql =""" 
       INSERT INTO  Recrunova.Recrut.Users ( nom,prenom,nom_entreprise,role,password,Tel,date_inscription,Email )
       values (%s,%s,%s,%s,%s,%s,%s,%s)
       
       """
       params=[nom,prenom,nom_entreprise,role,y,Tel,date_inscription,Email]
       x=cursor.execute(sql,params)


    return RedirectResponse(url='/login',status_code=200)
    

@app.get("/login")
async def  Login (request:Request):
    error=request.session.get("error",None)
    if error:
        return templates.TemplateResponse("login.html",{"request":request,"error":error})
    return templates.TemplateResponse("login.html",{"request":request})


@app.post("/login")

async def Login(request:Request, Email :str =Form(...),password :str = Form(...)):
    sql="SELECT *  FROM  Recrunova.Recrut.Users where Email=%s"
    params=[Email]
    cursor.execute(sql,params)
    resultat=cursor.fetchone()
    
    if resultat:
        x= password_verify(password,resultat[5])

        if x :
          s={
              "user_id":resultat[0],
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
    

@app.post("/ajout_offre")
async def Ajout_offre(request:Request, titre :str = Form(...), langue :str = Form(...),salaire :str = Form(...),description :str= Form(...),competences :str= Form(...),type_poste :str = Form(...),horaire :str= Form(...), avantages :str= Form(...),):
    sql=" INSERT INTO Recrunova.Recrut.Offres( user_id,titre,langue,salaire,description,competences,type_poste,horaire,avantages) values (%s,%s,%s,%s,%s,%s,%s,%s)"

    params= [user_id,titre,langue,salaire,description,competences,type_poste,horaire,avantages]
    cursor.execute(sql,params)

    return templates.TemplateResponse("home.html",{"request":request})


@app.get("/recup_offre")
async def Recuper_off(request:Request):
    sql="SELECT * FROM  Recrunova.Recrut.Offres"
    cursor.execute(sql)
    resultat=cursor.fetchall()
  

    return templates.TemplateResponse("offres.html",{"request":request,"resultat":resultat})


@app.get("/description/{id}")
async def Descrip(request:Request,offre_id:str = (...)):
    sql="SELECT * FROM Recrunova.Recrut.offres where offre_id =%s"
    cursor.execute(sql)
    resultat=cursor.fetchone()


    return templates.TemplateResponse("description.html",{"request":request,"resultat":resultat})
   


@app.post("/logout")
async def logout(request:Request):
    response =RedirectResponse(url='/login')
    request.session.clear()
    return response



















if __name__=="__main__":
    uvicorn.run(app,host='0.0.0.0', port=8002, workers=1)