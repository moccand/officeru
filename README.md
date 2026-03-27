# officeru

utilise :  
- Python 3.12.7  
- Django 6.0.3  
- Tailwind 4  
- DaisyUi 5  (pour l'IA et les IDE : https://daisyui.com/docs/editor/)
- https://heroicons.com/  

## Installation  

python -m venv .venv  
source .venv/bin/activate      # Linux/Mac  
ou .venv\Scripts\activate    # Windows  
pour powershell (par exemple dans Cursor) il peut être nécessaire de lancer : Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned  
pip install -r requirements.txt  
python manage.py runserver  


## chargement de données de test  
--Insérer les 10 voies fixes (skip si déjà présentes)  
python manage.py seed_voies  
-- Repartir de zéro et insérer les voies fixes  
python manage.py seed_voies --reset  
-- Insérer les voies fixes + 100 voies aléatoires  
python manage.py seed_voies --count 100  
-- Tout supprimer et générer 200 voies aléatoires  
python manage.py seed_voies --reset --count 200  


-- les parcelles  



-- Puis les alignements — 3 par voie par défaut  
python manage.py seed_alignements  
-- 5 alignements par voie  
python manage.py seed_alignements --par_voie 5  
-- Repartir de zéro  
python manage.py seed_alignements --reset --par_voie 3  


## Initialisation du projet  

python -m venv .venv  
.venv\Scripts\activate  
pip install django django-cors-headers psycopg2 django-environ djangorestframework django-filter  
django-admin startproject ru  
cd ru  
python manage.py startapp core  
python manage.py startapp backoffice  
python manage.py makemigrations  
python manage.py migrate  
python manage.py createsuperuser  
python manage.py runserver  




## Déploiement
Pour déployer le projet, suivre les instructions dans [`docs/deploiement/`](docs/deploiement/).





