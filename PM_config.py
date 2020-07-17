## FILE/DIRECTORY LOCATIONS:
# sound:
applause_sound_location='/Users/user/Documents/PYTHON_PROJECTS/PM_local/applaud.aiff',
ding_sound_location='/Users/user/Documents/PYTHON_PROJECTS/PM_local/ding.wav'

# database:
database_location = '"/Users/user/Documents/PRODUCTIVITY/PG_DATABASE"'
#######################################################################################################################################
#######################################################################################################################################

# INITIAL SCHEDULE
initial_schedule = [
    {'task': 'work', 'length': 25, 'hassler': False, 'applause':True, 'focus': '', 'notes': ''},
    {'task': 'meditation', 'length': 5, 'hassler': False, 'applause':True, 'focus': '', 'notes': ''},
    {'task': 'work', 'length': 25, 'hassler': True, 'applause':True, 'focus': '', 'notes': ''},
    {'task': 'movement', 'length': 5, 'hassler': False, 'applause':True, 'focus': '', 'notes': ''},
    {'task': 'work', 'length': 25, 'hassler': True, 'applause':True, 'focus': '', 'notes': ''},
    {'task': 'meditation', 'length': 5, 'hassler': False, 'applause':True, 'focus': '', 'notes': ''},
    {'task': 'work', 'length': 25, 'hassler': True, 'applause':True, 'focus': '', 'notes': ''},
    {'task': 'break', 'length': 15, 'hassler': False, 'applause':True, 'focus': '', 'notes': ''}]

## DOCKER SETTINGS:
pg_local_port='5430'
pg_docker_port='5432'
postgres_container_name = 'prodman-pg'

