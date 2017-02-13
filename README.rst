Agenda microservice
###################

.. image:: https://travis-ci.org/haum/hms_agenda.svg?branch=master
    :target: https://travis-ci.org/haum/hms_agenda

.. image:: https://coveralls.io/repos/github/haum/hms_agenda/badge.svg?branch=master
    :target: https://coveralls.io/github/haum/hms_agenda?branch=master

This microservice is dedicated for the handling of the agenda of the HAUM.

The backend of this microservice is a SQLite database, but you should
communicate with this service if you want to interact with the agenda
instead of using the database directly.

Using
=====

Create a Python 3 virtualenv and install software::

    $ virtualenv -ppython3 venv
    $ source venv/bin/activate
    (venv) $ pip install .

Then start the bot inside the virtual env::

    (venv) $ hms_agenda

Accepted messages
=================

Topic ``agenda.query``.

Adding an event
---------------

.. code:: python

    command = {
        'command': 'add',
        'arguments': {
            'date': '10/11/2017 17:45',
            'location': 'Local du HAUM',
            'title': 'Test débile',
            'desc': 'Un super test complètement débile'
        }
    }

Adding a seance
---------------

.. code:: python

    command = {
        'command': 'add_seance',
        'arguments': {
            'date': '10/11/2017 17:45'
        }
    }


Removing an event
-----------------

.. code:: python

    command = {
        'command': 'remove',
        'arguments': {
            'id': 42
        }
    }

Modifying an event
------------------

.. code:: python

    command = {
        'command': 'modify',
        'arguments': {
            'id': 42,
            'field': 'titre',
            'new_value': 'Un super nouveau titre'
        }
    }

License
=======

This project is brought to you under MIT license. For further information,
please read the provided ``LICENSE.txt`` file.