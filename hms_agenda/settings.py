
#DB_PATH = '/home/oneshot/agenda.sqlite'
DB_PATH = '/home/microjoe/agenda.sqlite'

try:
    from hms_agenda.settings_prod import *
except ImportError:
    pass