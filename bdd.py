import sqlite3

connexion = sqlite3.connect("api_trad.db")
curseur = connexion.cursor()


curseur.execute("""
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pseudo TEXT NOT NULL,
                    email TEXT NOT NULL,
                    mdp TEXT NOT NULL
                )
                """)


curseur.execute("""
                CREATE TABLE IF NOT EXISTS asso_user_user (
                    suiveur_id INTEGER,
                    suivi_id INTEGER,
                    FOREIGN KEY(suiveur_id) REFERENCES user(id),
                    FOREIGN KEY(suivi_id) REFERENCES user(id)
                )
                """)

curseur.execute("""
                CREATE TABLE IF NOT EXISTS action (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prix FLOAT NOT NULL,
                    entreprise_id INTEGER NOT NULL,
                    FOREIGN KEY(entreprise_id) REFERENCES entreprise(id)
                )
                """)


curseur.execute("""
                CREATE TABLE IF NOT EXISTS asso_user_action(
                    user_id INTEGER,
                    action_id INTEGER,
                    date_achat DATE NOT NULL,
                    date_vente DATE NOT NULL,
                    prix_achat FLOAT NOT NULL,
                    prix_vente FLOAT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES groupe(id),
                    FOREIGN KEY(action_id) REFERENCES action(id)
                )
                """)

curseur.execute("""
                CREATE TABLE IF NOT EXISTS entreprise (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL
                )
                """)

connexion.commit()

connexion.close()