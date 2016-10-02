import time
import logging
import re

from hms_agenda.agenda import Agenda


DB_PATH = '/home/microjoe/agenda.sqlite.backup'

COMMAND_ADD_REGEX = re.compile(r'(\d{1,2}\/\d{2}\/\d{4}\s\d{1,2}:\d{2})\s"([^"]+)"\s"([^"]+)"(.+)$')
COMMAND_ADDSCEANCE_REGEX = re.compile(r'(\d{1,2}\/\d{2}\/\d{4}\s\d{1,2}:\d{2})$')


def get_logger():
    return logging.getLogger(__name__)

class AgendaBot:
    def __init__(self, rabbit):
        self.rabbit = rabbit
        self.agenda = Agenda(DB_PATH)

    def irc_debug(self, msg):
        self.rabbit.publish('irc_debug', {'privmsg': msg})

    def parse_command(self, client, topic, message):

        if message['arg'] == '':
            self.show_events()
            return
        if message['arg'] == 'all':
            self.show_events(show_all=True)
            return

        # (add_seance|add|remove|modify|all)
        command = message['arg'].split(' ')[0]
        command_arg = ' '.join(message['arg'].split(' ')[1:])

        if command == 'remove':
            self.remove_event(command_arg)

        elif command == 'add':
            self.add_event(command_arg)


    def show_events(self, show_all=False):
        """Show the events on the IRC chan."""
        for event in self.agenda.get_events(show_all):
            # Display the event on IRC in human-readable format
            self.irc_debug('#{0}: {1} ; {2} le {4} {5}'.format(*event))
            # Sleep between each line in order to avoid throttle
            time.sleep(1)

    def remove_event(self, arg):
        """Remove one event with its ID in the database."""
        try:
            self.agenda.remove_event(int(arg))
            self.irc_debug('événement correctement supprimé')
        except (TypeError, ValueError):
            get_logger().error('error while parsing args for remove')
            self.irc_debug('il me faut un nombre en paramètre')

    def add_event(self, arg):
        """Add an event to the database."""
        result = COMMAND_ADD_REGEX.match(arg)

        if not result:
            get_logger().error('error while parsing args for add')
            self.irc_debug('mauvais format')
            return

        self.agenda.add_event(*result.groups())
        self.irc_debug('événement ajouté !')