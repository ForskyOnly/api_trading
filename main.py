from fastapi import FastAPI, HTTPException, Request
from jose import jwt
from pydantic import BaseModel
import crud
from jose import jwt
import hashlib
import sqlite3



#########################################################################################################################################################################
                                                               # CLASSES 
#########################################################################################################################################################################


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
    


#########################################################################################################################################################################
                                                               # VARIABLE ET CONSTANTE 
#########################################################################################################################################################################


app = FastAPI()
connexion = sqlite3.connect('api_trad.db')
curseur = connexion.cursor()
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


#########################################################################################################################################################################
                                                               # FONCTIONS ENCODGE TOKEN
#########################################################################################################################################################################



def hasher_mdp(mdp:str) -> str:
    """ 
        Cette fonction prend en entrée un mot de passe sous forme de chaîne de caractères et renvoie une version hashée de ce mot de passe. 
        Elle utilise la fonction de hachage SHA-256 de la bibliothèque hashlib.
    """
    return hashlib.sha256(mdp.encode()).hexdigest()

def decoder_token(token:str)->dict:
    """ 
        Cette fonction prend en entrée un jeton d'authentification sous forme de chaîne de caractères et renvoie un dictionnaire contenant 
        les informations encodées dans le jeton. Elle utilise la clé secrète et l'algorithme définis dans les variables globales SECRET_KEY 
        et ALGORITHM.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

def verifier_token(req: Request):
    """ 
        Cette fonction prend en entrée une requête HTTP Flask dans un objet de type Request. Elle vérifie la présence d'un jeton d'authentification
        dans l'en-tête "Authorization" de la requête et valide ce jeton en utilisant la fonction decoder_token(). Si le jeton est valide, elle 
        renvoie un dictionnaire contenant les informations encodées dans le jeton, sinon elle renvoie None.
    """
    token = req.headers["Authorization"]
    

#########################################################################################################################################################################
                                                               # AUTHENTIFICATION/INSCRIPTION 
#########################################################################################################################################################################

@app.post("/auth/inscription")
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
    
#########################################################################################################################################################################
                                                               # UTILISATEUR
#########################################################################################################################################################################

@app.post("/utilisateur/suivre_utilisateur")
async def suivre_utilisateur(req: Request, follow: Follow):
    try:
        decode = decoder_token(req.headers["Authorization"])
        crud.suivre_utilisateur(decode["email"], follow.email_suivi)
        return {"message": f"L'utilisateur {follow.email_suivi} a été suivi avec succès."}
    except:
        raise HTTPException(status_code=401, detail="Vous suivez déjà cet utilisateur.")
    
    
@app.delete("/utilisateur/arreter_de_suivre_utilisateur")
async def arreter_de_suivre_utilisateur(req: Request, follow: Follow):
    try:
        decode = decoder_token(req.headers["Authorization"])
        crud.arreter_de_suivre_utilisateur(decode["id"], follow.email_suivi)
        return {"message": "L'utilisateur n'est plus suivi."}
    except:
        raise HTTPException(status_code=401, detail="Vous devez être identifié pour accéder à cet endpoint.")
    

@app.put("/utilisateur/mettre_a_jour_utilisateur/{id}")
async def modifier_utilisateur_route(id: int, utilisateur: User) -> None:
    crud.modifier_utilisateur(id, utilisateur.pseudo, utilisateur.email, utilisateur.mdp)
    return {"detail": "Utilisateur mis à jour avec succès"}


@app.get("/utilisateur/portefeuille/{user_id}")
async def portefeuille_route(user_id: int) -> dict:
    portefeuille_data = crud.portefeuille(user_id)
    return {"portefeuille": portefeuille_data}


#########################################################################################################################################################################
                                                               # ACTIONS ET MANIPULATIONS D'ACTIONS
#########################################################################################################################################################################

@app.post("/actions/asocier_user_action/{user_id}/{action_id}")
async def asocier_user_action_route(user_id: int, action_id: int) -> None:
    crud.asocier_user_action(user_id, action_id)
    return {"detail": "Action associée à l'utilisateur avec succès"}


@app.post("/actions/placer_ordre_achat/")
async def placer_ordre_achat_route(ordre_achat: OrdreAchat) -> None:
    crud.placer_ordre_achat(connexion, ordre_achat.user_id, ordre_achat.action_id, ordre_achat.date_achat, ordre_achat.prix_achat)
    return {"detail": "Ordre d'achat placé avec succès"}


@app.post("/actions/placer_ordre_vente/")
async def placer_ordre_vente_route(ordre_vente: OrdreVente) -> None:
    crud.placer_ordre_vente(connexion, ordre_vente.user_id, ordre_vente.action_id, ordre_vente.date_vente, ordre_vente.prix_vente)
    return {"detail": "Ordre de vente placé avec succès"}


@app.get("/actions/lister_actions/")
async def lister_actions_route() -> list:
    actions = crud.lister_actions()
    return actions


@app.get("/actions/actions_suivis/{suiveur_id}")
async def actions_suivis_route(suiveur_id: int) -> dict:
    actions_suivis_list = crud.actions_suivis(suiveur_id)
    return {"actions_suivis": actions_suivis_list}


@app.get("/actions/mes_actions")
async def mes_actions(req: Request):
    try:
        decode = decoder_token(req.headers["Authorization"])
        print(decode)
        return {"action_id" : crud.action_par_user_id(decode["id"])[0]}
    except:
        raise HTTPException(status_code=401, detail="Vous devez être identifiés pour accéder à cet endpoint")
    
    
@app.get("/actions/actions_utilisateurs_suivi/{suiveur_id}")
async def actions_des_suivi_route(suiveur_id: int) -> dict:
    stock_suivi = crud.actions_des_suivi(suiveur_id)
    return {"stocks_followed": stock_suivi}

#########################################################################################################################################################################
                                                               # FONCTIONS ADMINS
#########################################################################################################################################################################


# @app.delete("/utilisateur/supprimer/{id}")
# async def supprimer_utilisateur_route(id: int) -> dict:
#     crud.supprimer_utilisateur(id)
#     return {"message": "Utilisateur supprimé avec succès"}
    
    
# @app.put("/actions/mettre_a_jour_action/{action_id}")
# async def mettre_a_jour_action_route(action_id: int, action: Action) -> None:
#     crud.mettre_a_jour_action(action_id, action.nom, action.prix, action.entreprise)
#     return {"detail": "Action mise à jour avec succès"}


# @app.delete("/actions/supprimer_action/{action_id}")
# async def supprimer_action_route(action_id: int) -> None:
#     crud.supprimer_action(action_id)
#     return {"detail": f"L'action {action_id} a été supprimée avec succès."}


# @app.post("/actions/ajout_action/")
# async def ajout_action_route(action: Action) -> None:
#     crud.ajout_action(action.nom, action.prix, action.entreprise)
#     return {"detail": "Action ajoutée avec succès"}

# @app.post("/auth/jwt")
# async def connexion(user:UserLogin):
#     jwt_token = crud.obtenir_jwt_depuis_email_mdp(user.email, hasher_mdp(user.mdp))
#     if jwt_token is None:
#         raise HTTPException(status_code=401, detail="Identifiants invalides")
#     else:
#         return {"token": jwt_token[0]}
    
    
# @app.get("/auth/verification_token")
# async def verifier_token_route(request: Request):
#     token = request.headers.get("Authorization", None)
#     if not token:
#         raise HTTPException(status_code=401, detail="Jeton d'authentification manquant")
#     decoded_token = crud.verif_validite_jwt(token, SECRET_KEY, ALGORITHM)
#     if decoded_token:
#         return decoded_token
#     else:
#         raise HTTPException(status_code=401, detail="Jeton d'authentification invalide")