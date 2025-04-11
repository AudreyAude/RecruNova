from fastapi import FastAPI,Request,Form
import uvicorn
import os,sys
import snowflake.connector as sc
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
app=FastAPI()
load_dotenv()
# app.add_middleware(SessionMiddleware,Secret_key=os.getenv("secret_key"),max_age=60)
templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"templates"))
templates=Jinja2Templates(directory=templates_dir)

#static
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"static"))
app.mount("/static",StaticFiles(directory=static_dir))


# Connect = sc.connect(
#     user= os.getenv("snowflake_user"),
#     password= os.getenv("snowflake_password"),
#     account=os.getenv("snowflake_account"),
#     database=os.getenv("snowflake_database"),
# )

@app.get("/home")
async def home_page(request:Request):
    
    return templates.TemplateResponse("home.html",{"request":request })



if __name__=="__main__":
    uvicorn.run(app,host='0.0.0.0', port=8002, workers=1)