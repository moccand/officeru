# officeru

utilise : 
- Django 6.0.3
- Tailwind 4
- DaisyUi 5

## Initialis

python -m venv .venv
source .venv/bin/activate      # Linux/Mac
ou .venv\Scripts\activate    # Windows

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
- création et debug des templates créés par Claude.ai à partir des 


python manage.py runserver



