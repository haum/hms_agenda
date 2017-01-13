import logging

import coloredlogs

from hms_base.client import Client
from hms_base.decorators import topic

from hms_agenda.parser import AgendaParser


def get_logger():
    return logging.getLogger(__name__)


def main():
    """Entry point of the program."""

    # Logging
    coloredlogs.install(level='INFO')

    # Connect to Rabbit
    rabbit = Client('hms_agenda', 'haum', ['agenda.*'])
    rabbit.connect()

    bot = AgendaParser(rabbit)

    @topic('agenda.query')
    def query_callback(client, topic, message):
        bot.parse_command(client, topic, message)

    rabbit.listeners.append(query_callback)

    # Infinite listen loop
    try:
        rabbit.start_consuming()
    except KeyboardInterrupt:
        get_logger().critical('Got a keyboard interrupt')
    finally:
        rabbit.disconnect()


if __name__ == '__main__':
    main()
