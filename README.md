# officeru

utilise :  
- Django 6.0.3  
- Tailwind 4  
- DaisyUi 5  

## Installation

python -m venv .venv  
source .venv/bin/activate      # Linux/Mac  
ou .venv\Scripts\activate    # Windows  
pip install -r requirements.txt  
python manage.py runserver  


## Initialisation

python -m venv .venv  
.venv\Scripts\activate  
pip install django,  django-cors-headers, psycopg2, django-environ  
django-admin startproject ru  
cd ru  
python manage.py startapp core  
python manage.py startapp backoffice  
python manage.py makemigrations  
python manage.py migrate  
python manage.py createsuperuser  
python manage.py runserver  






