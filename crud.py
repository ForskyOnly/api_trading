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


def lister_actions():
    with sqlite3.connect("api_trad.db") as connexion:
        curseur = connexion.cursor()
        curseur.execute("SELECT nom, prix FROM action")
        actions = curseur.fetchall()
        for action in actions:
            print(f"{action[0]} - {action[1]}€")
            
            
def portefeuille(user_id: int):
    with sqlite3.connect("api_trad.db") as connexion:
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

def follow_user(email:str, suiveur_id:int)->None:
    with sqlite3.connect("api_trad.db") as connexion:
        curseur = connexion.cursor()
        curseur.execute("SELECT id FROM user WHERE email=?", (email,))
        suivi_id = curseur.fetchone()[0]
        curseur.execute("INSERT INTO asso_user_user(suiveur_id, suivi_id) VALUES (?, ?)", (suiveur_id, suivi_id))
        connexion.commit()
        

def actions_suivis(suiveur_id:int):
    with sqlite3.connect("api_trad.db") as connexion:
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
            pseudo_utilisateur = resultat[2]
            print(f"{nom_action} - {prix_action}€ (acheté par {pseudo_utilisateur})")
