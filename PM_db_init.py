# docker run --rm --name prodman-pg -e POSTGRES_PASSWORD=docker -d -p 5430:5432 -v "/Users/user/Documents/PRODMAN_RECORDS":/var/lib/postgresql/data postgres

from sqlalchemy import text, create_engine
import os

database_location = '"/Users/user/Documents/PRODUCTIVITY/PG_DATABASE"'
pg_local_port='5430'

# docker run --rm --name prodman-pg -e POSTGRES_PASSWORD=docker -d -p 5430:5432 -v "/Users/user/Documents/PRODUCTIVITY/PG_DATABASE":/var/lib/postgresql/data postgres
docker_shell_command = 'docker run --rm --name prodman-pg -e POSTGRES_PASSWORD=docker -d -p {}:5432 -v {}:/var/lib/postgresql/data postgres'.format(pg_local_port, database_location)
os.system(docker_shell_command)


# pg_local_port='5430'
db_string = 'postgresql://postgres:docker@localhost:{}/postgres'.format(pg_local_port)
engine = create_engine(db_string)
connection = engine.connect()

create_history_table = text("""
    CREATE TABLE IF NOT EXISTS public.history (
        session_date text,
        session_id numeric,
        session_name text,
        timeline json,
        schedule json);
        CREATE INDEX ON public.history(session_date, session_id)
""")

create_templates_table = text("""
    CREATE TABLE IF NOT EXISTS public.templates (
        template_id text,
        template json);
        CREATE INDEX ON public.templates(template_id)
""")

connection.execute(create_history_table)
connection.execute(create_templates_table)

engine.dispose()


