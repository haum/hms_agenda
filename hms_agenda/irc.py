import time
import logging
import re

from hms_agenda.agenda import Agenda


DB_PATH = '/home/oneshot/agenda.sqlite'

COMMAND_ADD_REGEX = re.compile(r'(\d{1,2}\/\d{2}\/\d{4}\s\d{1,2}:\d{2})\s"([^"]+)"\s"([^"]+)"(.+)$')
COMMAND_ADDSEANCE_REGEX = re.compile(r'(\d{1,2}\/\d{2}\/\d{4}\s\d{1,2}:\d{2})$')
COMMAND_MODIFSCEANCE_REGEX = re.compile(r'(\d+)\s(titre|lieu|date|status)\s(.+)$')

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
        elif command == 'add_seance':
            self.add_seance(command_arg)
        elif command == 'modify':
            self.modify_sceance(command_arg)
        elif command == 'help':
            self.help()


    def show_events(self, show_all=False):
        """Show the events on the IRC chan."""
        events = self.agenda.get_events(show_all)
        if events:
            for event in events:
                # Display the event on IRC in human-readable format
                self.irc_debug('#{0}: {1} ; {2} le {4} {5}'.format(*event))
                # Sleep between each line in order to avoid throttle
                time.sleep(1)
        else:
            self.irc_debug('Aucun événement prochainement')

    def remove_event(self, arg):
        """Remove one event with its ID in the database."""
        try:
            self.agenda.remove_event(int(arg))
            self.irc_debug('Événement correctement supprimé')
        except (TypeError, ValueError):
            get_logger().error('error while parsing args for remove')
            self.bad_format()
            self.help_remove()

    def add_event(self, arg):
        """Add an event to the database."""
        result = COMMAND_ADD_REGEX.match(arg)

        if not result:
            get_logger().error('error while parsing args for add')
            self.bad_format()
            self.help_add()
            return

        self.agenda.add_event(*result.groups())
        self.irc_debug('Événement ajouté !')

    def add_seance(self, arg):
        result = COMMAND_ADDSEANCE_REGEX.match(arg)

        if not result:
            get_logger().error('error while parsing args for add_seance')
            self.bad_format()
            self.help_add_seance()
            return

        self.agenda.add_sceance(*result.groups())
        self.irc_debug('Séance ajoutée !')

    def modify_sceance(self, arg):
        result = COMMAND_MODIFSCEANCE_REGEX.match(arg)

        if not result:
            get_logger().error('error while parsing args for modify_sceance')
            self.bad_format()
            self.help_modify()
            return

        self.agenda.modify_sceance(*result.groups())
        self.irc_debug('Modification effectuée !')

    # Help methods

    def bad_format(self):
        self.irc_debug('Mauvais format')

    def help_remove(self):
        self.irc_debug('Pour supprimer un élément, : !agenda remove id')

    def help_add(self):
        self.irc_debug(
            'Pour ajouter un élément, : !agenda add JJ/MM/YYYY (h)h:mm "Lieu" "Titre" Description')

    def help_add_seance(self):
        self.irc_debug(
            'Pour ajouter un élément, : !agenda add_seance JJ/MM/YYYY (h)h:mm')

    def help_modify(self):
        self.irc_debug(
            'Pour modifier un élément, : !agenda modify id [titre|lieu|date|status] nouvelle valeur')

    def help(self):
        self.help_add()
        self.help_add_seance()
        self.help_modify()
        self.help_remove()