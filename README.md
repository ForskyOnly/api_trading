
# API de trading

Version 1.0

## Description du Projet

Ce projet a été réalisé lors de la formation Dev IA Microsoft by Simplon HDF.

L'objectif : crée un API de trading en utilisant FastApi, en utilisant Python et SQL.

### Contexte du projet

Le client, GreenAnt souhaite créer un outil de trading social.

​

Le trading social est une forme de négociation qui permet aux traders ou aux investisseurs de copier et d’exécuter les stratégies de leurs pairs ou de traders plus expérimentés. Si la plupart des traders réalisent leurs propres analyses fondamentale et technique, certains préfèrent observer et répliquer les analyses des autres.

​

**GreenAnt souhaite les fonctionnalités suivantes dans son MVP:**

- Un système pour s'incrire et connecter (Via des jetons JWT)
- Voir la liste des actions disponibles.
- Voir son portefeuille d'actions (plus la valeur de notre capital)
- Placer un ordre d'achat
- Placer un ordre de vente
- Possibilité de suivre un utilisateur (On le trouve via son email)
- Possibilité de voir les actions des personnes que l'on suit.

## Organisation du dossier

- crud.py : regroupe  les fonctions nécessaire pour l'utilisation de l'API,
- main.py : regroupe les fonctions disponible à l'utilisation via l'interface de l'API,
- bdd.py : creation et structure de la base de donnée,
- api_trad.db : Base de donée.

## Auteurs

- [Agathe Becquart](https://github.com/AgatheBecquart)
- [Rubic](https://github.com/Forskyonly)

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Installation

Installer depuis un terminal:

 ```bash
  git clone git@github.com:ForskyOnly/api_trading.git

```

- Télécharger le depuis [le depot GIT](https://github.com/ForskyOnly/api_trading)

### Utilisation

Importer et/ou installer les modules suivantes:

- FastAPI, HTTPException, Request, Depends
- JWTError, JWT
- CryptContext
- BaseModel
- Hashlib
- Datetime, timedelta
- sqlite3

Lancer le serveur depuis un terminal avec la commande :

```bash
  uvicorn main:app --reload

```

Entrez  <http://127.0.0.1:8000/docs#/>  dans votre navigateur pour acceder à l'interface de l'API.
