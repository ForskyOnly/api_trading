import sqlite3

def ajout_user(pseudo:str, email:str, mdp:str)-> None:
    with sqlite3.connect("api_trad.db") as connexion:
        curseur = connexion.cursor()
        curseur.execute("INSERT INTO user(pseudo, email, mdp) VALUES (?, ?, ?)", (pseudo, email, mdp))
        connexion.commit()        
        
                
ajout_user("user","user@user.us","user123")
        
def ajout_action(nom:str, prix:float, entreprise:str)->None:
    with sqlite3.connect("api_trad.db") as connexion:
        curseur = connexion.cursor()
        curseur.execute("INSERT INTO action(nom, prix, entreprise) VALUES (?, ?, ?)", (nom,prix,entreprise))
        connexion.commit()
        

def follow(suiveur_id:int, suivi_id:int)->None:
    with sqlite3.connect("api_trad.db") as connexion:
        curseur = connexion.cursor()
        curseur.execute("INSERT INTO asso_user_user(suiveur_id, suivi_id) VALUES (?, ?)", (suiveur_id, suivi_id))
        connexion.commit()

def asocier_user_action(user_id:int, action_id:int)-> None:
    with sqlite3.connect("api_trad.db") as connexion:
        curseur = connexion.cursor()
        curseur.execute("INSERT INTO asso_user_action(user_id,action_id) VALUES (?, ?)", (user_id, action_id))
        connexion.commit()
        
        
def placer_ordre_achat(connexion, user_id, action_id, date_achat, prix_achat):
    curseur = connexion.cursor()
    curseur.execute("INSERT INTO asso_user_action (user_id, action_id, date_achat, prix_achat) VALUES (?, ?, ?, ?)", (user_id, action_id, date_achat, prix_achat))
    connexion.commit()
    

def placer_ordre_vente(connexion, user_id, action_id, date_vente, prix_vente):
    curseur = connexion.cursor()
    curseur.execute(" UPDATE asso_user_action SET date_vente = ?, prix_vente = ?  WHERE user_id = ? AND action_id = ? AND date_vente IS NULL ", (date_vente, prix_vente, user_id, action_id))
    connexion.commit()
