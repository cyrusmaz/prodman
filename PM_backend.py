import time
import datetime
import threading
import os
import pandas as pd
from copy import deepcopy
import json
from sqlalchemy import text, create_engine
from functools import reduce

import PM_config


class prodman_backend:
    def __init__(self, applause_sound_location,ding_sound_location):

        self.applause_sound_location = applause_sound_location
        self.ding_sound_location = ding_sound_location

        self.tasks = []
        self.schedule = []

        self.totals_goal = {}
        
        # totals / counts:
        # total minutes spent on task thus far / total blocks spent on task thus far
        self.totals= {}
        self.counts= {}

        self.user_input = None
        self.task = None
        self.current_focus = None
        self.current_notes = None
        self.current_block_index = 0
        self.pause = False
        self.hassler_status = False
        self.session_complete = True

        self.length = None
        self.block_time_elapsed = None
        self.block_time_remaining = None
        

        self.timeline = [] # list of dicts: 
 
        self.session_start_time = None
        self.date_string = None
        self.time_string = None
        self.timedelta_elapsed = datetime.timedelta()
        self.pause_elapsed_timedelta = datetime.timedelta()

        self.template_names = []
        self.templates_dict = []
        self.selected_history = []
        

    def set_schedule(self,schedule):
        # print(schedule)
        tasks=[]
        for block in schedule:
            task=block['task'].strip().lower()
            tasks.append(task)
            block['task']=task
        tasks = list(set(tasks))

        self.tasks = tasks
        self.schedule=schedule

        # totals_goal:
        goal = pd.DataFrame(schedule).groupby('task').sum()['length']
        self.totals_goal = dict(zip(
            list(goal.index.values)+['pause', 'hassler',], 
            [datetime.timedelta(seconds=float(m)*60) for m in list(goal.values)]+[datetime.timedelta()]*3
            ))
        self.totals_goal['total']=reduce((lambda x, y: x + y), self.totals_goal.values())
        
        # totals / counts:
        # total minutes spent on task thus far / total blocks spent on task thus far
        self.totals=dict(zip(tasks+['pause', 'hassler',], [datetime.timedelta()]*(len(tasks)+2)))
        self.counts=dict(zip(tasks+['pause', 'hassler',], [0]*((len(tasks)+2))))        


    def new_timeline_block(self, task=None):
        if task is None: task=self.task
        new_block = {
            'start': datetime.datetime.now(),
            'end': None,
            'task': task,
            'focus': self.current_focus,
            'notes': self.current_notes,}
        self.timeline.append(new_block)

    def end_timeline_block(self):
        if self.timeline[-1]['end'] is not None: 
            print("LAST BLOCK DOES NOT NEED ENDING!!!!!!")
        else:
            self.timeline[-1]['end']=datetime.datetime.now()

    def initialize_user_input(self): self.user_input=None

    def start(self):
        self.current_block_index = 0
        self.session_complete = False
        self.pause = False
        self.timeline = []
        self.session_start_time = datetime.datetime.now()
        self.date_string="{}:{}:{}".format(self.session_start_time.year,str(self.session_start_time.month).rjust(2, "0"),str(self.session_start_time.day).rjust(2, "0"))
        self.time_string="{}:{}:{}".format(str(self.session_start_time.hour).rjust(2, "0"),str(self.session_start_time.minute).rjust(2, "0"),str(self.session_start_time.second).rjust(2, "0"))
        for block in self.schedule: 
            a=self.general_timer(**block)
            if a=="finish":
                self.end_timeline_block()
                self.session_complete = True
                self.task = None
                self.initialize_user_input()
                break
            self.current_block_index += 1   
        self.session_complete = True
        self.system_wrapper('say ", session completed!"')
        print("SESSION COMPLETED!")
        
    def return_progress(self):
        if len(self.tasks)==0:
            return [], [], []
        tasks = self.tasks+['pause', 'hassler']
        y_total = [ self.totals[task].total_seconds()/60 for task in tasks]
        y_goal = [ self.totals_goal[task].total_seconds()/60 for task in tasks]
        return tasks, y_goal, y_total

    def return_totals_and_goals_numeric(self):
        if len(self.totals)==0:
            return {}, {}
        session_total=deepcopy(self.totals)
        session_total['total']=reduce((lambda x, y: x + y), self.totals.values())

        intermediate = [v if k not in ['pause','hassler','total'] else datetime.timedelta(0) for k,v in session_total.items()]
        session_total['total*']=reduce((lambda x, y: x + y), intermediate)
        # print([v if k not in ['pause','hassler','total'] else 0 for k,v in session_total.items()])
        # print(session_total)
        
        goal = deepcopy(self.totals_goal)
        goal['total*']=goal['total']
        return session_total, goal

    def return_totals_and_goals_string(self):
        
        if len(self.totals)==0:
            return {}, {}

        session_total, goal = self.return_totals_and_goals_numeric()

        session_total={k:self.timedelta_to_string(v) for k, v in session_total.items()}
        # session_total['total']=self.timedelta_to_string(reduce((lambda x, y: x + y), self.totals.values()))
        # session_total['total*']=self.timedelta_to_string(sum([v if k not in ['pause','hassler','total'] else 0 for k,v in self.totals.items()]))
        
        goal = {k:self.timedelta_to_string(v) for k, v in goal.items()}
        return session_total, goal

    def print_stats(self):
        current_time = datetime.datetime.now()
        total_elapsed = current_time - self.session_start_time
        os.system("printf '\033c'")
        print("****************************************************************************")
        print("Session started at: {}".format(self.session_start_time))
        # date_string="{}:{}:{}".format(self.session_start_time.year,str(self.session_start_time.month).rjust(2, "0"),str(self.session_start_time.day).rjust(2, "0"))
        # time_string="{}:{}:{}".format(str(self.session_start_time.hour).rjust(2, "0"),str(self.session_start_time.minute).rjust(2, "0"),str(self.session_start_time.second).rjust(2, "0"))
        print("START DATE: {}".format(self.date_string))
        print("START TIME: {}".format(self.time_string))
        print("TIME ELAPSED: {}".format(self.timedelta_to_string(total_elapsed)))
        # print("TIMELINE:")
        # print(pd.DataFrame(data=self.timeline))

        # print("COUNTS: ")
        # print(pd.Series(self.counts))

        print("Block index: {}".format(self.current_block_index))

        print("TOTALS:")
        # total={k:self.timedelta_to_string(v) for k, v in self.totals.items()}
        # goal = {k:self.timedelta_to_string(v) for k, v in self.totals_goal.items()}
        session_total, goal = self.return_totals_and_goals_string()
        print(pd.DataFrame([session_total, goal], index=['total', 'goal']))

        print("****************************************************************************")

        if self.pause == True:
            print("CURRENTLY: {}, PAUSED".format(self.task))
        
        elif self.pause == False:
            print("CURRENTLY: {}, IN SESSION".format(self.task))
        
        if (self.current_focus != None) and (self.current_focus != ''):
            print("FOCUS: {}".format(self.current_focus))

        if (self.current_focus != None) and (self.current_focus != ''):
            print("NOTES: {}".format(self.current_notes))
        # pass

    def set_input_from_dash(self, dash_input):
        self.user_input = dash_input
        if dash_input == "pause":
            self.pause = True
            self.counts['pause'] += 1
        if dash_input == "unpause":
            self.pause = False
        if dash_input == "record":
            self.record_session() 
  

    def get_input(self):
        while True:
            self.user_input = input()
            print("wt.get_input() just set wt.user_input to {}".format(self.user_input))
            if self.user_input == "pause":
                self.pause = True
                self.counts['pause'] += 1

            if self.user_input == "unpause":
                self.pause = False
            if self.user_input == "record":
                self.record_session()
            if self.user_input == "start":
                self.start()          
            if self.user_input == "exit":
                return      

# ### record to CSV
#     def record_session(self):
#         data=deepcopy(self.timeline)
#         data[-1]['end']=datetime.datetime.now()

#         output = pd.DataFrame(data)
#         output['length'] = output['end']-output['start']
#         output['length'] = [length.total_seconds()/60 for length in list(output['length'])]

#         record_file_path = self.log_file_location

#         output.to_csv(record_file_path)
#         os.system('say "recorded!"')
    
    def timeline_completed(self):
        """
        returns the timeline of current session in json format. 
        if there is no 'end' for final block, it uses current time for it
        """
        
        if len(self.timeline)<1:
            return []
        
        # compute length per block for each block:
        # update end time of final block, if necessary
        timeline_completed=deepcopy(self.timeline)
        if timeline_completed[-1]['end'] is None:
            timeline_completed[-1]['end']=datetime.datetime.now()
        
        # compute length of each block
        length = lambda end, start: (end-start).total_seconds()/60
        for item in timeline_completed:
            item.update( {'length': length(item['end'], item['start'])})            
            item.update( {'start': str(item['start'])}) 
            item.update( {'end': str(item['end'])}) 

        return timeline_completed

    #### SQL DATABASE FUNCTIONS:

    def postgres_startup(self):
        docker_shell_command = 'docker run --rm --name {} -e POSTGRES_PASSWORD=docker -d -p {}:{} -v {}:/var/lib/postgresql/data postgres'.format(
            PM_config.postgres_container_name, 
            PM_config.pg_local_port,
            PM_config.pg_docker_port, 
            PM_config.database_location)
        check_container = 'docker container inspect {} > /dev/null 2>&1 || '.format(PM_config.postgres_container_name)
        # fire up postgres in a docker container if there is currently no docker container by the name of postgres_container_name
        os.system(check_container+docker_shell_command)

    def get_history(self, start_date, end_date):
        pg_local_port='5430'
        db_string = 'postgresql://postgres:docker@localhost:{}/postgres'.format(pg_local_port)
        engine = create_engine(db_string)
        connection = engine.connect()
        get_history_query = text("""
        SELECT * FROM history WHERE session_date BETWEEN '{}' AND '{}'
        """.format(start_date,end_date))
        history = connection.execute(get_history_query)
        history = list(history)
        wt.selected_history = history
        # return history

    def save_template(self,template_id, template, vocalize=True):
        self.get_templates(audio=False)


        if (template_id =='') or ('"' in template_id) or ("'" in template_id):
            if vocalize is not False:
                self.system_wrapper('say "template name cannot be blank!"')
            return 'invalid name'

        if template_id in self.template_names:
            # self.system_wrapper('say "template name already exists."')
            output_string = "overwritten"
        else: 
            output_string = "saved"


        pg_local_port='5430'
        db_string = 'postgresql://postgres:docker@localhost:{}/postgres'.format(pg_local_port)
        engine = create_engine(db_string)
        connection = engine.connect()

        insert_statement = text("""
        INSERT INTO public.templates
        (
            template_id,
            template
        )
        VALUES ('{template_id}', '{template}')
        """.format(
            template_id=template_id,
            template=json.dumps(template),
        ))

        connection.execute(insert_statement)
        engine.dispose()
        if vocalize is not False:
            if output_string == "saved":
                self.system_wrapper('say "template saved!"')
            if output_string == "overwritten":
                self.system_wrapper('say "template overwritten!"')

        return output_string

    def get_templates(self, audio=True):
        pg_local_port='5430'
        db_string = 'postgresql://postgres:docker@localhost:{}/postgres'.format(pg_local_port)
        engine = create_engine(db_string)
        connection = engine.connect()

        templates_list_query = text("""
        SELECT * 
        FROM public.templates """)

        templates_list = connection.execute(templates_list_query)
        engine.dispose()
        if audio==True:
            self.system_wrapper('say "templates list refreshed!"')
        templates_list = list(templates_list)

        self.templates_dict = {template[0] : template[1] for template in templates_list}
        self.template_names = [k for k,v in self.templates_dict.items()]

    def delete_template(self, template_id):
        pg_local_port='5430'
        db_string = 'postgresql://postgres:docker@localhost:{}/postgres'.format(pg_local_port)
        engine = create_engine(db_string)
        connection = engine.connect()

        delete_statement = text("""
        DELETE FROM public.templates
        WHERE template_id='{template_id}'
        """.format(template_id=template_id))

        connection.execute(delete_statement)
        engine.dispose()   
        self.system_wrapper('say "template deleted!"')     

    def delete_from_history(self, session_dates, session_ids):
        pg_local_port='5430'
        db_string = 'postgresql://postgres:docker@localhost:{}/postgres'.format(pg_local_port)
        engine = create_engine(db_string)
        connection = engine.connect()
        
        query_string = "DELETE FROM HISTORY WHERE "
        condition_list = ["(session_date='{}' AND session_id={}) ".format(session_date, session_id) for session_date, session_id in zip(session_dates, session_ids)]
        for j in range(len(condition_list)):
            query_string=query_string+condition_list[j]
            if j<(len(condition_list)-1):
                query_string= query_string+"OR "

        connection.execute(query_string)
        if len(session_dates)==1:
            self.system_wrapper('say "1 session deleted"')
        else:    
            self.system_wrapper('say "{} sessions deleted"'.format(len(session_dates)))

    def record_session(self, session_name=None):
        pg_local_port='5430'
        db_string = 'postgresql://postgres:docker@localhost:{}/postgres'.format(pg_local_port)
        engine = create_engine(db_string)
        connection = engine.connect()

        session_date = self.session_start_time.strftime('%Y-%m-%d')

        #### see if there are any sessions with the same date
        session_id_query = text("""
        SELECT session_id 
        FROM public.history 
        WHERE session_date='{}'
        ORDER BY session_id DESC
        LIMIT 1
        """.format(session_date))
        
        session_id_list = connection.execute(session_id_query)
        session_id_list = list(session_id_list)

        ### set session_id
        if len(session_id_list)==0:
            session_id=0
        else:
             session_id=int(session_id_list[0][0]+1)
        
        # ### set timeline
        # timeline = self.timeline_json()
        # print("HERE")
        ### insert current session into database
        if session_name is not None:
            insert_statement = text("""
                INSERT INTO public.history
                (
                    session_date,
                    session_id,
                    session_name,
                    timeline,
                    schedule
                )
                VALUES ('{session_date}', '{session_id}', '{session_name}', '{timeline}', '{schedule}' )
                """.format(
                    session_date=session_date,
                    session_id=session_id,
                    session_name=session_name,
                    timeline=json.dumps(self.timeline_completed()),
                    schedule=json.dumps(self.schedule)
                ))

        elif session_name is None: 
            insert_statement = text("""
            INSERT INTO public.history
            (
                session_date,
                session_id,
                timeline,
                schedule
            )
            VALUES ('{session_date}', '{session_id}', '{timeline}', '{schedule}' )
            """.format(
                session_date=session_date,
                session_id=session_id,
                timeline=json.dumps(self.timeline_completed()),
                schedule=json.dumps(self.schedule)
            ))
        
        connection.execute(insert_statement)
        engine.dispose()
        # os.system('say "recorded!"')
        self.system_wrapper('say "recorded!"')
    ########



    @staticmethod
    def timedelta_to_string(timedelta_obj):
        if type(timedelta_obj) is not datetime.timedelta:
            return timedelta_obj
        else:
            time_elapsed = timedelta_obj.total_seconds()
            hours = str(int(time_elapsed // 3600))
            hours = hours.rjust(2, "0")
            time_elapsed = time_elapsed - (time_elapsed // 3600)*3600
            minutes = time_elapsed // 60
            minutes = str(int(time_elapsed // 60))
            minutes = minutes.rjust(2, "0")
            time_elapsed = time_elapsed - (time_elapsed // 60)*60
            seconds = str(int(time_elapsed))
            seconds = seconds.rjust(2, "0")
            output = "{}:{}:{}".format(hours,minutes,seconds)
            return(output)

    def general_timer(  self, 
                        task, 
                        length,
                        focus=None,
                        hassler=False,
                        applause=False,
                        dinger=None,
                        notes=None,
                        **kwargs):

        if hassler == True:
            self.hassler(task, focus)

        # # os.system("printf '\033c'")
        print("START {}!".format(task))                 # PRING STATEMENT OF START
        if (focus is not None) and (focus!=''):
            print("FOCUS ON {}!".format(focus))   
        
        print("Notes: {}!".format(notes))                     # PRING STATEMENT OF START
        
        self.system_wrapper('say "START {}!"'.format(task))
        if (focus is not None) and (focus!=''):
            # os.system('say "FOCUS ON {}!"'.format(focus))
            self.system_wrapper('say "FOCUS ON {}!"'.format(focus))

        length = datetime.timedelta(seconds=length*60)
        self.length = length        

        self.current_focus = focus
        self.task = task
        self.current_notes = notes

        self.new_timeline_block()

        start_time = datetime.datetime.now()
        timedelta_elapsed_current_phase = datetime.timedelta()

        total_so_far = self.totals[task]

        dinger_time = None
        if (dinger is not None) and (dinger is not '') and (type(dinger)in [int, float]) and(dinger>0):
            dinger_time = datetime.timedelta(minutes=dinger)


        while True:    
            ## delete this
            self.return_totals_and_goals_numeric()
            ##
            time_now = datetime.datetime.now()
            self.timedelta_elapsed = time_now - start_time
            timedelta_remaining = max(length - (timedelta_elapsed_current_phase + self.timedelta_elapsed),datetime.timedelta())


            # string for dash display
            self.block_time_remaining = self.timedelta_to_string(timedelta_remaining)
            self.block_time_elapsed = (timedelta_elapsed_current_phase + self.timedelta_elapsed)


            self.totals[task] = total_so_far + self.timedelta_elapsed + timedelta_elapsed_current_phase
            if (dinger is not None) and (dinger is not '') and (type(dinger)in [int, float]) and(dinger>0):
                if length-timedelta_remaining>dinger_time:
                    self.system_wrapper('afplay {}'.format(self.ding_sound_location))
                    dinger_time=dinger_time+datetime.timedelta(minutes=dinger)

            os.system("printf '\033c'")
            self.print_stats()
            ##### UNCOMMENT THIS: 
            print("{} time remaining: {}".format(task, self.timedelta_to_string(timedelta_remaining)))
            
            if timedelta_elapsed_current_phase + self.timedelta_elapsed > length:  

                self.end_timeline_block() ### HEHE            

                self.counts[task]+=1
                if applause==True: 
                    os.system('afplay {}'.format(self.applause_sound_location))

                self.timedelta_elapsed = datetime.timedelta()
                break

            if self.pause == True:
                timedelta_elapsed_current_phase = timedelta_elapsed_current_phase + self.timedelta_elapsed

                self.end_timeline_block()
                pause_result = self.pause_timer(timedelta_remaining)
                if pause_result == "finish":
                    return "finish"
                self.new_timeline_block()

                start_time = datetime.datetime.now()

            ###########
            if self.user_input=="finish":
                return "finish"
            ###########

            if self.user_input is not None and str.lower(self.user_input) == "next":
                self.initialize_user_input()
                self.end_timeline_block()
                self.system_wrapper('say "next!"')
                
                break

            time.sleep(1)

    def next_timer(self):
        start_time = datetime.datetime.now()

        print("Are you sure you want to go to next block?")
        print("y / n ?")
        self.system_wrapper('say "you sure, dude ?"')

        self.new_timeline_block(task='next')
        while self.user_input is None:
            time.sleep(1)
            pass 
        if str.lower(self.user_input) == "yes" or str.lower(self.user_input) == "y":
            response = 'yes'
        else: 
            response = 'no'    

        self.end_timeline_block()
        elapsed_time = datetime.datetime.now() - start_time
        self.totals['next_prompt'] = self.totals['next_prompt'] + elapsed_time

        self.initialize_user_input() 
        return response

    def pause_timer(self, timedelta_remaining):
        print("PAUSING SESSION! type unpause to continue!\n")                  
        self.system_wrapper('say "pausing current session"')

        self.new_timeline_block(task='pause')

        pause_timer_start = datetime.datetime.now()
        total_so_far = self.totals['pause']
        while self.pause == True:
            
            if self.user_input=="finish":
                return "finish"

            time.sleep(1)
            time_now = datetime.datetime.now()
            pause_elapsed_timedelta = time_now - pause_timer_start

            self.totals['pause'] = total_so_far + pause_elapsed_timedelta

            # os.system("printf '\033c'")
            self.print_stats()
            self.pause_elapsed_timedelta=pause_elapsed_timedelta
            print("{} time remaining: {}".format(self.task, self.timedelta_to_string(timedelta_remaining)))
            print("Paused thus far: {}".format(self.timedelta_to_string(pause_elapsed_timedelta)))
        
        if self.pause == False:
            time_now = datetime.datetime.now()
            pause_elapsed_timedelta = time_now - pause_timer_start
            
            self.totals['pause'] = total_so_far + pause_elapsed_timedelta 

            self.end_timeline_block()

            print("UNPAUSING\n")                                                      # UNPAUSE PRINT

            # os.system('say "unpausing current session"')                              # UNPAUSE AUDIO
            self.system_wrapper('say "unpausing"')
            # os.system('say "returning to {}"'.format(self.task))                      # UNPAUSE AUDIO
            
            self.system_wrapper('say "and returning to {}"'.format(self.task))    
            return ""

    @staticmethod
    def system_wrapper(string):
        def dictate(string):
            os.system(string)
            return
        t=threading.Thread(target=dictate, kwargs={'string':string})
        t.start()

    def hassler(self, task, focus):
        #########
        self.hassler_status = True
        total_so_far = self.totals['hassler']
        #########
        start_time = datetime.datetime.now()

        self.new_timeline_block(task='hassler')

        if focus is not None:
            print("Time to start {}, with focus on {}".format(task, focus))

        if focus is None:
            print("Time to start {}".format(task))

        print("type 'okay' to begin")

        while self.user_input != "okay":

            os.system('say "type, okay, to start {}"'.format(task))

            if self.user_input == 'pause':
                #########
                elapsed_time = datetime.datetime.now() - start_time
                self.totals['hassler'] = total_so_far + elapsed_time
                #########
                self.end_timeline_block()
                self.pause_timer(datetime.timedelta())
                self.new_timeline_block(task='hassler')

                #########
                total_so_far = self.totals['hassler']
                #########

            time.sleep(0.5)

        if self.user_input == "okay":
            self.end_timeline_block()

        elapsed_time = datetime.datetime.now() - start_time
        self.totals['hassler'] = total_so_far + elapsed_time

        self.initialize_user_input() 
        #########
        self.hassler_status = False

# if __name__ == "__main__":

#     schedule = [
#         {'task': 'work',        'length': 15, 'hassler': True, 'applause':True, 'dinger':'next', 'focus': 'standing', 'notes': ''},
#         {'task': 'work',        'length': 15, 'hassler': False, 'applause':True, 'dinger':5, 'focus': 'standing', 'notes': ''},
#         {'task': 'work',        'length': 15, 'hassler': False, 'applause':True, 'dinger':None, 'focus': 'standing', 'notes': ''},
#         {'task': 'work',        'length': 15, 'hassler': False, 'applause':True, 'dinger':0.1, 'focus': 'standing', 'notes': ''},
#         {'task': 'work',        'length': 15, 'hassler': False, 'focus': 'standing', 'notes': ''},]*4


# ####################################################################################

#     wt = prodman_backend(applause_sound_location=PM_config.applause_sound_location, ding_sound_location=PM_config.ding_sound_location)
#     wt.set_schedule(schedule)
#     t=threading.Thread(name="input", target=wt.get_input, daemon=True)
#     t.start()
#     wt.start()
