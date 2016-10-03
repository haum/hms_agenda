Agenda microservice
###################

This microservice is dedicated for the handling of the agenda of the HAUM.

The backend of this microservice is a SQLite database, but you should
communicate with this service if you want to interract with the agenda
instead of using the database directly.

Using
-----

Create a Python 3 virtualenv and install software::

    $ virtualenv -ppython3 venv
    $ source venv/bin/activate
    (venv) $ pip install .

Then start the bot inside the virtual env::

    (venv) $ hms_agenda

License
-------

This project is brought to you under MIT license. For further information,
please read the provided ``LICENSE.txt`` file.