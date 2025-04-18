from fastapi import FastAPI,Request,Form,UploadFile,File
import uvicorn
import os,sys
import snowflake.connector as sc
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
# from .model import User,log,offre
from .function import password_hash,password_verify
from.Mail import mailPostuleCandidat,mailRegister
from datetime import datetime


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
app=FastAPI()
load_dotenv()

app.add_middleware(SessionMiddleware,secret_key=os.getenv("secret_key"),max_age=300)
templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"templates"))
templates=Jinja2Templates(directory=templates_dir)

#static 
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"static"))
app.mount("/static",StaticFiles(directory=static_dir), name="static")

   
Connect = sc.connect(
    user= os.getenv("snowflake_user"),
    password= os.getenv("snowflake_password"),
    account=  os.getenv("snowflake_account"),
    database=os.getenv("snowflake_database"),
)
 
cursor=Connect.cursor() 

current_time=datetime.now()
     
time=current_time.strftime("%Y-%m-%d")

@app.get("/")
async def home_page(request:Request):
    user = request.session.get("user")
   
    if user:
        return templates.TemplateResponse("home.html",{"request":request ,"username":user})
   
    return templates.TemplateResponse("home.html",{"request":request })
 
@app.get("/sing_up")
async def  connect_emp(request:Request):
    
    return templates.TemplateResponse("User.html",{"request":request })


@app.post("/sing_up")
async def connect_empl(request:Request, nom: str=Form(...),prenom:str=Form(...),nom_entreprise:str=Form(...),role:str=Form(...),password:str=Form(...),Tel:str=Form(...),Email:str=Form(...)):
    
    sql = "SELECT * FROM  Recrunova.Recrut.Users where Email=%s"
    params=[Email]
    cursor.execute(sql,params)
    resultat=cursor.fetchone()

    if resultat:
        message=f"{Email} est deja utilise "
       
        return templates.TemplateResponse("User.html",{"request":request ,"message":message })
    else:
        
       y= password_hash(password)

       
      
       sql =""" 
       INSERT INTO  Recrunova.Recrut.Users ( nom,prenom,nom_entreprise,role,password,Tel,date_inscription,Email )
       values (%s,%s,%s,%s,%s,%s,%s,%s)
       
       """
       params=[nom,prenom,nom_entreprise,role,y,Tel,time,Email]
       cursor.execute(sql,params)
       password= os.getenv("password")
       if role=="1":
           
            mailRegister(Email,nom_entreprise,password)
       else:
            mailRegister(Email,nom,password)
        

       return RedirectResponse(url="/login",status_code=302)
     

@app.get("/login")
async def  Login (request:Request):
    error=request.session.get("error",None)
    if error:
        return templates.TemplateResponse("login.html",{"request":request,"error":error})
    return templates.TemplateResponse("login.html",{"request":request})


@app.post("/login")

async def Login(request:Request,Email:str=Form(...),password:str=Form(...)):
  
  if not Email or not password: 
    request.session["error"] = "veuillez remplir tout les champs svp"
    return RedirectResponse(url='/login', status_code=302)

  else: 
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
              "organisation":resultat[3],
              "Email":resultat[8],
              "Role":resultat[4],
              "tel":resultat[6],
              "date":resultat[7],
              "cv":resultat[9],
              "password":resultat[5]
              
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
    
@app.get("/candidature/{id}") 
async def candidature (request:Request,id:str):
    user=request.session.get("user",None) 
    if user:
        sql = """
  SELECT u.NOM_ENTREPRISE,o.titre,c.statut, c.date FROM Recrunova.Recrut.Candidatures AS c
  JOIN Recrunova.Recrut.Offres AS o
  ON c.offre_id = o.offre_id
  JOIN Recrunova.Recrut.users AS u
  ON o.user_id = u.user_id
  WHERE c.user_id =%s;
   
    """
        params=[id]
        cursor.execute(sql,params)
        resultat=cursor.fetchall()
    
        return templates.TemplateResponse("candidature.html",{"request":request,"username":user,"resultat":resultat})
    return templates.TemplateResponse("home.html",{"request":request})

@app.get("/ajout_offre")
async def Ajout_offre(request:Request):
        user = request.session.get("user")
   
        if user:
            return templates.TemplateResponse("Addjob.html",{"request":request ,"username":user})
        return templates.TemplateResponse("Addjob.html.html",{"request":request})



@app.post("/ajout_offre")
async def Ajout_offre(request:Request, user_id:str=Form(...), titre :str = Form(...), langue :str = Form(...),salaire :str = Form(...),description :str= Form(...),competences :str= Form(...),type_poste :str = Form(...),horaire :str= Form(...), avantages :str= Form(...),lieu:str=Form(...)):
    user = request.session.get("user")

    if user:
        if user['Role']=="2":
                message="desole un compte employeur est necessaire"
                return templates.TemplateResponse("Addjob.html",{"request":request,"message":message,"username":user})

        else:

            
            if not titre or not langue or not salaire or not description or not competences or not type_poste or not horaire or not avantages or not lieu :
                message="veuillez remplir tout les champs svp"
                return templates.TemplateResponse("Addjob.html",{"request":request,"message":message,"username":user})


            else:
                    sql=" INSERT INTO Recrunova.Recrut.Offres( user_id,titre,langue,salaire,description,competences,type_poste,horaire,avantages,lieu,date,entreprise) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

                    params=[user_id,titre,langue,salaire,description,competences,type_poste,horaire,avantages,lieu,time,user['organisation']]
                    cursor.execute(sql,params)
                    message="l'emploie a ete bien publie"

                    return templates.TemplateResponse("Addjob.html",{"request":request,"message":message,"username":user})
    else:
       RedirectResponse(url='/login', status_code=302)


@app.get("/offre")
async def offre(request:Request):
        sql="SELECT * FROM  Recrunova.Recrut.Offres"
        cursor.execute(sql)
        resultat=cursor.fetchall()
        user = request.session.get("user")
        if user:
          return templates.TemplateResponse("offre.html",{"request":request, "resultat":resultat,"username":user})


        
        return templates.TemplateResponse("offre.html",{"request":request, "resultat":resultat})

@app.get("/description/{id}")  
async def description(request:Request, id:str):
    user = request.session.get("user")
    
    sql="SELECT * FROM  Recrunova.Recrut.Offres where OFFRE_ID=%s"
    params=[id]
    cursor.execute(sql,params)
    resultat=cursor.fetchone()
    return templates.TemplateResponse("description.html",{"request":request,"resultat":resultat,"username":user})
 

@app.get("/addcv")
async def addcv(request:Request):
        
        user = request.session.get("user")

        if user:
            return templates.TemplateResponse("Addcv.html",{"request":request ,"username":user})
        return RedirectResponse(url='/login', status_code=302)

@app.post("/addcv")
async def addcv(request:Request,file:UploadFile=File(...),user_id: str = Form(...)):
        
        user = request.session.get("user")
        content_Type = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
        if file.content_type not in content_Type or file is None:
            response='format de fichier non valide'
        else:  
            path_dir="Backend\static\CVs"
            path=rf"{os.path.join(path_dir,file.filename)}"
     
            content= await file.read()

            sql = """
            update Recrunova.Recrut.Users set cv =%s where user_id =%s
            """ 
            params=[path,user_id] 
            cursor.execute(sql,params)

            with open(path,"wb")as f:

              
                f.write(content)
                response=f"{file.filename} a ete bien ajouter"
           

        if user:
            return templates.TemplateResponse("Addcv.html",{"request":request ,"username":user,"message":response})
        return RedirectResponse(url='/login', status_code=302)  


@app.get("/recup_offre")
async def Recuper_off(request:Request):
    sql="SELECT * FROM  Recrunova.Recrut.Offres"
    cursor.execute(sql)
    resultat=cursor.fetchall()
  

    return templates.TemplateResponse("offres.html",{"request":request,"resultat":resultat})

 


@app.get("/postule/{id}") 
async def postule(request:Request,id:str):
        
        user = request.session.get("user")

        if user:
            return templates.TemplateResponse("postule.html",{"request":request ,"username":user,"id":id})
        return RedirectResponse(url='/login', status_code=302)


@app.post("/postule")
async def postule(request:Request,file:UploadFile=File(...),file1:UploadFile=File(...),user_id: str = Form(...),offre_id:str=Form(...)):
        
        user = request.session.get("user")
        if user:

            content_Type = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
            if file.content_type not in content_Type or file is None or file1.content_type not in content_Type:
                response='format de fichier non valide'
            else:
                path_dir="Backend\static\Lettre"
                path_dir_cv="Backend\static\CVs"

                path=rf"{os.path.join(path_dir,file.filename)}"
                path1=rf"{os.path.join(path_dir_cv,file1.filename)}"


        
                statut="en cours de traitement"
                sql=" INSERT INTO Recrunova.Recrut.Candidatures(user_id,Offre_id,statut,lettre_motivation,cv,date) values (%s,%s,%s,%s,%s)"
                params=[user_id,offre_id,statut,path,path1,time] 
               
                cursor.execute(sql,params)
                Tab=[path,path1]
                for i in Tab:

                 with open(path,"wb")as f:

                    content= await file.read()
                  
                    f.write(content)
                response=f"candidature a ete bien recu"
                password= os.getenv("password")

                mailPostuleCandidat(user['Email',user['nom'],password])

                return templates.TemplateResponse("postule.html",{"request":request ,"username":user,"message":response})
        return RedirectResponse(url='/login', status_code=302)  

@app.get("/listcandidature/{id}") 
async def listcandidature (request:Request,id:str):
    user=request.session.get("user",None) 
    if user:
        sql = """
  SELECT o.titre,u.nom,u.prenom ,c.cv,c.LETTRE_MOTIVATION,c.statut,c.candidature_id,o.date  FROM Recrunova.Recrut.Candidatures AS c
  JOIN Recrunova.Recrut.Offres AS o
  ON c.offre_id = o.offre_id
  JOIN Recrunova.Recrut.users AS u
  ON c.user_id = u.user_id 
  WHERE o.user_id = %s;
   
    """ 
        params=[id]
        cursor.execute(sql,params)
        resultat=cursor.fetchall()
        response=[]
        for item in resultat:
            tab={
                "titre":item[0],
                "nom":item[1],
                "prenom":item[2],
                "cv":item[3].replace("Backend",""),
                "lettre_motivation":item[4].replace("Backend",""),
                "statut":item[5],
                "id_user":item[6],
                "date":item[7]


            }
            response.append(tab)
       
        return templates.TemplateResponse("listcandidature.html",{"request":request,"username":user,"resultat":response})
    return templates.TemplateResponse("home.html",{"request":request})

@app.get("/Updatestatut/{value}/{id}") 
async def Updatestatut (request:Request,value:str,id:str):
    user=request.session.get("user",None) 
    if user:
        sql = """
  UPDATE Recrunova.Recrut.Candidatures
SET statut =%s
WHERE candidature_id=%s;


    """ 
        params=[value,id]
        cursor.execute(sql,params)
      
        return RedirectResponse(url=f"/listcandidature/{user['user_id']}",status_code=302)
    return templates.TemplateResponse("home.html",{"request":request})



@app.get("/ListOffre/{id}") 
async def ListOffre (request:Request,id:str):
    user=request.session.get("user",None) 
    if user:
        sql = """
        SELECT offre_id,titre    FROM Recrunova.Recrut.offres 
        WHERE user_id = %s;
   
        """ 
        params=[id]
        cursor.execute(sql,params)
        resultat=cursor.fetchall()
       
        return templates.TemplateResponse("Listeoffre.html",{"request":request,"username":user,"resultat":resultat})
    return templates.TemplateResponse("home.html",{"request":request})


@app.get("/UpdateOffre/{id}") 
async def UpdateOffre (request:Request,id:str):
    user=request.session.get("user",None) 
    if user: 
    

        sql ="""
        SELECT offre_id,titre,langue,salaire,description,competences,type_poste,horaire,avantages,lieu   FROM Recrunova.Recrut.offres 
        WHERE offre_id = %s;
   """  
        params=[id]
        cursor.execute(sql,params)
        resultat=cursor.fetchone()
      
        return templates.TemplateResponse("updatJob.html",{"request":request,"username":user,"resultat":resultat})

    return templates.TemplateResponse("home.html",{"request":request})


@app.post("/UpdateOffre") 
async def UpdateOffre (request:Request,offre_id:str=Form(...), titre :str = Form(...), langue :str = Form(...),salaire :str = Form(...),description :str= Form(...),competences :str= Form(...),type_poste :str = Form(...),horaire :str= Form(...), avantages :str= Form(...),lieu:str=Form(...)):
    user=request.session.get("user",None) 
    if user: 
    

        sql =""" 
            UPDATE Recrunova.Recrut.offres
            SET titre =%s,langue=%s,salaire=%s,description=%s,competences=%s,type_poste=%s,horaire=%s,avantages=%s,lieu=%s
            WHERE offre_id=%s;
            """  
        params=[titre,langue,salaire,description,competences,type_poste,horaire,avantages,lieu,offre_id]
        cursor.execute(sql,params)
       
      
        return RedirectResponse(url=f"/ListOffre/{user['user_id']}",status_code=302)

    return templates.TemplateResponse("home.html",{"request":request})


@app.get("/deleteOffre/{id}")
async def deleteOffre(request:Request,id:str):
    user=request.session.get("user",None) 
    if user:
    
        print("delete")
        sql ="""
        DELETE  FROM Recrunova.Recrut.offres
        WHERE offre_id=%s;
        """ 
 
        params=[id]
        cursor.execute(sql,params)
      
        return RedirectResponse(url=f"/ListOffre/{user['user_id']}",status_code=302)
        

    return templates.TemplateResponse("home.html",{"request":request})






@app.get("/profile")

async def profile(request:Request):
    user=request.session.get("user",None) 
     
    if user:
         

        return templates.TemplateResponse("profile.html",{"request":request,"username":user})
    return templates.TemplateResponse("home.html",{"request":request})

@app.post("/updatepassword")

async def updatepassword(request:Request,password1:str=Form(...),password2:str=Form(...)):
    user=request.session.get("user",None)  
    if user:
        x= password_verify(password1,user['password'])
        print(x)

        if not password1 or not password2  :
                message="veuillez remplir tout les champs svp"
                return templates.TemplateResponse("profile.html",{"request":request,"message":message,"username":user})
        elif x!=True:
                message="ancien mot de passe non valide "
                return templates.TemplateResponse("profile.html",{"request":request,"message":message,"username":user})
        elif x==True:
             sql =""" 
            UPDATE Recrunova.Recrut.users
            SET password=%s
            WHERE user_id=%s;
            """  
        params=[user["user_id"]]
        cursor.execute(sql,params)
        message="le mot de passe a ete change "

         

        return templates.TemplateResponse("profile.html",{"request":request,"username":user,"message":message})
    return templates.TemplateResponse("home.html",{"request":request})

@app.post("/updateprofile")

async def updatepassword(request:Request,nom:str=Form(...),prenom:str=Form(...),tel:str=Form(...)):
    user=request.session.get("user",None)  
    if user:
      
        if not nom or not prenom or not tel  :
                message="veuillez remplir tout les champs svp"
                return templates.TemplateResponse("profile.html",{"request":request,"message1":message,"username":user})
       
        else:
             sql =""" 
            UPDATE Recrunova.Recrut.users
            SET nom=%s,prenom=%s,tel=%s
            WHERE user_id=%s;
            """  
        params=[nom,prenom,tel,user["user_id"]]
        # cursor.execute(sql,params)
        message="le changement effectuer "

         

        return templates.TemplateResponse("profile.html",{"request":request,"username":user,"message1":message})
    return templates.TemplateResponse("home.html",{"request":request})



    


@app.get("/logout")
async def logout(request:Request):
    response =RedirectResponse(url='/login')
    request.session.clear()
    return response











if __name__=="__main__":
    uvicorn.run(app,host='0.0.0.0', port=8002, workers=1)