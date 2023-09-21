# Incursion (aka Transient Assault (aka Project Keqei 2.0))
There's nothing to see here. Just a random login screen from a tutorial and nothing else.

### Installing

Create a virtual environment with `python -m venv .venv`

Start the thing with `.venv\Scripts\Activate.ps1`

Install shit with
`python -m pip install django~=4.0.0`
`python -m pip install channels`
`python -m pip install django-crispy-forms`
`python -m pip install crispy-bootstrap4` 
(poetry or whatever stuff that deal with these exist but let's just install it manually)

Create an admin user with `python manage.py createsuperuser`
(Alternatively, use username: admin, password: ilovekeqing)

Run the thing with `python manage.py runserver`

It should be there on `127.0.0.1:8000`

Admin panel on `127.0.0.1:8000/admin`

When in doubt, `python manage.py makemigrations`, `python manage.py migrate`, or `python manage.py migrate --run-syncdb`. 

Remember to `.venv\Scripts\Activate.ps1` if you run it again later in a new terminal

Well it works on my machine

![yanfeismug](https://github.com/Mewtwo2387/basement/blob/main/yanfeismug.png?raw=true)