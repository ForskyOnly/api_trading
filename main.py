from fastapi import FastAPI, HTTPException, Request, Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import crud
from jose import jwt
import hashlib
from datetime import datetime, timedelta
import sqlite3


########################################################### CLASES #########################################################################
class SuivreUtilisateur(BaseModel):
    email: str
    suiveur_id: int
    
class User(BaseModel):
    pseudo: str
    email: str
    mdp: str
    jwt: str

class UserRegister(BaseModel):
    pseudo : str
    email: str
    mdp: str
    
class UserLogin(BaseModel):
    email: str
    mdp: str

class Action(BaseModel):
    nom: str
    prix: float
    entreprise: str
    
class OrdreAchat(BaseModel):
    user_id: int
    action_id: int
    date_achat: str
    prix_achat: float
    
class OrdreVente(BaseModel):
    user_id: int
    action_id: int
    date_vente: str
    prix_vente: float
    
class Follow(BaseModel):
    email_suivi: str
    

######################################################## VARIABLE ET CONSTANTE ###########################################################

app = FastAPI()
connexion = sqlite3.connect('api_trad.db')
curseur = connexion.cursor()
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

###################################################### FONCTIONS ENCODGE TOKEN ###########################################################
def hasher_mdp(mdp:str) -> str:
    return hashlib.sha256(mdp.encode()).hexdigest()

def decoder_token(token:str)->dict:
    return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

def verifier_token(req: Request):
    token = req.headers["Authorization"]
    

#####################################################   AUTHENTIFICATION INSCRIPTION ##############################################
@app.post("/api/auth/inscription")
async def inscription(user:UserRegister):
    if len(crud.get_users_by_mail(user.email)) > 0:
        raise HTTPException(status_code=403, detail="L'email fourni possède déjà un compte")
    else:
        id_user = crud.creer_utilisateur(user.pseudo, user.email, hasher_mdp(user.mdp), None)
        token = jwt.encode({
            "email" : user.email,
            "mdp" : user.mdp,
            "id" : id_user
        }, SECRET_KEY, algorithm=ALGORITHM)
        crud.update_token(id_user, token)
        return {"token" : token}
    

################################################# USER ##############################################################################

@app.post("/suivre_utilisateur")
async def suivre_utilisateur(req: Request, follow: Follow):
    try:
        decode = decoder_token(req.headers["Authorization"])
        crud.suivre_utilisateur(decode["email"], follow.email_suivi)
        return {"message": f"L'utilisateur {follow.email_suivi} a été suivi avec succès."}
    except:
        raise HTTPException(status_code=401, detail="L'utilisateur suit déjà cet utilisateur.")
    
@app.delete("/arreter_de_suivre_utilisateur")
async def arreter_de_suivre_utilisateur(req: Request, follow: Follow):
    try:
        decode = decoder_token(req.headers["Authorization"])
        crud.arreter_de_suivre_utilisateur(decode["id"], follow.email_suivi)
        return {"message": "L'utilisateur n'est plus suivi."}
    except:
        raise HTTPException(status_code=401, detail="Vous devez être identifié pour accéder à cet endpoint.")

@app.put("/mettre_a_jour_utilisateur/{id}")
async def modifier_utilisateur_route(id: int, utilisateur: User) -> None:
    crud.modifier_utilisateur(id, utilisateur.pseudo, utilisateur.email, utilisateur.mdp)
    return {"detail": "Utilisateur mis à jour avec succès"}


@app.get("/portefeuille/{user_id}")
async def portefeuille_route(user_id: int) -> dict:
    portefeuille_data = crud.portefeuille(user_id)
    return {"portefeuille": portefeuille_data}


####################################################### ACTIONS ###################################################################


@app.post("/asocier_user_action/{user_id}/{action_id}")
async def asocier_user_action_route(user_id: int, action_id: int) -> None:
    crud.asocier_user_action(user_id, action_id)
    return {"detail": "Action associée à l'utilisateur avec succès"}

@app.post("/placer_ordre_achat/")
async def placer_ordre_achat_route(ordre_achat: OrdreAchat) -> None:
    crud.placer_ordre_achat(connexion, ordre_achat.user_id, ordre_achat.action_id, ordre_achat.date_achat, ordre_achat.prix_achat)
    return {"detail": "Ordre d'achat placé avec succès"}

@app.post("/placer_ordre_vente/")
async def placer_ordre_vente_route(ordre_vente: OrdreVente) -> None:
    crud.placer_ordre_vente(connexion, ordre_vente.user_id, ordre_vente.action_id, ordre_vente.date_vente, ordre_vente.prix_vente)
    return {"detail": "Ordre de vente placé avec succès"}

@app.get("/lister_actions/")
async def lister_actions_route() -> list:
    actions = crud.lister_actions()
    return actions

@app.get("/portefeuille/{user_id}")
async def portefeuille_route(user_id: int) -> dict:
    portefeuille = portefeuille(user_id)
    return {"portefeuille": portefeuille}

@app.get("/actions_suivis/{suiveur_id}")
async def actions_suivis_route(suiveur_id: int) -> dict:
    actions_suivis_list = crud.actions_suivis(suiveur_id)
    return {"actions_suivis": actions_suivis_list}

@app.get("/api/mes_actions")
async def mes_actions(req: Request):
    try:
        decode = decoder_token(req.headers["Authorization"])
        noms_actions = [action[0] for action in crud.get_action_by_user_id(decode["id"])]
        return {"noms_actions" : noms_actions}
    except:
        raise HTTPException(status_code=401, detail="Vous devez être identifiés pour accéder à cet endpoint")
    
@app.get("/actions_utilisateurs_suivi/{suivi_id}")
async def actions_des_suivi_route(suivi_id: int) -> dict:
    stock_suivi = crud.actions_des_suivi(suivi_id)
    return {"stocks_followed": stock_suivi}
