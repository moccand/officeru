# officeru





## Initialis

python -m venv .venv
source .venv/bin/activate      # Linux/Mac
# ou .venv\Scripts\activate    # Windows

pip install -r requirements.txt

python manage.py runserver

## 

python -m venv .venv
.venv\Scripts\activate
pip install django,  django-cors-headers, psycopg2, django-environ
django-admin startproject ru
cd ru
python manage.py startapp core
python manage.py startapp backoffice
- création des modèles via Claude.ai à partir de la stricture des tables SQL + création des indexes
- ajoute de l'app au projet
python manage.py makemigrations
python manage.py migrate 
python manage.py createsuperuser
- ajout des modèles à l'admin dans core/admin.py


python manage.py runserver



je reviens sur le sujet des templates : mon projet Django 6/0.3 s'appelle 'ru' et mon application 'backoffice' est-ce que tu peux me refaire une structure de template optimisée et les URL pour les 2 pages ? la page visiteur.html que tu as préparée sera consultation/carte et la page dasboard sera 