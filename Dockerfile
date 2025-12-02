FROM python:3.11-slim

# 2️⃣ Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3️⃣ Création du répertoire de travail dans le container
WORKDIR /app

# 4️⃣ Copier le requirements.txt et installer les dépendances
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 5️⃣ Copier tout le code de l'application
COPY . .

# 6️⃣ Exposer le port sur lequel Flask va tourner
EXPOSE 5001

# 7️⃣ Commande pour lancer l'application en production
# Flask utilisera SECRET_KEY et DATABASE_URL injectés par l'environnement
CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:app"]
