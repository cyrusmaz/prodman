from sqlalchemy import text, create_engine
import os

import PM_config

PM_config.postgres_startup()

db_string = 'postgresql://postgres:docker@localhost:{}/postgres'.format(PM_config.pg_local_port)
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
