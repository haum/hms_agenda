import unittest
from unittest.mock import Mock

from hms_agenda.parser import AgendaParser


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = AgendaParser(None)
        self.parser.agenda = Mock()
        self.parser.agenda.add_event = Mock()
        self.parser.agenda.add_sceance = Mock()
        self.parser.agenda.modify_event = Mock()
        self.parser.agenda.remove_event = Mock()
        self.parser.agenda.get_events = Mock(return_value=[])
        self.parser.answer = Mock()

    def parse_command(self, command, args=None):
        message = {'command': command}
        if args is not None:
            message['arguments'] = args
        self.parser.parse_command(None, 'irc_command', message)

    def test_list_last(self):
        self.parse_command('list')
        self.parser.agenda.get_events.assert_called_once_with(all=False)
        self.assertTrue(self.parser.answer.called)

    def test_list_all(self):
        self.parse_command('list', {'all': True})
        self.parser.agenda.get_events.assert_called_once_with(all=True)
        self.assertTrue(self.parser.answer.called)

    def test_add_event(self):
        self.parse_command('add', {
            'date': '10/11/2017 17:45',
            'location': 'Local du HAUM',
            'title': 'Test débile',
            'desc': 'Un super test complètement débile'
        })
        self.parser.agenda.add_event.assert_called_once_with(
            date='10/11/2017 17:45',
            location='Local du HAUM',
            title='Test débile',
            desc='Un super test complètement débile'
        )
        self.assertTrue(self.parser.answer.called)

    def test_add_seance(self):
        self.parse_command('add_seance', {
            'date': '10/11/2017 17:45'
        })
        self.parser.agenda.add_sceance.assert_called_once_with(
            date='10/11/2017 17:45'
        )
        self.assertTrue(self.parser.answer.called)

    def test_remove_event(self):
        self.parse_command('remove', {'id': 42})
        self.parser.agenda.remove_event.assert_called_once_with(id=42)
        self.assertTrue(self.parser.answer.called)

    def test_modify_event(self):
        self.parse_command('modify', {
            'id': 42,
            'field': 'titre',
            'new_value': 'Un super nouveau titre'
        })
        self.parser.agenda.modify_event.assert_called_once_with(
            id=42,
            field='titre',
            new_value='Un super nouveau titre'
        )
        self.assertTrue(self.parser.answer.called)