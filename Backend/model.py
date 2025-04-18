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
<<<<<<< HEAD


class User(BaseModel):

    nom :str
    prenom :str
    nom_entreprise:str
    role :str
    password :str
    Tel :str
    date_inscription:str
    Email :str
=======
>>>>>>> 4cacb13ca4892eabf7fa0fefb5834634cda64252
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