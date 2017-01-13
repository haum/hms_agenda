import logging

from hms_agenda.agenda import Agenda
from hms_agenda import settings


def get_logger():
    return logging.getLogger(__name__)

class AgendaParser:
    def __init__(self, rabbit):
        self.rabbit = rabbit
        self.agenda = Agenda(settings.DB_PATH)

    def parse_command(self, client, topic, message):
        command = message['command']
        args = message['arguments'] if 'arguments' in message else None

        # Handle listing of events
        if command == 'list':
            show_all = 'all' in args if args else False
            events = list(self.agenda.get_events(all=show_all))
            self.answer({'list': events}, message)
            return

        # Handle other commands using a look-up table
        commands_lut = {
            'remove': self.agenda.remove_event,
            'add': self.agenda.add_event,
            'add_seance': self.agenda.add_sceance,
            'modify': self.agenda.modify_sceance
        }

        # Try to find command and call it with provided arguments
        if command in commands_lut:
            # Execute corresponding command
            commands_lut[command](**args)
            # Notify that the command was executed
            self.answer({command: True}, message)


    def answer(self, content, orig):
        self.rabbit.publish('agenda.answer', {
            'source': orig['source'],
            'content': content
        })
