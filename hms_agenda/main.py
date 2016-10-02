import logging

import coloredlogs

from hms_base.client import Client
from hms_base.decorators import topic

from irc import AgendaBot


def get_logger():
    return logging.getLogger(__name__)


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
            if 'is_voiced' in args[2] and args[2]['is_voiced']:
                return f(*args)
            else:
                rabbit.publish('irc_debug', {'privmsg': 'On se connait ? Tu n’es pas voiced mon ami...'})
        return wrapper

    bot = AgendaBot(rabbit)

    @topic('irc_command')
    def callback(client, topic, message):
        
        @voice_required
        def do_work(client, topic, message):
            bot.parse_command(client, topic, message)

        if 'command' in message and message['command'] == 'agenda':
            do_work(client, topic, message)

    rabbit.listeners.append(callback)

    # Infinite listen loop
    rabbit.start_consuming()
    rabbit.disconnect()


if __name__ == '__main__':
    main()
