import logging
import re
import sqlite3

import coloredlogs

from hms_base.client import Client
from hms_base.decorators import topic


DB_PATH = '/home/oneshot/agenda.sqlite.backup'

COMMAND_ADD_REGEX = re.compile('(\d{1,2}\/\d{2}\/\d{4}\s\d{1,2}:\d{2})\s"([^"]+)"\s"([^"]+)"(.+)$')
COMMAND_ADDSCEANCE_REGEX = re.compile('(\d{1,2}\/\d{2}\/\d{4}\s\d{1,2}:\d{2})$')

def get_logger():
    return logging.getLogger(__name__)

def irc_debug(rabbit, msg):
    rabbit.publish('irc_debug', {'privmsg': msg})

def show_all(rabbit, db, show_all=False):
    query = 'select rowid,* from agenda where status=1 order by rowid asc'
    if not show_all:
        query += ' limit 5'

    for event in db.execute(query):
        txt = '#{0}: {1} ; {2} le {4} {5}'.format(*event)
        irc_debug(rabbit, txt)


def remove_event(rabbit, db, id):
    db.execute('update agenda set status=0 where rowid=?', (id,))

def add_event(rabbit, db, date, lieu, titre, desc):
    db.execute('insert into agenda (titre,lieu,description,date,status) values (?,?,?,?,1)', (titre, lieu, desc, date))


def main():
    """Entry point of the program."""

    # Logging
    coloredlogs.install(level='INFO')

    # Connect to Rabbit
    rabbit = Client('hms_agenda', 'haum', ['irc_command'])

    rabbit.connect()

    def voice_required(f):
        """Decorator that checks if the sender is voiced."""
        def wrapper(*args):
            print(args)
            if 'is_voiced' in args[2] and args[2]['is_voiced']:
                return f(*args)
            else:
                rabbit.publish('irc_debug', {'privmsg': 'On se connait ? Tu n’es pas voiced mon ami...'})
        return wrapper

    @topic('irc_command')
    def callback(client, topic, message):
        
        @voice_required
        def do_work(client, topic, message):
            conn = sqlite3.connect(DB_PATH)
            db = conn.cursor()

            if message['arg'] == '':
                show_all(rabbit, db)
                return
            if message['arg'] == 'all':
                show_all(rabbit, db, show_all=True)
                return

            # (add_seance|add|remove|modify|all)
            command = message['arg'].split(' ')[0]
            command_arg = ' '.join(message['arg'].split(' ')[1:])

            if command == 'remove':
                try:
                    remove_event(rabbit, db, int(command_arg))
                    irc_debug(rabbit, 'événement correctement supprimé')
                except (TypeError, ValueError):
                    get_logger().error('error while parsing args for remove')
                    irc_debug(rabbit, 'il me faut un nombre en paramètre')

            elif command == 'add':
                result = COMMAND_ADD_REGEX.match(command_arg)
                if not result:
                   get_logger().error('error while parsing args for add')
                   irc_debug(rabbit, 'mauvais format')
                   return

                date = result.group(1)
                lieu = result.group(2)
                titre = result.group(3)
                desc = result.group(4)

                get_logger().info('starting add event')
                add_event(rabbit, db, date, lieu, titre, desc)
                get_logger().info('event added')

                irc_debug(rabbit, 'événement ajouté !')

            conn.commit()
            conn.close()                

        if 'command' in message and message['command'] == 'agen':
            do_work(client, topic, message)

    rabbit.listeners.append(callback)

    rabbit.start_consuming()

    rabbit.disconnect()


if __name__ == '__main__':
    main()
