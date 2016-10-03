import logging

import coloredlogs

from hms_base.client import Client
from hms_base.decorators import topic

from hms_agenda.irc import AgendaBot


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

        if 'command' in message:
            if message['command'] == 'agenda':
                do_work(client, topic, message)
            elif message['command'] == 'help':
                bot.help()

    rabbit.listeners.append(callback)

    # Infinite listen loop
    try:
        rabbit.start_consuming()
    except KeyboardInterrupt:
        get_logger().critical('Got a keyboard interrupt')
    finally:
        rabbit.disconnect()


if __name__ == '__main__':
    main()
