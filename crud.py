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
        connexion = sqlite3.connect("api_trad.db")
        curseur = connexion.cursor()
        curseur.execute("INSERT INTO user VALUES (NULL, ?, ?, ?, ?)", (pseudo, email, mdp, jwt))
        id_user = curseur.lastrowid
        connexion.commit()
        return id_user  

def suivre_utilisateur(suiveur_email: str, suivi_email: str):
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    suiveur = curseur.execute("SELECT id FROM user WHERE email = ?", (suiveur_email,)).fetchone()
    suivi = curseur.execute("SELECT id FROM user WHERE email = ?", (suivi_email,)).fetchone()

    # Vérifier que les deux utilisateurs existent
    if not suiveur or not suivi:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # Vérifier que l'utilisateur suiveur ne suit pas déjà l'utilisateur suivi
    asso_exists = curseur.execute("SELECT COUNT(*) FROM asso_user_user WHERE suiveur_id = ? AND suivi_id = ?",
                              (suiveur[0], suivi[0])).fetchone()
    if asso_exists[0] > 0:
        raise HTTPException(status_code=400, detail="L'utilisateur suit déjà cet utilisateur")

    # Ajouter une entrée dans la table d'association
    curseur.execute("INSERT INTO asso_user_user (suiveur_id, suivi_id) VALUES (?, ?)", (suiveur[0], suivi[0]))
    connexion.commit()

def arreter_de_suivre_utilisateur(suiveur_id: int, suivi_email: str):
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()

    # Vérifier que l'utilisateur suiveur existe
    suiveur_exists = curseur.execute("SELECT COUNT(*) FROM user WHERE id = ?", (suiveur_id,)).fetchone()[0]
    if not suiveur_exists:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # Récupérer l'ID de l'utilisateur suivi à partir de son e-mail
    suivi = curseur.execute("SELECT id FROM user WHERE email = ?", (suivi_email,)).fetchone()
    if not suivi:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # Supprimer l'entrée correspondante dans la table d'association
    curseur.execute("DELETE FROM asso_user_user WHERE suiveur_id = ? AND suivi_id = ?", (suiveur_id, suivi[0]))
    connexion.commit()

def modifier_utilisateur(id:int, pseudo:str, email:str, mdp:str)-> None:
        connexion = sqlite3.connect("api_trad.db")
        curseur = connexion.cursor()
        curseur.execute("UPDATE user SET pseudo=?, email=?, mdp=? WHERE id=?", (pseudo, email, mdp, id))
        connexion.commit()

def supprimer_utilisateur(id:int)-> None:
        connexion = sqlite3.connect("api_trad.db")
        curseur = connexion.cursor()
        curseur.execute("DELETE FROM user WHERE id=?", (id,))
        connexion.commit()
    
    
def get_users_by_mail(mail:str):
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute(" SELECT * FROM user WHERE email=?", (mail,))
    resultat = curseur.fetchall()
    connexion.close()
    return resultat

############################################################ ACTIONS #########################################################################
        
def ajout_action(nom:str, prix:float, entreprise:str)->None:
        connexion = sqlite3.connect("api_trad.db")
        curseur = connexion.cursor()
        curseur.execute("INSERT INTO action(nom, prix, entreprise) VALUES (?, ?, ?)", (nom,prix,entreprise))
        connexion.commit()
        


def asocier_user_action(user_id:int, action_id:int)-> None:
        connexion = sqlite3.connect("api_trad.db")
        curseur = connexion.cursor()
        curseur.execute("INSERT INTO asso_user_action(user_id,action_id) VALUES (?, ?)", (user_id, action_id))
        connexion.commit()
        
        
def placer_ordre_achat(user_id, action_id, date_achat, prix_achat):
    with sqlite3.connect("api_trad.db") as connexion:
        curseur = connexion.cursor()
        curseur.execute("INSERT INTO asso_user_action (user_id, action_id, date_achat, prix_achat) VALUES (?, ?, ?, ?)", (user_id, action_id, date_achat, prix_achat))
        connexion.commit()

def placer_ordre_vente(user_id, action_id, date_vente, prix_vente):
    with sqlite3.connect("api_trad.db") as connexion:
        curseur = connexion.cursor()
        curseur.execute("SELECT * FROM asso_user_action WHERE user_id = ? AND action_id = ? AND date_vente IS NULL", (user_id, action_id))
        action = curseur.fetchone()
        if action:
            curseur.execute("UPDATE asso_user_action SET date_vente = ?, prix_vente = ? WHERE user_id = ? AND action_id = ? AND date_vente IS NULL", (date_vente, prix_vente, user_id, action_id))
            connexion.commit()
        else:
            print("Erreur : Aucun ordre d'achat trouvé pour cet utilisateur et cette action.")


def lister_actions():
        connexion = sqlite3.connect("api_trad.db")
        curseur = connexion.cursor()
        curseur.execute("SELECT nom, prix FROM action")
        actions = curseur.fetchall()
        return [{"nom": action[0], "prix": action[1]} for action in actions]
        

def mettre_a_jour_action(id:int, nom:str, prix:float, entreprise:str)-> None:
        connexion = sqlite3.connect("api_trad.db")
        curseur = connexion.cursor()
        curseur.execute("UPDATE action SET nom=?, prix=?, entreprise=? WHERE id=?", (nom, prix, entreprise, id))
        connexion.commit()

def supprimer_action(id:int)-> None:
        connexion = sqlite3.connect("api_trad.db")
        curseur = connexion.cursor()
        curseur.execute("DELETE FROM action WHERE id=?", (id,))
        connexion.commit()

def portefeuille(user_id: int):
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
        for action in portefeuille:
            print(f"{action[0]} - {action[1]}€")
        print(f"Capital total: {capital}€")


def actions_suivis(suiveur_id:int):
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
        for resultat in resultats:
            nom_action = resultat[0]
            prix_action = resultat[1]
            pseudo_user = resultat[2]
            print(f"{nom_action} - {prix_action}€ (acheté par {pseudo_user})")
            
            
def obtenir_jwt_depuis_email_mdp(email:str, mdp:str):
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("SELECT jwt FROM user WHERE email=? AND mdp=?", (email, mdp))
    resultat = curseur.fetchone()
    connexion.close()
    return resultat


def update_token(id, token:str)->None:
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("""
                    UPDATE user
                        SET jwt = ?
                        WHERE id=?
                    """,(token, id))
    connexion.commit()
    connexion.close()
    
def get_action_by_user_id(user_id: int):
    connexion = sqlite3.connect("api_trad.db")
    curseur = connexion.cursor()
    curseur.execute("""
                    SELECT action.nom
                    FROM asso_user_action 
                    INNER JOIN action 
                    ON asso_user_action.action_id = action.id 
                    WHERE asso_user_action.user_id=?
                    """, (user_id,))
    resultat = curseur.fetchall()
    connexion.close()
    return resultat
