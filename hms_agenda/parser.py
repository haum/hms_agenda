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

        if command == 'list':
            show_all = 'all' in args if args else False
            events = list(self.agenda.get_events(all=show_all))
            self.answer({'list': events}, message)

        if command == 'remove':
            self.agenda.remove_event(**args)
            self.answer({command: True}, message)
        elif command == 'add':
            self.agenda.add_event(**args)
            self.answer({command: True}, message)
        elif command == 'add_seance':
            self.agenda.add_sceance(**args)
            self.answer({command: True}, message)
        elif command == 'modify':
            self.agenda.modify_sceance(**args)
            self.answer({command: True}, message)

    def answer(self, content, orig):
        self.rabbit.publish('agenda.answer', {
            'source': orig['source'],
            'content': content
        })
