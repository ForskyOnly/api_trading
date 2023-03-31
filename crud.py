from fastapi import FastAPI, HTTPException, Request, Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import crud
from jose import jwt
import hashlib
from datetime import datetime, timedelta
import sqlite3




connexion = sqlite3.connect('api_trad.db')
curseur = connexion.cursor()

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

################################################################## USER ########################################################################


def creer_utilisateur(pseudo:str, email:str, mdp:str, jwt:str) -> int:
    """ 
        Cette fonction prend en entrée le pseudo, l'email, le mot de passe et le jeton JWT d'un 
        utilisateur et crée un nouvel enregistrement dans la table "user" de la base de données 
        "api_trad.db". Elle renvoie l'ID de l'utilisateur créé.
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("INSERT INTO user VALUES (NULL, ?, ?, ?, ?)", (pseudo, email, mdp, jwt))
    id_user = curseur.lastrowid
    connexion.commit()
    return id_user  


def suivre_utilisateur(suiveur_email: str, suivi_email: str):
    """
        Cette fonction prend en entrée les adresses e-mail d'un utilisateur qui veut suivre un autre
        utilisateur.Elle vérifie que les adresses e-mail sont valides et que les utilisateurs existent
        dans la table "user" de la base de données "api_trad.db". Si c'est le cas, elle crée un nouvel
        enregistrement dans la table "asso_user_user" de la base de données qui relie les deux 
        utilisateurs (le suiveur et le suivi).
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    suiveur = curseur.execute("SELECT id FROM user WHERE email = ?", (suiveur_email,)).fetchone()
    suivi = curseur.execute("SELECT id FROM user WHERE email = ?", (suivi_email,)).fetchone()
    if not suiveur or not suivi:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    asso_exists = curseur.execute("SELECT COUNT(*) FROM asso_user_user WHERE suiveur_id = ? AND suivi_id = ?",
                              (suiveur[0], suivi[0])).fetchone()
    if asso_exists[0] > 0:
        raise HTTPException(status_code=400, detail="L'utilisateur suit déjà cet utilisateur")
    curseur.execute("INSERT INTO asso_user_user (suiveur_id, suivi_id) VALUES (?, ?)", (suiveur[0], suivi[0]))
    connexion.commit()

     
def arreter_de_suivre_utilisateur(suiveur_id: int, suivi_email: str):
    """ 
        Cette fonction prend en entrée l'ID d'un utilisateur qui veut arrêter de suivre un autre utilisateur,
        ainsi que l'adresse e-mail de l'utilisateur suivi. Elle vérifie que l'utilisateur suiveur existe et 
        que l'utilisateur suivi est présent dans la table "user" de la base de données. Si c'est le cas, elle
        supprime l'enregistrement correspondant dans la table "asso_user_user" de la base de données.
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    suiveur_exists = curseur.execute("SELECT COUNT(*) FROM user WHERE id = ?", (suiveur_id,)).fetchone()[0]
    if not suiveur_exists:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    suivi = curseur.execute("SELECT id FROM user WHERE email = ?", (suivi_email,)).fetchone()
    if not suivi:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    curseur.execute("DELETE FROM asso_user_user WHERE suiveur_id = ? AND suivi_id = ?", (suiveur_id, suivi[0]))
    connexion.commit()
        

def modifier_utilisateur(id:int, pseudo:str, email:str, mdp:str)-> None:
    """
        Cette fonction prend en entrée l'ID d'un utilisateur ainsi que le nouveau pseudo, l'email et le mot de 
        passe associés. Elle met à jour l'enregistrement correspondant dans la table "user" de la base de données.
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("UPDATE user SET pseudo=?, email=?, mdp=? WHERE id=?", (pseudo, email, mdp, id))
    connexion.commit()


def supprimer_utilisateur(id:int)-> None:
    """ 
        Cette fonction prend en entrée l'ID d'un utilisateur et supprime l'enregistrement correspondant dans la table
        "user" de la base de données.
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("DELETE FROM user WHERE id=?", (id,))
    connexion.commit()
    

def get_users_by_mail(mail:str):
    """ 
        Cette fonction prend en entrée une adresse e-mail et renvoie une liste de tuples contenant les informations de tous 
        les utilisateurs ayant cette adresse e-mail dans la table "user" de la base de données.
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute(" SELECT * FROM user WHERE email=?", (mail,))
    resultat = curseur.fetchall()
    connexion.close()
    return resultat

############################################################ ACTIONS #########################################################################
        
def ajout_action(nom:str, prix:float, entreprise:str)->None:
    """
        Cette fonction prend en entrée le nom, le prix et l'entreprise d'une action et crée un nouvel enregistrement dans la table 
        "action" de la base de données "api_trad.db".
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("INSERT INTO action(nom, prix, entreprise) VALUES (?, ?, ?)", (nom,prix,entreprise))
    connexion.commit()
    

def asocier_user_action(user_id:int, action_id:int)-> None:
    """ 
        Cette fonction prend en entrée l'ID d'un utilisateur et l'ID d'une action, et crée un nouvel enregistrement dans la table 
        "asso_user_action" de la base de données qui lie l'utilisateur à l'action.
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("INSERT INTO asso_user_action(user_id,action_id) VALUES (?, ?)", (user_id, action_id))
    connexion.commit()
    
    
def placer_ordre_achat(connexion, user_id, action_id, date_achat, prix_achat):
    """ 
        Cette fonction prend en entrée une connexion à la base de données, l'ID d'un utilisateur, l'ID d'une action, la date d'achat
        et le prix d'achat de cette action. Elle crée un nouvel enregistrement dans la table "asso_user_action" de la base de données,
        correspondant à un ordre d'achat.
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("INSERT INTO asso_user_action (user_id, action_id, date_achat, prix_achat) VALUES (?, ?, ?, ?)", (user_id, action_id, date_achat, prix_achat))
    connexion.commit()

def placer_ordre_vente(connexion, user_id, action_id, date_vente, prix_vente):
    """
        Cette fonction prend en entrée une connexion à la base de données, l'ID d'un utilisateur, l'ID d'une action, la date de vente
        et le prix de vente de cette action. Elle met à jour l'enregistrement correspondant dans la table "asso_user_action" de la base
        de données, correspondant à l'ordre d'achat de l'utilisateur et de l'action donnés, en y ajoutant la date de vente et le prix de vente.
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("SELECT * FROM asso_user_action WHERE user_id = ? AND action_id = ? AND date_vente IS NULL", (user_id, action_id))
    action = curseur.fetchone()
    if action:
        curseur.execute("""
            UPDATE asso_user_action 
            SET date_vente = ?, prix_vente = ? 
            WHERE user_id = ? AND action_id = ? AND date_vente IS NULL
            """,
            (date_vente, prix_vente, user_id, action_id))
        connexion.commit()
    else:
        print("Erreur : Aucun ordre d'achat trouvé pour cet utilisateur et cette action.")
        
        
def actions_des_suivi(suiveur_id: int):
    """
        Cette fonction prend en entrée l'ID d'un utilisateur (suiveur) et renvoie une liste de dictionnaires contenant les informations 
        sur toutes les actions suivies par cet utilisateur. Les informations incluent le pseudo de l'utilisateur qui a acheté l'action, 
        le nom de l'action, le prix d'achat et l'entreprise associée.
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("""
        SELECT user.pseudo, action.nom, action.prix, action.entreprise
        FROM asso_user_action
        INNER JOIN action ON asso_user_action.action_id = action.id
        INNER JOIN user ON asso_user_action.user_id = user.id
        WHERE asso_user_action.user_id IN 
            (SELECT suivi_id FROM asso_user_user WHERE suiveur_id = ?)
    """, (suiveur_id,))
    resultats = curseur.fetchall()
    stock_suivi = []
    for resultat in resultats:
        pseudo = resultat[0]
        nom_action = resultat[1]
        prix_action = resultat[2]
        entreprise = resultat[3]
        stock_suivi.append({"pseudo": pseudo, "action": nom_action, "prix_action": prix_action, "entreprise": entreprise})
    connexion.close()
    return stock_suivi


def lister_actions():
    """ 
        Cette fonction renvoie une liste de dictionnaires contenant les informations de toutes les actions présentes dans la table "action"
        de la base de données "api_trad.db". Les informations incluent le nom de l'action et son prix.
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("SELECT nom, prix FROM action")
    actions = curseur.fetchall()
    return [{"nom": action[0], "prix": action[1]} for action in actions]

        
def mettre_a_jour_action(id:int, nom:str, prix:float, entreprise:str)-> None:
    """ 
        Cette fonction prend en entrée l'ID d'une action ainsi que le nouveau nom, le nouveau prix et la nouvelle entreprise associés. Elle met
        à jour l'enregistrement correspondant dans la table "action" de la base de données.
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("UPDATE action SET nom=?, prix=?, entreprise=? WHERE id=?", (nom, prix, entreprise, id))
    connexion.commit()
    

def supprimer_action(id:int)-> None:
    """ 
        Cette fonction prend en entrée l'ID d'une action et la supprime de la table "action" de la base de données.
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("DELETE FROM action WHERE id=?", (id,))
    connexion.commit()


def portefeuille(user_id: int):
    """
        Cette fonction prend en entrée l'ID d'un utilisateur et renvoie un dictionnaire contenant deux clés : "actions" 
        et "capital". La clé "actions" contient une liste de tuples représentant les actions détenues par l'utilisateur 
        et leur plus-value actuelle. Si l'utilisateur n'a pas encore vendu ses actions, la plus-value est le prix actuel
        de l'action moins le prix d'achat initial. Si l'utilisateur a déjà vendu ses actions, la plus-value est le prix 
        de vente de l'action moins le prix d'achat initial. La clé "capital" contient le montant total d'argent que 
        l'utilisateur a actuellement dans son portefeuille (en prenant en compte la valeur de ses actions et de ses ventes).
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("""
        SELECT 
            asso_user_action.date_achat, 
            action.nom, 
            asso_user_action.prix_achat, 
            asso_user_action.date_vente, 
            asso_user_action.prix_vente 
        FROM asso_user_action 
        INNER JOIN action ON asso_user_action.action_id = action.id 
        WHERE asso_user_action.user_id = ?
    """, (user_id,))
    resultats = curseur.fetchall()
    portefeuille = []
    capital = 0
    for resultat in resultats:
        date_achat = resultat[0]
        nom = resultat[1]
        prix_achat = resultat[2]
        date_vente = resultat[3]
        prix_vente = resultat[4]
        if date_vente is None:
            portefeuille.append((nom, prix_achat))
            capital += prix_achat
        else:
            plus_value = prix_vente - prix_achat
            portefeuille.append((nom, plus_value))
            capital += prix_vente
    return {"actions": portefeuille, "capital": capital}


def actions_suivis(suiveur_id: int):
    """
        Cette fonction prend en entrée l'ID d'un utilisateur suiveur et renvoie la liste des actions achetées par les utilisateurs qu'il
        suit,        avec le nom de l'action, son prix et le pseudo de l'utilisateur qui l'a achetée. Elle effectue une jointure entre les
        tables "asso_user_action", "action" et "user" de la base de données "api_trad.db", pour récupérer les informations nécessaires. 
        Elle renvoie une liste de dictionnaires, où chaque dictionnaire correspond à une action achetée par un utilisateur suivi, avec les
        clés "nom_action", "prix_action" et "pseudo_user".
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("""
        SELECT action.nom, action.prix, user.pseudo
        FROM asso_user_action
        INNER JOIN action ON asso_user_action.action_id = action.id
        INNER JOIN user ON asso_user_action.user_id = user.id
        WHERE asso_user_action.user_id IN 
            (SELECT suivi_id FROM asso_user_user WHERE suiveur_id = ?)
    """, (suiveur_id,))
    resultats = curseur.fetchall()
    actions_suivis_list = []
    for resultat in resultats:
        nom_action = resultat[0]
        prix_action = resultat[1]
        pseudo_user = resultat[2]
        actions_suivis_list.append({"nom_action": nom_action, "prix_action": prix_action, "pseudo_user": pseudo_user})
    connexion.close()
    return actions_suivis_list
            
    
def action_par_user_id(user_id:int):
    """ 
        Cette fonction prend en entrée l'ID d'un utilisateur et renvoie la liste des ID des actions qu'il a achetées, en effectuant une requête 
        SQL sur la table "asso_user_action" de la base de données "api_trad.db". Elle renvoie une liste de tuples, où chaque tuple contient un 
        seul élément (l'ID de l'action).
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute(" SELECT action_id FROM asso_user_action WHERE user_id=?", (user_id,))
    resultat = curseur.fetchall()
    connexion.close()
    return resultat


############################################################################## VERIF & RECHERCHE ###########################################################

def obtenir_jwt_depuis_email_mdp(email:str, mdp:str):
    """
        Cette fonction prend en entrée une adresse e-mail et un mot de passe d'un utilisateur, recherche l'utilisateur correspondant dans la base 
        de données "api_trad.db" et renvoie le jeton JWT (JSON Web Token) de l'utilisateur s'il existe, sinon elle renvoie None.
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("SELECT jwt FROM user WHERE email=? AND mdp=?", (email, mdp))
    resultat = curseur.fetchone()
    connexion.close()
    return resultat


def update_token(id, token:str)->None:
    """
        Cette fonction prend en entrée l'ID d'un utilisateur et un nouveau jeton JWT et met à jour l'enregistrement correspondant dans la table "user"
        de la base de données "api_trad.db". 
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("UPDATE user SET jwt = ? WHERE id=?",(token, id))
    connexion.commit()
    connexion.close()
    
def verif_validite_jwt(token: str, secret_key: str, algorithm: str):
    """
        Cette fonction prend en entrée un jeton JWT, une clé secrète et un algorithme de hachage et vérifie la validité du jeton. Si le jeton est valide,
        elle renvoie un dictionnaire contenant les informations du payload du jeton, sinon elle renvoie None. 
    """
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=[algorithm])
        return decoded_token
    except JWTError:
        return None
    

def user_id_par_mail_jwt(email=None, jwt=None):
    """
        Cette fonction prend en entrée soit l'adresse e-mail, soit le jeton JWT d'un utilisateur et renvoie l'ID de l'utilisateur correspondant dans la 
        table "user" de la base de données "api_trad.db", ou None s'il n'existe pas.
    """
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    if email:
        curseur.execute("SELECT id FROM user WHERE email=?", (email,))
    elif jwt:
        curseur.execute("SELECT id FROM user WHERE jwt=?", (jwt,))
    row = curseur.fetchone()
    connexion.close()
    if row:
        return row[0]
    else:
        return None
