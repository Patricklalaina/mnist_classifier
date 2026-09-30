# Déploiement Render Free

Ce projet se déploie avec **2 services gratuits Render** :

- `mnist-api` : Web Service Docker (FastAPI + TensorFlow)
- `mnist-web` : Static Site (React/Vite)

## 1. API

Dans Render : **New → Web Service**.

- Repository : le dépôt GitHub du projet
- Root Directory : laisser vide (racine du dépôt)
- Language : **Docker**
- Dockerfile Path : `./Dockerfile.render`
- Docker Context : `.`
- Plan : **Free**
- Health Check Path : `/health`

Après création, attendre le déploiement et copier l'URL publique de l'API, par exemple :
`https://mnist-api-xxxx.onrender.com`

Ajouter la variable d'environnement :

`ALLOWED_ORIGINS=https://mnist-web-xxxx.onrender.com`

(Remplacer par l'URL réelle du frontend après sa création.)

## 2. Frontend

Dans Render : **New → Static Site**.

- Repository : le même dépôt GitHub
- Root Directory : `frontend`
- Build Command : `npm ci && npm run build`
- Publish Directory : `dist`

Ajouter avant le build :

`VITE_API_BASE=https://mnist-api-xxxx.onrender.com`

Puis déployer.

## 3. Une fois le frontend créé

Mettre son URL réelle dans `ALLOWED_ORIGINS` du service API, puis redéployer l'API.

## Important

Le service API gratuit peut se mettre en veille après 15 minutes sans trafic et le premier appel suivant peut donc être lent. Le système de fichiers d'un service Free Render est éphémère, mais ce projet n'a pas besoin d'écrire le modèle au runtime : `models/` est embarqué dans l'image Docker.
