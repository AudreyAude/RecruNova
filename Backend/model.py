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