import unittest
from unittest.mock import Mock

from hms_agenda.parser import AgendaParser


class TestIRCCommands(unittest.TestCase):
    def setUp(self):
        self.bot = AgendaParser(None)
        self.bot.show_events = Mock()

    def parse_command(self, command):
        message = {'arg': command}
        self.bot.parse_command(None, 'irc_command', message)

    def test_list_last(self):
        self.parse_command('')
        self.bot.show_events.assert_called_once_with()

    def test_list_all(self):
        self.parse_command('all')
        self.bot.show_events.assert_called_once_with(show_all=True)

    def test_add_event(self):
        self.bot.add_event = Mock()
        self.parse_command('add test test')
        self.bot.add_event.assert_called_once_with('test test')

    def test_remove_event(self):
        self.bot.remove_event = Mock()
        self.parse_command('remove test test')
        self.bot.remove_event.assert_called_once_with('test test')

    def test_modify_event(self):
        self.bot.modify_sceance = Mock()
        self.parse_command('modify test test')
        self.bot.modify_sceance.assert_called_once_with('test test')

    def test_help(self):
        self.bot.help = Mock()
        self.parse_command('help')
        self.bot.help.assert_called_once_with()