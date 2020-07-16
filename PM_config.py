#######################################################################################################################################
## FILE/DIRECTORY LOCATIONS:
# sound:
applause_sound_location='/Users/user/Documents/PYTHON_PROJECTS/work_TIMER/applaud.aiff',
ding_sound_location='/Users/user/Documents/PYTHON_PROJECTS/work_TIMER/glass.aiff'

# database:
database_location = '"/Users/user/Documents/PRODUCTIVITY/PG_DATABASE"'

#######################################################################################################################################

## DOCKER SETTINGS:
pg_local_port='5430'
postgres_container_name = 'prodman-pg'


## databse startup function:
import os 
def postgres_startup():
    docker_shell_command = 'docker run --rm --name {} -e POSTGRES_PASSWORD=docker -d -p {}:5432 -v {}:/var/lib/postgresql/data postgres'.format(postgres_container_name, pg_local_port, database_location)
    check_container = 'docker container inspect {} > /dev/null 2>&1 || '.format(postgres_container_name)
    os.system(check_container+docker_shell_command)