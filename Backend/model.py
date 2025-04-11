from pydantic import BaseModel


class User(BaseModel):

    nom :str
    prenom :str
    nom_entreprise:str
    role :str
    password :str
    Tel :str
    date_inscription:str
    Email :str
    # Cv 


class log(BaseModel):
    Email :str
    password :str

class offre(BaseModel):
    titre :str
    langue :str
    salaire :str
    description :str
    competences :str
    type_poste :str
    horaire :str
    avantages :str