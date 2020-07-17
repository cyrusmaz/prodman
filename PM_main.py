import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_table
from dash_table.Format import Format, Scheme, Sign, Symbol
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from flask import Flask
import datetime
import os 
from copy import deepcopy
from collections import defaultdict 
import re
from math import floor 
from matplotlib.pyplot import get_cmap

from PM_backend import *
import PM_config

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
tasks = ['work', 'meditation', 'movement', 'break'] + ['pause', 'hassler']

total_star_message = html.Div("(total* excludes pause and hassler from its count)", style={'text-align':'center','margin-top':'5px'})

multi_analysis_focus_color_scale='viridis'

colors = {
    'work':'#2D7DD2', 
    'break':'#EEB902', 
    'meditation':'#F45D01', 
    'movement':'#97CC04',
    'pause' : '#212738',
    'next': '#FFA5A5',
    'hassler': '#440381',
    'total':'#565857',

    'goal':'#820263',
    'completed':'#D90368',

    'error':'#FCB0B3',
    'accent':'#2B9EB3',
    
    'tab_background': '#EBE9E9',
    'selected_tab_background': '#7A94A5',
    'disabled_tab_background' : '#EBE9E9'
    }

tabs_styles = {
    'height': '38px',
    'padding' : '2px',
    # 'margin-top':'0px' 
    }

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': colors['tab_background'],
    'padding': '6px',
    'fontWeight': 'bold',
    'text-align': 'center',
    'font-family': 'HelveticaNeue',
    'font-size': '14px',
    'font-weight': '600',
    'height': '38px',
    'margin-bottom': '2px',
    'margin-top': '2px',
    'margin-left': '2px',
    'margin-right': '2px'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': colors['selected_tab_background'],
    'color': 'white',
    'padding': '6px',
    'fontWeight': 'bold',
    'text-align': 'center',
    'font-family': 'HelveticaNeue',
    'font-size': '16px',
    'font-weight': '600',
    'height': '38px',
    'margin-bottom': '2px',
    'margin-top': '2px',
    'margin-left': '2px',
    'margin-right': '2px'
}

tab_disabled_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': colors['disabled_tab_background'],
    'color': 'grey',
    'padding': '6px',
    # 'fontWeight': 'bold',
    'text-align': 'center',
    'font-family': 'HelveticaNeue',
    'font-size': '14px',
    # 'font-weight': '600',
    'height': '38px',
    'margin-bottom': '2px',
    'margin-top': '2px',
    'margin-left': '2px',
    'margin-right': '2px'
}

########################################################################################################################################################################
########################################################################################################################################################################
########################################################################################################################################################################
########################################################################################################################################################################

##################################
#### HELPER FUNCTIONS        ####
##################################

def plot_bar_chart_goal_total(tasks, y_total, y_goal, title=None):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=tasks,
        y=y_goal,
        name='Goal',
        marker_color=colors['goal']
    ))

    fig.add_trace(go.Bar(
        x=tasks,
        y=y_total,
        name='Completed',
        marker_color=colors['completed']
    ))    

    fig.update_xaxes(
        title_text="Tasks",
        # showspikes=True, 
        # spikecolor="orange", 
        # spikesnap="cursor", 
        # spikethickness=0.75, 
        # spikemode="across"        
        )
    fig.update_yaxes(
        title_text="Time (minutes)",
        # showspikes=True, 
        # spikecolor="orange", 
        # spikesnap="cursor", 
        # spikethickness=0.75, 
        # spikemode="across"        
        )    

    fig.update_layout(spikedistance=1000, hoverdistance=1000)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=20))
    fig.update_layout(xaxis_fixedrange=True, yaxis_fixedrange=True,) ## DISABLE ZOOMING!
    fig.update_layout(
        legend=dict(y=-0.05, traceorder='normal', font_size=16),
        legend_orientation="h")
    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(barmode='group')
    
    if title is not None:
        fig.update_layout(title={
            'text': title,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    return fig

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
        if hours!='00':
            output = "{}:{}:{}".format(hours,minutes,seconds)
        else: 
            output = "{}:{}".format(minutes,seconds)
        return(output)

def current_info_html_output(task, focus, notes, block_length, block_time_elapsed, pause, pause_elapsed_timedelta, session_complete, zen_mode=False):

    if (session_complete is True):
        return html.Div(children=[
            html.H3(children=["Session completed!"], style={'text-align':'center', 'padding':'10px', 'margin':'10px'})
            ])

    if zen_mode is False:
        style_cell={'backgroundColor': '#CFCFCF',
                'font-family': 'HelveticaNeue',
                'font-size': '30px',        
                'fontWeight': 'bold',
                'textAlign': 'center',
                'border': '2px solid black',
            }
    else: 
        style_cell={ 'backgroundColor': '#CFCFCF',
            'font-family': 'HelveticaNeue',
            'font-size': '50px',        
            'fontWeight': 'bold',
            'textAlign': 'center',
            'border': '2px solid black',
        }

    if task is None:
        task=''
    if focus is None:
        focus=''
    if notes is None:
        notes=''   

    if (block_time_elapsed is not None) and (block_length is not None):
        progress_string = "{} / {}".format(timedelta_to_string(block_time_elapsed), timedelta_to_string(block_length))
    else: 
        # progress = '0'
        progress_string = "00:00 / 00:00"

    if pause is True:
        status = "PAUSED: {}".format(timedelta_to_string(pause_elapsed_timedelta))
        pause = 'yes'
    else: 
        status = "IN SESSION"
        pause='no'

    hidden_columns=['pause']
    if (notes is None) or (notes==''):
        hidden_columns=hidden_columns+['notes']

    if (focus is None) or (focus==''):
        hidden_columns=hidden_columns+['focus']

    data = dict(task=task, focus=focus, notes=notes,pause=pause, progress=progress_string, status=status)

    output = dash_table.DataTable(
        columns=[
            {'id':'task', 'name':'Task'},
            {'id':'focus', 'name':'Focus'},
            {'id':'notes', 'name':'Notes'},
            {'id':'progress', 'name':'Progress'},
            {'id':'status', 'name':'Status'},
            {'id':'pause', 'name':'Pause'}
            ],
        hidden_columns = hidden_columns,

        data=[data],
        style_data_conditional=[{'if': {'filter_query': '{task} = %()s && {pause} = no' % {"": task}}, 'backgroundColor': colors[task],'color': 'black'} for task in ['work', 'meditation','movement','break']]+[{'if': {'filter_query': '{pause} = yes'}, 'backgroundColor': colors['pause'],'color': 'white'}],
        style_header={'font-size':'20px'},
        style_cell=style_cell,

        css=[{"selector": ".show-hide", "rule": "display: none"}],
        style_data={
            'color': 'black',
            'whiteSpace': 'normal',
            'textAlign': 'center',
            'border': '2px solid black',
            },    
        )
    return output 

def info_table_from_schedule(data, tasks=['work', 'break', 'meditation', 'movement']):
    df=pd.DataFrame(data)
    info = df.groupby("task").sum()['length']
    info = info.to_dict()
    total = timedelta_to_string(datetime.timedelta(seconds=sum(info.values())*60))
    info = {k: timedelta_to_string(datetime.timedelta(seconds=v*60)) for k, v in info.items()}
    info['total']= total

    info_table = dash_table.DataTable(
        columns=[{'id':task, 'name':task} for task in tasks]+[{'id':'total', 'name':'total'}],
        data=[info],

        style_data_conditional = [{'if': {'column_id': task},'backgroundColor': colors[task]} for task in tasks],

        style_cell={ 
            'backgroundColor': '#CFCFCF',
            'font-family': 'HelveticaNeue',
            'font-size': '12px',        
            'fontWeight': 'bold',
            'textAlign': 'center',
            'border': '2px solid black',
        },
        style_data={
            'color': 'black',
            'whiteSpace': 'normal',
            'textAlign': 'center',
            'border': '2px solid black',
            # 'height': 'auto',
            # 'lineHeight': '15px'
            },    
        )
    return info_table

def tracker_schedule_helper(data=[], id='tracker-presession-schedule', cell_borders=True):
    deploy_schedule_table = dash_table.DataTable(
        id=id,
        columns=[
                {'id': 'task', 'name': 'Task', 'presentation': 'dropdown'},
                {'id': 'length', 'name': 'Length','presentation': 'input', 'type' :'numeric'},
                {'id': 'focus', 'name': 'Focus', 'presentation': 'input', 'type' :'text'},
                {'id': 'notes', 'name': 'Notes', 'presentation': 'input', 'type' :'text'},
                {'id': 'hassler', 'name': 'Hassler', 'presentation': 'dropdown'},
                {'id': 'applause', 'name': 'Applause', 'presentation': 'dropdown'},
                {'id': 'dinger', 'name': 'Dinger', 'presentation': 'input', 'type' :'numeric'},
            ],
        dropdown={
            'task': {'options' : [
                {'label': 'Work', 'value': 'work'},
                {'label': 'Break', 'value': 'break'},
                {'label': 'Meditation', 'value': 'meditation'},
                {'label': 'Movement', 'value': 'movement'}]},
            'hassler': {'options' : [
                {'label': 'Yes', 'value': True},
                {'label': 'No', 'value': False},]},
            'applause': {'options' : [
                {'label': 'Yes', 'value': True},
                {'label': 'No', 'value': False},]}  ,
            },
        data=data, 
        style_header={
            'backgroundColor': 'grey',
            'color' : 'black',
            'text-align': 'center',
            'font-family': 'HelveticaNeue',
            'font-size': '14px',        
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            # {'if': {'filter_query': '{task} = work'},   
            #     'backgroundColor': colors['work'],
            #     'color': 'black'},
            # {'if': {'filter_query': '{task} = break'},   
            #     'backgroundColor': colors['break'],
            #     'color': 'black'},
            # {'if': {'filter_query': '{task} = meditation'},   
            #     'backgroundColor': colors['meditation'],
            #     'color': 'black'},
            # {'if': {'filter_query': '{task} = movement'},   
            #     'backgroundColor': colors['movement'],
            #     'color': 'black'},  
        ## TASK COLORS: THIS IS EASIER TO READ, BUT MODULAR WAY TO CONDITIONALLY FORMAT THE CELLS BASED ON TASK (list comprehension)   
        ]+ [{'if': {'filter_query': '{task} = %()s' % {"": task}}, 'backgroundColor': colors[task],'color': 'black'} for task in tasks],
        
        css=[
            {'selector': '.Select-menu-outer','rule': '''--accent: black;'''},
            {'selector': '.Select-arrow','rule': '''--accent: black;'''},              
            ],
            
        style_cell = {
            'backgroundColor': '#CFCFCF',
            'font-family': 'HelveticaNeue',
            'font-size': '12px',        
            'fontWeight': 'bold', 
            'border': '2px solid black'},
        style_data={
            'color': 'black',
            'whiteSpace': 'normal',
            'textAlign': 'center'
        },    
        editable=False,
        style_as_list_view=True,
        persistence=True,
        )
    return deploy_schedule_table

def focus_table_from_schedule(schedule):
    if len(schedule)==0:
        return []
    df = pd.DataFrame(schedule)
    focus_totals = dict(df.groupby(["task",'focus']).sum().loc[:,'length'])
    focus_totals = {k:timedelta_to_string(datetime.timedelta(minutes=float(v))) for k,v in focus_totals.items()}
    focus_totals = [{'task': k[0], 'focus':k[1], 'total': v} for k,v in focus_totals.items()]
    focus_totals = sorted(focus_totals, key=lambda k: k['task'], reverse = True)
    return focus_totals
    
def task_table_from_schedule(schedule):
    if len(schedule)==0:
        return []
    df = pd.DataFrame(schedule)
    task_totals = dict(df.groupby("task").sum().loc[:,'length'])
    task_totals = {k:timedelta_to_string(datetime.timedelta(minutes=float(v))) for k,v in task_totals.items()}
    task_totals = [{'task':k, 'total': v} for k,v in task_totals.items()]
    task_totals = sorted(task_totals, key=lambda k: k['task'], reverse = True)
    task_totals.append({'task':'total','total':timedelta_to_string(datetime.timedelta(minutes=float(sum(df['length']))))})
    return task_totals

def task_and_focus_tables_4_schedule_and_template(task_table_id, focus_table_id):
    task_table = dash_table.DataTable(
        id=task_table_id,
        columns=[
                {'id': 'task', 'name': 'Task'},
                {'id': 'total', 'name': 'Total'},
                ],
        style_data_conditional = [{'if': {'filter_query': '{task} = %()s' % {"": task}}, 'backgroundColor': colors[task],'color': 'black'} for task in tasks],
        style_header={
            'backgroundColor': 'grey',
            'color' : 'black',
            'text-align': 'center',
            'font-family': 'HelveticaNeue',
            'font-size': '14px',        
            'fontWeight': 'bold'
        },
        data=[],
        style_cell={ 
                'backgroundColor': '#CFCFCF',
                'font-family': 'HelveticaNeue',
                'font-size': '12px',        
                'fontWeight': 'bold', 
                'border': '2px solid black',
            },
        style_data={
            'color': 'black',
            'whiteSpace': 'normal',
            'textAlign': 'center'
        },    
        css=[{"selector": ".show-hide", "rule": "display: none"}],
        row_deletable=False,
        row_selectable=False,
        editable=False,
        style_as_list_view=False,
        persistence=False,
        )   

    focus_table = dash_table.DataTable(
        id=focus_table_id,
        columns=[
                {'id': 'task', 'name': 'Task'},
                {'id': 'focus', 'name': 'Focus'},
                {'id': 'total', 'name': 'Total'},
                ],
        hidden_columns=['actual','goal'],
        style_data_conditional = [{'if': {'filter_query': '{task} = %()s' % {"": task}}, 'backgroundColor': colors[task],'color': 'black'} for task in ['work', 'meditation','movement', 'break']],
        style_header={
            'backgroundColor': 'grey',
            'color' : 'black',
            'text-align': 'center',
            'font-family': 'HelveticaNeue',
            'font-size': '14px',        
            'fontWeight': 'bold'
        },
        data=[],
        style_cell={ #### FIX THIS UP!
                'backgroundColor': '#CFCFCF',
                'font-family': 'HelveticaNeue',
                'font-size': '12px',        
                'fontWeight': 'bold', 
                'border': '2px solid black',
            },
        style_data={
            'color': 'black',
            'whiteSpace': 'normal',
            'textAlign': 'center'
        },    
        css=[{"selector": ".show-hide", "rule": "display: none"}],
        row_deletable=False,
        row_selectable=False,
        editable=False,
        style_as_list_view=False,
        persistence=False,
        )        
    return task_table, focus_table 

def cumulative_focus_chart(timeline_or_schedule, title=''):
    data = deepcopy(timeline_or_schedule)
    data = list(filter(lambda x: (x['task'] in tasks+['total']) and (x['length']>=0) and (type(x['length']) in [int, float] ), data ))

    task_focus_cum_list = [block['task']+": "+block['focus'] if ((block['focus'] is not None) and (block['focus'] is not '')) else block['task'] for block in data]

    for i in range(len(data)):
        data[i]['task']=task_focus_cum_list[i]

    unique_task_focus_pairs = list(set(task_focus_cum_list))
    unique_task_focus_pairs.sort(reverse=True)

    fig = cumulative_plot(data, title=title, tasks=unique_task_focus_pairs, cum_focus=True)
    return fig

############################################################################################################
####################################### HISTORY HELPERS ####################################################
############################################################################################################

def get_history(start_date, end_date):
    pg_local_port='5430'
    db_string = 'postgresql://postgres:docker@localhost:{}/postgres'.format(pg_local_port)
    engine = create_engine(db_string)
    connection = engine.connect()
    get_history_query = text("""
    SELECT * FROM history WHERE session_date BETWEEN '{}' AND '{}'
    """.format(start_date,end_date))
    history = connection.execute(get_history_query)
    history = list(history)
    return history

def history_compute_individual_task_data(session_date, session_id, session_name, timeline, schedule):
    timeline_df= pd.DataFrame(timeline)
    schedule_df= pd.DataFrame(schedule)
    totals_goal = dict(schedule_df.groupby("task").sum().loc[:,'length'])
    totals_goal['total']=sum(totals_goal.values())
    totals_goal['total*']=totals_goal['total']
    totals_session = dict(timeline_df.groupby("task").sum().loc[:,'length'])
    totals_session['total']=sum(totals_session.values())
    totals_session['total*']=sum([v if k not in ['pause','hassler','total'] else 0 for k,v in totals_session.items()])

    for task in tasks:
        if task not in totals_goal.keys():
            totals_goal[task]=0
        if task not in totals_session.keys():
            totals_session[task]=0

    output={}
    # task='work'
    for task in tasks+['total', 'total*']:
        if (task is not "pause") and (task is not "hassler"):
            actual = np.float64(totals_session[task])
            goal = np.float64(totals_goal[task])
            output[task+'_actual']= actual
            output[task+'_goal']= goal

            session_time_string = timedelta_to_string(datetime.timedelta(minutes=actual))
            goal_time_string = timedelta_to_string(datetime.timedelta(minutes=goal))

            output[task] = "{} / {}".format(session_time_string, goal_time_string)
        if (task is "pause") or (task is "hassler"):
            actual = np.float64(totals_session[task])
            output[task+'_actual'] = actual
            output[task] = timedelta_to_string(datetime.timedelta(minutes=actual))

    output['session_date'] = session_date
    output['session_id'] = session_id
    output['session_name'] = session_name
    return output

def format_multi_session_task_lines(selected_sessions):
    formatted_data_actual=defaultdict(list)
    formatted_data_goals=defaultdict(list)
    for session in selected_sessions:
        formatted_data_actual['session_date'].append(session['session_date'])
        formatted_data_actual['session_id'].append(session['session_id'])
        formatted_data_actual['session_name'].append(session['session_name'])

        formatted_data_goals['session_date'].append(session['session_date'])
        formatted_data_goals['session_id'].append(session['session_id'])   
        formatted_data_goals['session_name'].append(session['session_name'])


        for task in ['work', 'meditation','movement','break']+ ['hassler', 'pause']+['total']:
            formatted_data_actual[task].append(session[task+'_actual'])
        for task in ['work', 'meditation','movement','break']+ ['total']:
            formatted_data_goals[task].append(session[task+'_goal'])         
    
    formatted_data_actual=dict(formatted_data_actual)
    formatted_data_goals=dict(formatted_data_goals)
    return formatted_data_actual, formatted_data_goals

def multisession_task_overview_plot(actual, goals, title=None):
    fig = go.Figure()
    # actual: 
    for task in [task for task in ['work', 'meditation','movement','break']+ ['hassler', 'pause']+['total']]:
        fig.add_trace(
            go.Scattergl(
                x=list(range(len(actual['session_date']))), 
                y=actual[task], 
                # ticktext=actual['session_date'],
                name=task,
                # name=None,
                # name=task,
                line=dict(color=colors[task], width=2),
                # mode='lines',
                text=[timedelta_to_string(datetime.timedelta(minutes=x)) for x in actual[task]],
                hovertemplate="%{text}" 
                # hovertemplate="<b>{}</b><br>".format(task.upper()) + "%{text}" 
                    # "Time Elapsed: %{x} minutes <br>" +
                    # "Time Spent On Task: %{y}" +
                    # "<extra></extra>",
                )
                )    

    for task in [task for task in ['work', 'meditation','movement','break']+ ['total']]:
        fig.add_trace(
            go.Scattergl(
                x=list(range(len(goals['session_date']))), 
                y=goals[task], 
                name="GOAL - "+task,
                # ticktext=goals['session_date'],
                # name=None,
                # name=task,
                line=dict(color=colors[task], width=2, dash='dot'),
                # mode='lines',
                text=[timedelta_to_string(datetime.timedelta(minutes=x)) for x in goals[task]],
                hovertemplate="%{text}" 
                # hovertemplate="<b>{}</b><br>".format(task.upper()) + "%{text}" 
                    # "Time Elapsed: %{x} minutes <br>" +
                    # "Time Spent On Task: %{y}" +
                    # "<extra></extra>",
                )
                )  
    fig.update_layout(xaxis = dict(
        tickmode = 'array',
        tickvals = list(range(len(goals['session_date']))),
        ticktext = [session_date+"<br>"+str(session_name) for session_date, session_name in zip(goals['session_date'], goals['session_name']) ]
        )
    )

    fig.update_xaxes(
        showspikes=True, 
        spikecolor="orange", 
        spikesnap="cursor", 
        spikethickness=0.75, 
        spikemode="across")
    fig.update_yaxes(
        showspikes=True, 
        spikecolor="orange", 
        spikesnap="cursor", 
        spikethickness=0.75, 
        spikemode="across",
        side="left")
    
    fig.update_layout(xaxis_fixedrange=True, yaxis_fixedrange=True,) 
    if title is not None:
        fig.update_layout(title={
            'text': title,
            'y':0.85,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    fig.update_layout(uirevision='dataset')

    return fig

def compute_individual_focus_data(schedule, timeline, tasks=['work', 'meditation', 'movement', 'break']):
    if (len(schedule)==0) or (len(timeline)==0):
        return []
    timeline=pd.DataFrame(timeline)  
    schedule=pd.DataFrame(schedule)  

    timeline_focus_sums=timeline.groupby(["task",'focus']).sum().loc[:,'length']
    schedule_focus_sums=schedule.groupby(["task",'focus']).sum().loc[:,'length']
    schedule_focus_sums[0]

    output=[]
    for multi_index in list(schedule_focus_sums.index):
        new_entry = {}
        new_entry['task']=multi_index[0]
        new_entry['focus']=multi_index[1]
        new_entry['goal']=schedule_focus_sums[multi_index]
        if multi_index in timeline_focus_sums.index:
            new_entry['actual']=timeline_focus_sums[multi_index]
        else: 
            new_entry['actual']=0
        output.append(new_entry)

    sorted_output=[]
    for task in tasks:
        sorted_output = sorted_output + list(filter(lambda x: x['task']==task, output))

    if len(sorted_output)==0: return []

    data = list(map(convert_minutes_to_string, sorted_output))
    return data

def format_multi_session_focus_lines(selected_sessions):
    list_of_focus_dfs = [pd.DataFrame(compute_individual_focus_data(session['schedule'], session['timeline'])) for session in selected_sessions]
    list_of_focus_dfs = list(map(lambda x: x.drop('result',axis=1), list_of_focus_dfs))
    list_of_task_focus = []
    aggregate_dfs = []
    for df in list_of_focus_dfs:
        df['task'] = df['task']+": " + df['focus']
        list_of_task_focus= list_of_task_focus+ list(df['task'])
        df.drop('focus',axis=1,inplace=True)
        df.set_index(['task'], inplace=True)
        aggregate_dfs.append(df)
    tasks = list(set(list_of_task_focus))
    tasks.sort(reverse=True)

    formatted_data_actual=defaultdict(list)
    formatted_data_goals=defaultdict(list)
    for session in selected_sessions:
        formatted_data_actual['session_date'].append(session['session_date'])
        formatted_data_actual['session_id'].append(session['session_id'])
        formatted_data_actual['session_name'].append(session['session_name'])

        formatted_data_goals['session_date'].append(session['session_date'])
        formatted_data_goals['session_id'].append(session['session_id'])   
        formatted_data_goals['session_name'].append(session['session_name'])

    for df in aggregate_dfs:
        
        for task in tasks:
            if task in list(df.index):
                formatted_data_actual[task].append(df.loc[task,'actual'])
                formatted_data_goals[task].append(df.loc[task,'goal'])
            else: 
                formatted_data_actual[task].append(0)
                formatted_data_goals[task].append(0)

    formatted_data_actual=dict(formatted_data_actual)
    formatted_data_goals=dict(formatted_data_goals)
    return formatted_data_actual, formatted_data_goals, tasks

def multisession_focus_overview_plot(actual, goals, tasks, title=None):
    cmap = get_cmap(multi_analysis_focus_color_scale)

    fig = go.Figure()
    # actual: 
    i = 0 
    if len(actual)<=1:
        dt=0
    else:
        dt = floor(256/(len(actual)-4))
    for task in tasks:
        task_color='rgb'+str(cmap(i)[0:3])
        fig.add_trace(
            go.Scattergl(
                x=list(range(len(actual['session_date']))), 
                y=actual[task], 
                # ticktext=actual['session_date'],
                name=task,
                # name=None,
                # name=task,
                line=dict(color=task_color ,width=2),
                # mode='lines',
                text=[timedelta_to_string(datetime.timedelta(minutes=float(x))) for x in actual[task]],
                hovertemplate="%{text}" 
                # hovertemplate="<b>{}</b><br>".format(task.upper()) + "%{text}" 
                    # "Time Elapsed: %{x} minutes <br>" +
                    # "Time Spent On Task: %{y}" +
                    # "<extra></extra>",
                )
                )  
                
    ### UNCOMMENT TO PAIR UP ACTUAL AND GOAL / COMMENT TO SPLIT THEM
    #     i=i+dt
    # i = 0 
    # for task in tasks:
        task_color='rgb'+str(cmap(i)[0:3])
        fig.add_trace(
            go.Scattergl(
                x=list(range(len(goals['session_date']))), 
                y=goals[task], 
                name="GOAL - "+task,
                # ticktext=goals['session_date'],
                # name=None,
                # name=task,
                line=dict(color=task_color, width=2, dash='dot'),
                # mode='lines',
                text=[timedelta_to_string(datetime.timedelta(minutes=float(x))) for x in goals[task]],
                hovertemplate="%{text}" 
                # hovertemplate="<b>{}</b><br>".format(task.upper()) + "%{text}" 
                    # "Time Elapsed: %{x} minutes <br>" +
                    # "Time Spent On Task: %{y}" +
                    # "<extra></extra>",
                )
                )
        ### UNCOMMENT TO PAIR UP ACTUAL AND GOAL / COMMENT TO SPLIT THEM  
        i=i+dt
        
    fig.update_layout(xaxis = dict(
        tickmode = 'array',
        tickvals = list(range(len(goals['session_date']))),
        ticktext = [session_date+"<br>"+str(session_name) for session_date, session_name in zip(goals['session_date'], goals['session_name']) ]
        )
    )

    fig.update_xaxes(
        showspikes=True, 
        spikecolor="orange", 
        spikesnap="cursor", 
        spikethickness=0.75, 
        spikemode="across")
    fig.update_yaxes(
        showspikes=True, 
        spikecolor="orange", 
        spikesnap="cursor", 
        spikethickness=0.75, 
        spikemode="across",
        side="left")
    
    fig.update_layout(xaxis_fixedrange=True, yaxis_fixedrange=True,) 

    if title is not None:
        fig.update_layout(title={
            'text': title,
            'y':0.85,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    fig.update_layout(uirevision='dataset')

    return fig

def format_data_for_history_bar_chart(schedule, timeline, tasks=['work', 'meditation', 'movement', 'break', 'hassler','pause']):
    if (len(schedule)==0) or (len(timeline)==0):
        return [], [], []
    totals_goal = dict(pd.DataFrame(schedule).groupby("task").sum().loc[:,'length'])
    totals_timeline = dict(pd.DataFrame(timeline).groupby("task").sum().loc[:,'length'])
    
    y_goal = [ totals_goal[task] if task in totals_goal.keys() else 0 for task in tasks]
    y_timeline = [ totals_timeline[task] if task in totals_timeline.keys() else 0 for task in tasks]
    return tasks, y_timeline, y_goal

def task_and_focus_table_4_history(task_table_id, focus_table_id):
    task_table = dash_table.DataTable(
        id=task_table_id,
        columns=[
                {'id': 'task', 'name': 'Task'},
                {'id': 'result', 'name': 'Result'},
                {'id': 'actual', 'name': 'actual'},
                {'id': 'goal', 'name': 'goal'},
                # {'id': 'goal', 'name': 'Goal'},
                ],
        hidden_columns=['actual','goal'],
        style_data_conditional = [{'if': {'filter_query': '{task} = %()s' % {"": task}}, 'backgroundColor': colors[task],'color': 'black'} for task in ['work', 'meditation','movement', 'break']]+
            [{'if': {'filter_query': '{task} = %()s' % {"": stall}}, 'backgroundColor': colors[stall],'color': 'white'} for stall in ['hassler', 'pause']],
        style_header={
            'backgroundColor': 'grey',
            'color' : 'black',
            'text-align': 'center',
            'font-family': 'HelveticaNeue',
            'font-size': '14px',        
            'fontWeight': 'bold'
        },
        data=[],
        style_cell={
                'backgroundColor': '#CFCFCF',
                'font-family': 'HelveticaNeue',
                'font-size': '12px',        
                'fontWeight': 'bold', 
                'border': '2px solid black',
            },
        style_data={
            'color': 'black',
            'whiteSpace': 'normal',
            'textAlign': 'center'
        },    
        css=[{"selector": ".show-hide", "rule": "display: none"}],
        row_deletable=True,
        row_selectable='multi',
        selected_rows=list(range(7)),
        editable=False,
        style_as_list_view=False,
        persistence=False,
        )    

    focus_table = dash_table.DataTable(
        id=focus_table_id,
        columns=[
                {'id': 'task', 'name': 'Task'},
                {'id': 'focus', 'name': 'Focus'},
                {'id': 'result', 'name': 'Result'},
                {'id': 'actual', 'name': 'actual'},
                {'id': 'goal', 'name': 'goal'},
                # {'id': 'goal', 'name': 'Goal'},
                ],
        hidden_columns=['actual','goal'],
        style_data_conditional = [{'if': {'filter_query': '{task} = %()s' % {"": task}}, 'backgroundColor': colors[task],'color': 'black'} for task in tasks],
        style_header={
            'backgroundColor': 'grey',
            'color' : 'black',
            'text-align': 'center',
            'font-family': 'HelveticaNeue',
            'font-size': '14px',        
            'fontWeight': 'bold'
        },
        data=[],
        style_cell={ #### FIX THIS UP!
                'backgroundColor': '#CFCFCF',
                'font-family': 'HelveticaNeue',
                'font-size': '12px',        
                'fontWeight': 'bold', 
                'border': '2px solid black',
            },
        style_data={
            'color': 'black',
            'whiteSpace': 'normal',
            'textAlign': 'center'
        },    
        css=[{"selector": ".show-hide", "rule": "display: none"}],
        row_deletable=True,
        row_selectable='multi',
        selected_rows=[],
        editable=False,
        style_as_list_view=False,
        persistence=False,
        )    
    return task_table, focus_table

def compute_multi_focus_data(full_sessions, tasks=['work', 'meditation', 'movement', 'break']):

    list_of_foci = [pd.DataFrame(compute_individual_focus_data(session['schedule'], session['timeline'])) for session in full_sessions]
    list_of_foci= list(map(lambda x: x.drop('result',axis=1), list_of_foci))

    list_of_foci= [session.set_index(['task', 'focus']) for session in list_of_foci]

    df = reduce(lambda x,y: x.add(y, fill_value=0), list_of_foci)

    output=[]
    for multi_index in list(df.index):
        new_entry = {}
        new_entry['task']=multi_index[0]
        new_entry['focus']=multi_index[1]
        new_entry['actual'] = df.loc[multi_index,'actual']
        new_entry['goal'] = df.loc[multi_index,'goal']
        output.append(new_entry)
    
    sorted_output=[]
    for task in tasks:
        sorted_output = sorted_output + list(filter(lambda x: x['task']==task, output))

    if len(sorted_output)==0: return []

    multi_focus_data = list(map(convert_minutes_to_string, sorted_output))

    return multi_focus_data

def convert_minutes_to_string(x):
    actual_string=timedelta_to_string(datetime.timedelta(minutes=np.float64(x['actual'])))
    goal_string=timedelta_to_string(datetime.timedelta(minutes=np.float64(x['goal'])))
    if x['task'] in ['pause', 'hassler']:
        x['result'] = actual_string
    else:     
        x['result'] = actual_string+ " / "+goal_string 
    return x

############################################################################################################
##################################### MULTI TEMPLATE HELPERS ###############################################
############################################################################################################

def multi_template_individual_task(schedule):
    schedule_df= pd.DataFrame(schedule)
    totals_goal = dict(schedule_df.groupby("task").sum().loc[:,'length'])
    totals_goal['total']=sum(totals_goal.values())
    
    for task in tasks:
        if task not in totals_goal.keys():
            totals_goal[task]=0

    output={}
    for task in tasks+['total']:
        goal = np.float64(totals_goal[task])
        output[task+'_numeric']= goal
        goal_time_string = timedelta_to_string(datetime.timedelta(minutes=goal))
        output[task] = goal_time_string

    return output

def task_and_focus_table_4_multi_templates(task_table_id, focus_table_id):
    task_table = dash_table.DataTable(
        id=task_table_id,
        columns=[
                {'id': 'task', 'name': 'Task'},
                {'id': 'string', 'name': 'Goal'},
                # {'id': 'actual', 'name': 'actual'},
                {'id': 'numeric', 'name': 'goal'},
                # {'id': 'goal', 'name': 'Goal'},
                ],
        hidden_columns=['numeric'],
        style_data_conditional = [{'if': {'filter_query': '{task} = %()s' % {"": task}}, 'backgroundColor': colors[task],'color': 'black'} for task in ['work', 'meditation','movement', 'break']]+
            [{'if': {'filter_query': '{task} = %()s' % {"": stall}}, 'backgroundColor': colors[stall],'color': 'white'} for stall in ['hassler', 'pause']],
        style_header={
            'backgroundColor': 'grey',
            'color' : 'black',
            'text-align': 'center',
            'font-family': 'HelveticaNeue',
            'font-size': '14px',        
            'fontWeight': 'bold'
        },
        data=[],
        style_cell={
                'backgroundColor': '#CFCFCF',
                'font-family': 'HelveticaNeue',
                'font-size': '12px',        
                'fontWeight': 'bold', 
                'border': '2px solid black',
            },
        style_data={
            'color': 'black',
            'whiteSpace': 'normal',
            'textAlign': 'center'
        },    
        css=[{"selector": ".show-hide", "rule": "display: none"}],
        row_deletable=True,
        editable=False,
        style_as_list_view=False,
        persistence=False,
        )    

    focus_table = dash_table.DataTable(
        id=focus_table_id,
        columns=[
                {'id': 'task', 'name': 'Task'},
                {'id': 'focus', 'name': 'Focus'},
                {'id': 'string', 'name': 'Goal'},
                # {'id': 'actual', 'name': 'actual'},
                {'id': 'numeric', 'name': 'numeric'},
                # {'id': 'goal', 'name': 'Goal'},
                ],
        hidden_columns=['numeric'],
        style_data_conditional = [{'if': {'filter_query': '{task} = %()s' % {"": task}}, 'backgroundColor': colors[task],'color': 'black'} for task in tasks],
        style_header={
            'backgroundColor': 'grey',
            'color' : 'black',
            'text-align': 'center',
            'font-family': 'HelveticaNeue',
            'font-size': '14px',        
            'fontWeight': 'bold'
        },
        data=[],
        style_cell={ #### FIX THIS UP!
                'backgroundColor': '#CFCFCF',
                'font-family': 'HelveticaNeue',
                'font-size': '12px',        
                'fontWeight': 'bold', 
                'border': '2px solid black',
            },
        style_data={
            'color': 'black',
            'whiteSpace': 'normal',
            'textAlign': 'center'
        },    
        css=[{"selector": ".show-hide", "rule": "display: none"}],
        row_deletable=True,
        # row_selectable='multi',
        selected_rows=[],
        editable=False,
        style_as_list_view=False,
        persistence=False,
        )    
    return task_table, focus_table

def multi_temp_task_table_calc(non_empty_rows):
    """
    computes aggregate task table from a list of non_empty_rows from multi_temp_table
    """
    multi_task_data = []
    for task in ['work','meditation','movement','break','total']:    
        row = {}
        row['task']=task
        row[task+'_numeric']=sum([session[task+'_numeric'] for session in non_empty_rows])
        if row[task+'_numeric']==0:
            continue
        row['string']=timedelta_to_string(datetime.timedelta(minutes=np.float64(row[task+'_numeric'])))
        multi_task_data.append(row)
    return multi_task_data

def multi_temp_compute_individual_focus_data(schedule):
    if (len(schedule)==0):
        return []
    schedule=pd.DataFrame(schedule)  
    schedule_focus_sums=schedule.groupby(["task",'focus']).sum().loc[:,'length']
    output=[]
    for multi_index in list(schedule_focus_sums.index):
        new_entry = {}
        new_entry['task']=multi_index[0]
        new_entry['focus']=multi_index[1]
        new_entry['numeric']=schedule_focus_sums[multi_index]
        output.append(new_entry)

    sorted_output=[]
    for task in tasks:
        sorted_output = sorted_output + list(filter(lambda x: x['task']==task, output))

    return sorted_output

def multi_temp_focus_table_calc(list_of_templates, tasks=['work', 'meditation', 'movement', 'break']):
    """ eats list of template_id's and spits out a list of foci/task aggregates
    """
    
    def compute_multi_focus_data(list_of_focus_data):
        if len(list_of_focus_data)==0:
            return []
        list_of_foci = [pd.DataFrame(focus_data) for focus_data in list_of_focus_data]
        list_of_foci= [foci.set_index(['task', 'focus']) for foci in list_of_foci]

        df = reduce(lambda x,y: x.add(y, fill_value=0), list_of_foci)

        output=[]
        for multi_index in list(df.index):
            new_entry = {}
            new_entry['task']=multi_index[0]
            new_entry['focus']=multi_index[1]
            new_entry['numeric'] = df.loc[multi_index,'numeric']        
            new_entry['string'] = timedelta_to_string(datetime.timedelta(minutes=np.float64(new_entry['numeric'])))
            output.append(new_entry)
        
        sorted_output=[]
        for task in tasks:
            sorted_output = sorted_output + list(filter(lambda x: x['task']==task, output))

        return sorted_output

    list_of_schedules = [wt.templates_dict[x] for x in list_of_templates]
    list_of_focus_data = [multi_temp_compute_individual_focus_data(schedule) for schedule in list_of_schedules]
    output = compute_multi_focus_data(list_of_focus_data)

    return output

def multi_template_task_overview_plot(goals, title=None):
    fig = go.Figure()
    if (goals is None) or (len(goals)==0):
        return fig
    for task in [task for task in ['work', 'meditation','movement','break']+ ['total']]:
        fig.add_trace(
            go.Scattergl(
                x=list(range(len(goals['template_id']))), 
                y=goals[task], 
                name=task.capitalize(),
                # ticktext=goals['session_date'],
                # name=None,
                # name=task,
                line=dict(color=colors[task], width=2, dash='dot'),
                # mode='lines',
                text=[timedelta_to_string(datetime.timedelta(minutes=x)) for x in goals[task]],
                hovertemplate="%{text}" 
                # hovertemplate="<b>{}</b><br>".format(task.upper()) + "%{text}" 
                    # "Time Elapsed: %{x} minutes <br>" +
                    # "Time Spent On Task: %{y}" +
                    # "<extra></extra>",
                )
                )  
    fig.update_layout(xaxis = dict(
        tickmode = 'array',
        tickvals = list(range(len(goals['template_id']))),
        ticktext = [template_id+"<br>"+str(session_name) for template_id, session_name in zip(goals['template_id'], goals['session_name']) ]
        )
    )

    fig.update_xaxes(
        showspikes=True, 
        spikecolor="orange", 
        spikesnap="cursor", 
        spikethickness=0.75, 
        spikemode="across")
    fig.update_yaxes(
        showspikes=True, 
        spikecolor="orange", 
        spikesnap="cursor", 
        spikethickness=0.75, 
        spikemode="across",
        side="left")

    if title is not None:
        fig.update_layout(title={
            'text': title,
            'y':0.85,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    fig.update_layout(uirevision='dataset')

    return fig

def format_multi_temp_dist_task_data(output, data_list):
    multi_session_task_line_data=defaultdict(list)
    for j in range(len(output)):
        session = output[j]
        if len(session)==0:
            continue

        new_row={}
        template_id = session['template_id']

        session_number_string = str(j).rjust(2, '0')
        if 'session_name' in data_list[j].keys():
            session_name = session_number_string+" - "+data_list[j]['session_name']
        else: 
            session_name = session_number_string+" - unnamed"

        multi_session_task_line_data['template_id'].append(template_id)
        multi_session_task_line_data['session_name'].append(session_name)   
        
        for task in ['work', 'meditation','movement','break']+ ['total']:
            multi_session_task_line_data[task].append(session[task+'_numeric'])  
    return dict(multi_session_task_line_data)  

def format_multi_temp_dist_focus_data(data_list):
    data_list = list(filter(lambda x: 'template_id' in x.keys() , data_list))
    list_of_schedules = []
    for j in range(len(data_list)):
        datum = data_list[j]
        new_row = {}
        if (datum is not None) and (len(datum)>0) and ('template_id' in datum.keys()) and (datum['template_id'] is not None):
            new_row['template_id']=datum['template_id']
            new_row['schedule']=wt.templates_dict[datum['template_id']]
            
            session_number_string = str(j).rjust(2, '0')
            if 'session_name' in datum.keys():
                session_name = session_number_string+" - "+datum['session_name']
            else: 
                session_name = session_number_string+" - unnamed"
            
            new_row['session_name'] = session_name
            list_of_schedules.append(new_row)

    list_of_dfs = [pd.DataFrame(multi_temp_compute_individual_focus_data(schedule['schedule'])) for schedule in list_of_schedules]
    list_of_task_focus = []
    aggregate_dfs = []
    for df in list_of_dfs:
        df['task'] = df['task']+": " + df['focus']
        list_of_task_focus = list_of_task_focus+ list(df['task'])
        df.drop('focus',axis=1,inplace=True)
        df.set_index(['task'], inplace=True)
        aggregate_dfs.append(df)
    tasks = list(set(list_of_task_focus))
    tasks.sort(reverse=True)

    formatted_data_goals=defaultdict(list)
    for schedule in list_of_schedules:
        formatted_data_goals['template_id'].append(schedule['template_id'])
        formatted_data_goals['session_name'].append(schedule['session_name'])

    for df in aggregate_dfs:
        for task in tasks:
            if task in list(df.index):
                formatted_data_goals[task].append(df.loc[task,'numeric'])
            else: 
                formatted_data_goals[task].append(0)

    formatted_data_goals=dict(formatted_data_goals)
    return formatted_data_goals, tasks

def multi_temp_focus_overview_plot(goals, tasks, title=None):
    if len(goals)==0:
        return go.Figure()
    cmap = get_cmap(multi_analysis_focus_color_scale)

    fig = go.Figure()
    i = 0 
    if len(goals)==1:
        dt=0
    else:
        dt = floor(256/(len(goals)-3))

    for task in tasks:
        task_color='rgb'+str(cmap(i)[0:3])
        fig.add_trace(
            go.Scattergl(
                x=list(range(len(goals['template_id']))), 
                y=goals[task], 
                name=task,
                # ticktext=goals['session_date'],
                # name=None,
                # name=task,
                line=dict(color=task_color, width=2, dash='dot'),
                # mode='lines',
                text=[timedelta_to_string(datetime.timedelta(minutes=float(x))) for x in goals[task]],
                hovertemplate="%{text}" 
                # hovertemplate="<b>{}</b><br>".format(task.upper()) + "%{text}" 
                    # "Time Elapsed: %{x} minutes <br>" +
                    # "Time Spent On Task: %{y}" +
                    # "<extra></extra>",
                )
                )
        i=i+dt
        
    fig.update_layout(xaxis = dict(
        tickmode = 'array',
        tickvals = list(range(len(goals['template_id']))),
        ticktext = [template_id+"<br>"+str(session_name) for template_id, session_name in zip(goals['template_id'], goals['session_name']) ]
        )
    )

    fig.update_xaxes(
        showspikes=True, 
        spikecolor="orange", 
        spikesnap="cursor", 
        spikethickness=0.75, 
        spikemode="across")
    fig.update_yaxes(
        showspikes=True, 
        spikecolor="orange", 
        spikesnap="cursor", 
        spikethickness=0.75, 
        spikemode="across",
        side="left")

    if title is not None:
        fig.update_layout(title={
            'text': title,
            'y':0.85,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    fig.update_layout(uirevision='dataset')

    return fig

def return_template_names(non_empty_rows, primary_name):
    if (primary_name is not None) and (primary_name!=''):
        primary_name=primary_name.strip()
    template_names = []
    for j in range(len(non_empty_rows)):
        session_number_string = str(j).rjust(2, '0')
        if 'session_name' in non_empty_rows[j].keys():
            if non_empty_rows[j]['session_name']!='':
                session_name = session_number_string+" - "+non_empty_rows[j]['session_name']
        else: 
            session_name = session_number_string
        template_names.append(session_name)
    if (primary_name is not None) and (primary_name!=''):
        template_names = [primary_name+' - '+template_name for template_name in template_names]
    return template_names

############################################################################################################
########################################## HISTORY COMPONENTS ##############################################
############################################################################################################

tomorrow=datetime.datetime.now()

date_selector_html = html.Div(children=[
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=datetime.datetime(2020, 1, 1),
        max_date_allowed=tomorrow,
        initial_visible_month=tomorrow,
        end_date=datetime.date.today(),
        show_outside_days=True,
    ),]
    )

individual_multiple_radio = html.Div(dcc.RadioItems(
    id='individual-multiple-radio',
    options=[
        {'label': 'Single-Session', 'value': 'individual'},
        {'label': 'Multi-Sessions', 'value': 'multiple'}
    ],
    value='individual',
    labelStyle={'display': 'inline-block'}
    )
    )

### HISTORY INDIVIDUAL BUTTONS
history_individual_buttons_html = html.Div(
    children=[
        html.Button(children='Save to Templates', id='history-save-schedule-to-templates', n_clicks=0),
        html.Div(id='save-template-output')
        ],
    style={'width':'90%', 'text-align':'center','margin':'1px', 'display':'inline-block'})

multi_analysis_select_all = html.Div(dcc.Checklist(
    id='multi-select-all',
    options=[
        {'label': 'Select All', 'value': 'select-all'},
    ],
    value=[],
    labelStyle={'display': 'inline-block'}
    ),
    style={'margin-left':'10%'}
    )  

history_date_and_delete = html.Div(
    # id='tracker-session-summary-tables',
    children=[
        html.Div([date_selector_html, individual_multiple_radio, multi_analysis_select_all], className="six columns"),
        html.Div([html.Button(children='Delete Selected', id='history-delete-selected-button', n_clicks=0, style={'margin-top':'10px'}),html.Button(children='Refresh', id='history-refresh-dates', n_clicks=0),  html.Div(id='history-deleted-message')], className="six columns"),
        ], className="row", style={'width':'50%','margin-left':'25%', 'margin-bottom':'10px', 'margin-top':'10px'})   

delete_confirmation = dcc.ConfirmDialog(
        id='history-delete-selected-confirm',
    )

### MAIN HISTORY TABLE
history_table = dash_table.DataTable(
    id='history-table',
    columns=[
            {'id': 'session_id', 'name': '#id'},
            {'id': 'session_date', 'name': 'Date'},
            {'id': 'session_name', 'name': 'Name id'}]+
            [{'id': task, 'name': task.capitalize()} for task in ['work','meditation', 'movement','break']]+
            [{'id': task, 'name': task.capitalize()} for task in ['total*']]+
            [{'id': task, 'name': task.capitalize()} for task in ['pause','hassler']]+
            [{'id': task, 'name': task.capitalize()} for task in ['total']]+
            [{'id': task+'_actual', 'name': task.capitalize(), 'type':'numeric'} for task in ['work', 'meditation','movement','break']+['total','total*']]+
            [{'id': task+'_goal', 'name': task.capitalize()} for task in ['work', 'meditation','movement','break']+['total','total*']],

    hidden_columns = [task+'_actual' for task in ['work', 'meditation','movement','break']+['total','total*']]+
        [task+'_goal' for task in ['work', 'meditation','movement','break']+['total','total*']],
    data = [],
    selected_rows = [],
    style_data_conditional = [{'if': {'column_id': task},'backgroundColor': colors[task]} for task in tasks]+
        [{'if': {'column_id': stall},'color': 'white'} for stall in ['hassler', 'pause']],
    style_header={
        'backgroundColor': 'grey',
        'color' : 'black',
        'text-align': 'center',
        'font-family': 'HelveticaNeue',
        'font-size': '14px',        
        'fontWeight': 'bold'
    },

    style_cell={
            'backgroundColor': '#CFCFCF',
            'font-family': 'HelveticaNeue',
            'font-size': '12px',        
            'fontWeight': 'bold', 
            'border': '2px solid black',
        },
    style_data={
        'color': 'black',
        'whiteSpace': 'normal',
        'textAlign': 'center'
    },    
    css=[{"selector": ".show-hide", "rule": "display: none"}],
    row_deletable=True,
    row_selectable='single',
    editable=False,
    style_as_list_view=True,
    persistence=True,
    
    )
history_table_html = html.Div(
    children=[history_table],
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'})

#### #### #### #### #### #### #### #### ####
### INDIVIDUAL ANALYSIS COMPONENTS: #### ###
#### #### #### #### #### #### #### #### ####
history_individual_checklist = html.Div(dcc.Checklist(
    id='history-individual-checklist',
    options=[
        {'label': 'Summary Bar Charts', 'value': 'summary-charts'},
        {'label': 'Summary Tables', 'value': 'summary-tables'},
        {'label': 'Schedule', 'value': 'schedule'},
        {'label': 'Schedule Task Plot', 'value': 'schedule-task'},
        {'label': 'Timeline Task Plot', 'value': 'timeline-task'},
        {'label': 'Schedule Focus Plot', 'value': 'schedule-focus'},
        {'label': 'Timeline Focus Plot', 'value': 'timeline-focus'},
    ],value=['summary-charts', 'summary-tables'],labelStyle={'display': 'inline-block'}),
        )

history_individual_controls_html = html.Div(
    id='history-individual-controls',
    children=[
        html.Div([history_individual_checklist], className="six columns"),
        html.Div([history_individual_buttons_html], className="six columns"),
        ], className="row", style={'width':'50%','margin-left':'25%', 'margin-bottom':'10px'})    

# HISTORY INDIVIDUAL SCHEDULE TASK CHART
history_individual_schedule_task_chart_html = html.Div(
    id='history-individual-schedule-task-chart-html',
    children=[dcc.Graph(id='history-individual-schedule-task-chart',config={'displayModeBar': False})],
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

# HISTORY INDIVIDUAL SCHEDULE FOCUS CHART
history_individual_schedule_focus_chart_html = html.Div(
    id='history-individual-schedule-focus-chart-html',
    children=[dcc.Graph(id='history-individual-schedule-focus-chart',config={'displayModeBar': False})],
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

# HISTORY INDIVIDUAL TIMELINE TASK CHART
history_individual_timeline_task_chart_html = html.Div(
    id='history-individual-timeline-task-chart-html',
    children=[dcc.Graph(id='history-individual-timeline-task-chart',config={'displayModeBar': False})],
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

# HISTORY INDIVIDUAL TIMELINE FOCUS CHART
history_individual_timeline_focus_chart_html = html.Div(
    id='history-individual-timeline-focus-chart-html',
    children=[dcc.Graph(id='history-individual-timeline-focus-chart',config={'displayModeBar': False})],
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

history_individual_focus_bar_chart = dcc.Graph(id='history-individual-focus-bar-chart',config={'displayModeBar': False},)
history_individual_task_bar_chart = dcc.Graph(id='history-individual-task-bar-chart',config={'displayModeBar': False},)

history_individual_task_info_table, history_individual_focus_table = task_and_focus_table_4_history('history-individual-task-table', 'history-individual-focus-table')

# INDIVIDUAL SUMMARY TABLES 
history_individual_task_and_focus_tables_html = html.Div(
    id='individual-summary-tables',
    children=[
        html.Div([history_individual_task_info_table, total_star_message], className="six columns"),
        html.Div([history_individual_focus_table], className="six columns"),
        ], className="row", style={'width':'90%','margin-left':'5%'})   

# INDIVIDUAL BAR CHARTS
history_individual_task_and_focus_bar_charts_html = html.Div(
    id='individual-bar-charts',
    children=[
        html.Div([history_individual_task_bar_chart], className="six columns"),
        html.Div([history_individual_focus_bar_chart], className="six columns"),
        ], className="row", style={'width':'90%','margin-left':'5%'})    

history_schedule_table_html = html.Div(
    id='history-schedule-html', 
    children=[tracker_schedule_helper(data=[],id='history-schedule')],
    style={
        'width':'90%', 
        'border': '2px solid black',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
        )

#### #### #### #### #### #### #### #### ####
#### MULTI ANALYSIS COMPONENTS #### #### ###
#### #### #### #### #### #### #### #### #### 

# MULTI CHECK LIST
history_multi_checklist = html.Div(dcc.Checklist(
    id='history-multi-checklist',
    options=[
        {'label': 'Summary Bar Charts', 'value': 'summary-bar-charts'},
        {'label': 'Summary Tables', 'value': 'summary-tables'},
        {'label': 'Dist. Task Chart', 'value': 'dist-task-chart'},
        {'label': 'Cum. Task Chart', 'value': 'cum-task-chart'},
        {'label': 'Dist. Focus Chart', 'value': 'dist-focus-chart'},
        {'label': 'Cum. Focus Chart', 'value': 'cum-focus-chart'},        
    ],value=['summary-charts', 'summary-tables'],labelStyle={'display': 'inline-block'}),
    style={
        'text-align':'center',
        # 'border': '1px solid black',
        'margin-bottom':'2px',
        'margin-top':'2px',
        'width':'30%',
        'margin-left': 'auto',
        'margin-right': 'auto'}
        )

# MULTI DIST TASK CHART
history_multi_dist_task_chart_html = html.Div(
    id='history-multi-dist-task-chart-html',
    children=[dcc.Graph(id='history-multi-dist-task-chart', config={'displayModeBar': False})],
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )
# MULTI CUM TASK CHART
history_multi_cum_task_chart_html = html.Div(
    id='history-multi-cum-task-chart-html',
    children=[dcc.Graph(id='history-multi-cum-task-chart',config={'displayModeBar': False})],
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

# MULTI DIST FOCUS CHART
history_multi_dist_focus_chart_html = html.Div(
    id='history-multi-dist-focus-chart-html',
    children=[dcc.Graph(id='history-multi-dist-focus-chart',config={'displayModeBar': False})],
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )
# MULTI CUM FOCUS CHART
history_multi_cum_focus_chart_html = html.Div(
    id='history-multi-cum-focus-chart-html',
    children=[dcc.Graph(id='history-multi-cum-focus-chart',config={'displayModeBar': False})],
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

history_multi_task_info_table, history_multi_focus_table = task_and_focus_table_4_history('history-multi-task-table', 'history-multi-focus-table')

# MULTI SUMMARY TABLES
history_multi_task_and_focus_tables_html = html.Div(
    id='multi-summary-tables',
    children=[
        html.Div([history_multi_task_info_table,total_star_message], className="six columns"),
        html.Div([history_multi_focus_table], className="six columns"),
        ], className="row", style={'width':'90%','margin-left':'5%'})   

history_multi_focus_bar_chart = dcc.Graph(id='history-multi-focus-bar-chart',config={'displayModeBar': False},)
history_multi_task_bar_chart = dcc.Graph(id='history-multi-task-bar-chart',config={'displayModeBar': False},)

# side by side bar charts
# MULTI BAR CHARTS
history_multi_task_and_focus_bar_charts_html = html.Div(
    id='multi-bar-charts',
    children=[
        html.Div([history_multi_task_bar_chart], className="six columns"),
        html.Div([history_multi_focus_bar_chart], className="six columns"),
        ], className="row", style={'width':'90%','margin-left':'5%'})    

### INDIVIDUAL ANALAYSIS PAGE 
individual_analysis_page_html = html.Div(
    id='individual-analysis-page', 
    children=[
        delete_confirmation,

        history_individual_controls_html,
        history_individual_task_and_focus_bar_charts_html,
        history_individual_task_and_focus_tables_html,
        history_schedule_table_html,
        history_individual_schedule_task_chart_html,
        history_individual_timeline_task_chart_html,
        history_individual_schedule_focus_chart_html,
        history_individual_timeline_focus_chart_html
        ],
    )


### MULTI ANALAYSIS PAGE 
multi_analysis_page_html = html.Div(
    id='multi-analysis-page',
    children=[
        history_multi_checklist,
        history_multi_task_and_focus_bar_charts_html,
        history_multi_task_and_focus_tables_html,
        history_multi_dist_task_chart_html,
        history_multi_cum_task_chart_html,     
        history_multi_dist_focus_chart_html,   
        history_multi_cum_focus_chart_html
    ],
    )

history_page = html.Div(children=[
    history_date_and_delete,
    history_table_html,
    individual_analysis_page_html,
    multi_analysis_page_html
    ])

####################################################
####################################################
# TRACKER SESSION COMPONENTS 
####################################################
####################################################

tracker_timeline_task_chart = dcc.Graph(id='tracker-timeline-task-chart',config={'displayModeBar': False})
tracker_timeline_task_chart_html = html.Div(
    id='tracker-timeline-task-chart-html',
    children=tracker_timeline_task_chart,
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

tracker_timeline_focus_chart = dcc.Graph(id='tracker-timeline-focus-chart',config={'displayModeBar': False})
tracker_timeline_focus_chart_html = html.Div(
    id='tracker-timeline-focus-chart-html',
    children=tracker_timeline_focus_chart,
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

tracker_session_schedule_task_chart = dcc.Graph(id='tracker-session-schedule-task-chart',config={'displayModeBar': False})
tracker_session_schedule_task_chart_html = html.Div(
    id='tracker-session-schedule-task-chart-html',
    children=tracker_session_schedule_task_chart,
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

tracker_session_schedule_focus_chart = dcc.Graph(id='tracker-session-schedule-focus-chart',config={'displayModeBar': False})
tracker_session_schedule_focus_chart_html = html.Div(
    id='tracker-session-schedule-focus-chart-html',
    children=tracker_session_schedule_focus_chart,
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

tracker_session_schedule = html.Div(
    id='tracker-session-schedule-html', 
    children=[tracker_schedule_helper(data=[], id='tracker-session-schedule', cell_borders=False), ],
    style={
        'width':'90%', 
        'border': '2px solid black',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
        )

tracker_focus_bar_chart = dcc.Graph(id='tracker-focus-bar-chart',config={'displayModeBar': False},)
tracker_task_bar_chart = dcc.Graph(id='tracker-task-bar-chart',config={'displayModeBar': False},)

tracker_task_info_table = dash_table.DataTable(
    id='tracker-task-table',
    columns=[
            {'id': 'task', 'name': 'Task'},
            {'id': 'result', 'name': 'Result'},
            {'id': 'actual', 'name': 'actual'},
            {'id': 'goal', 'name': 'goal'},
            ],
    hidden_columns=['actual','goal'],
    style_data_conditional = [{'if': {'filter_query': '{task} = %()s' % {"": task}}, 'backgroundColor': colors[task],'color': 'black'} for task in ['work', 'meditation','movement', 'break']]+
        [{'if': {'filter_query': '{task} = %()s' % {"": stall}}, 'backgroundColor': colors[stall],'color': 'white'} for stall in ['hassler', 'pause']],
    style_header={
        'backgroundColor': 'grey',
        'color' : 'black',
        'text-align': 'center',
        'font-family': 'HelveticaNeue',
        'font-size': '14px',        
        'fontWeight': 'bold'
    },
    data=[],
    style_cell={ 
            'backgroundColor': '#CFCFCF',
            'font-family': 'HelveticaNeue',
            'font-size': '12px',        
            'fontWeight': 'bold', 
            'border': '2px solid black',
        },
    style_data={
        'color': 'black',
        'whiteSpace': 'normal',
        'textAlign': 'center'
    },    
    css=[{"selector": ".show-hide", "rule": "display: none"}],
    row_deletable=False,
    selected_rows=[],
    row_selectable='multi',
    editable=False,
    style_as_list_view=False,
    persistence=False,
    )    
tracker_focus_table = dash_table.DataTable(
    id='tracker-focus-table',
    columns=[
            {'id': 'task', 'name': 'Task'},
            {'id': 'focus', 'name': 'Focus'},
            {'id': 'result', 'name': 'Result'},
            {'id': 'actual', 'name': 'actual'},
            {'id': 'goal', 'name': 'goal'},
            # {'id': 'goal', 'name': 'Goal'},
            ],
    hidden_columns=['actual','goal'],
    style_data_conditional = [{'if': {'filter_query': '{task} = %()s' % {"": task}}, 'backgroundColor': colors[task],'color': 'black'} for task in tasks],
    style_header={
        'backgroundColor': 'grey',
        'color' : 'black',
        'text-align': 'center',
        'font-family': 'HelveticaNeue',
        'font-size': '14px',        
        'fontWeight': 'bold'
    },
    data=[],
    style_cell={ 
            'backgroundColor': '#CFCFCF',
            'font-family': 'HelveticaNeue',
            'font-size': '12px',        
            'fontWeight': 'bold', 
            'border': '2px solid black',
        },
    style_data={
        'color': 'black',
        'whiteSpace': 'normal',
        'textAlign': 'center'
    },    
    css=[{"selector": ".show-hide", "rule": "display: none"}],
    row_deletable=False,
    selected_rows=[0],
    row_selectable='multi',
    editable=False,
    style_as_list_view=False,
    persistence=False,
    )    


# side by side tables
tracker_task_and_focus_tables_html = html.Div(
    id='tracker-session-summary-tables',
    children=[
        html.Div([tracker_task_info_table, total_star_message], className="six columns"),
        html.Div([tracker_focus_table], className="six columns"),
        ], className="row", style={'width':'90%','margin-left':'5%'})   
# side by side bar charts
tracker_task_and_focus_bar_charts_html = html.Div(
    id='tracker-session-bar-charts',
    children=[
        html.Div([tracker_task_bar_chart], className="six columns"),
        html.Div([tracker_focus_bar_chart], className="six columns"),
        ], className="row", style={'width':'90%','margin-left':'5%'})    

########################

# TRACKER BUTTONS
start_button = html.Button(children='Pause/Unpause',accessKey='P', id='tracker-start-button', n_clicks=0)
next_button = html.Button(children='Next', id='tracker-next', n_clicks=0)
tracker_finish_button = html.Button(children='Finish Session', id='tracker-finish', n_clicks=0)
record_button = html.Button(children='Record Session', id='tracker-record', n_clicks=0)

record_button_and_input = html.Div(children=[
    dcc.Input(id='input-save-session', type="text", placeholder='session name (optional)', persistence=False),
    record_button],
    style={'margin':'2px'})

tracker_buttons_html = html.Div(
    children=[
        start_button,
        next_button,
        tracker_finish_button,
        record_button_and_input
        ],
    style={ 'margin-top':'5px'}
    )

tracker_session_zenmode_checklist = html.Div(dcc.Checklist(
    id='tracker-session-zen-mode',
    options=[{'label': 'Zen Mode', 'value': 'tracker-zen-mode'}],
    value=[],
    labelStyle={'display': 'inline-block'}
    ),
    style={'text-align':'center'})

tracker_session_checklist = html.Div(dcc.Checklist(
    id='tracker-session-checklist',
    options=[
        {'label': 'Summary Tables', 'value': 'summary-tables'},
        {'label': 'Summary Bar Plots', 'value': 'summary-bars'},
        {'label': 'Timeline Task Plot', 'value': 'timeline-task'},
        {'label': 'Timeline Focus Plot', 'value': 'timeline-focus'},
        {'label': 'Schedule Task Plot', 'value': 'schedule-task'},
        {'label': 'Schedule Focus Plot', 'value': 'schedule-focus'},
        {'label': 'Schedule', 'value': 'tracker-schedule'},

    ],
    value=['summary-tables'],
    labelStyle={'display': 'inline-block'}
    ),
    style={'text-align':'center', 'margin-top':'5px', 'margin-bottom':'5px'})

tracker_session_checklist_and_buttons = html.Div(
    children=[
        html.Div([tracker_session_checklist, tracker_session_zenmode_checklist], className="six columns"),
        html.Div([tracker_buttons_html], className="six columns"),
        ], className="row", style={'width':'90%','margin-left':'5%', 'margin-top':'10px', 'border':'1px solid black','display':'inline-block'}) 

confirm_finish = dcc.ConfirmDialog(
    id='confirm-finish',
    message='End session?',
    submit_n_clicks=0
    )

confirm_record = dcc.ConfirmDialog(
    id='confirm-record',
    message='Record session?',
    submit_n_clicks=0
    )

current_info_html = html.Div(id='current-info-html', style={'width':'90%', 'margin-left': '5%', 'margin-right': '5%', 'margin-top':'10px','margin-bottom':'10px','display':'inline-block','border':'1px solid black'})

hidden_div = html.Div(id='hidden-div', style={'display':'none'})
hidden_div_2 = html.Div(id='hidden-div-2', style={'display':'none'})
hidden_div_3 = html.Div(id='hidden-div-3', style={'display':'none'})
hidden_div_4 = html.Div(id='hidden-div-4', style={'display':'none'})
hidden_div_5 = html.Div(id='hidden-div-5', style={'display':'none'})

interval_charts = dcc.Interval(id='interval-charts', interval=10000)
interval_hassler = dcc.Interval(id='interval-hassler', interval=1000)
interval_info = dcc.Interval(id='interval-info', interval=1000)

input_hassler = dcc.Input(id="input-hassler", type="text", placeholder="", persistence=False, autoFocus=True)
input_hassler_html = html.Div(children=[
    html.H4("Type Here:"),
    html.Div(children=input_hassler)
    ], 
    id='input-hassler-html',
    style={
        'text-align': 'center',
        'padding': '70px'
        },
)

block_page = html.Div(
    children=[
        # invisible stuff:
        confirm_finish,
        confirm_record,
        hidden_div,
        hidden_div_2,
        hidden_div_3,
        hidden_div_4,
        interval_charts,
        interval_hassler,
        interval_info,

        # visible stuff: 
        current_info_html,
        
        tracker_session_checklist_and_buttons,
        tracker_task_and_focus_bar_charts_html,
        tracker_task_and_focus_tables_html, 
        
        tracker_timeline_task_chart_html,
        tracker_timeline_focus_chart_html,

        tracker_session_schedule_task_chart_html,
        tracker_session_schedule_focus_chart_html,
        tracker_session_schedule
        ],
    id='block-page'
    )

tracker_session_html = html.Div(children=[block_page, input_hassler_html], id='tracker-session-html')

####################################################################################################
####################################################################################################

###########
# TRACKER INITIAL PAGE 
tracker_init_html = html.Div(
    id='tracker-init-html',
    children=html.H1("Customize and deploy a schedule under the Schedule tab"),
    style={
        'text-align': 'center',
        'padding': '70px 0'
        },
    hidden=False
    )
###########

###### TRACKER - PRESESSION - COMPONENTS
deployed_schedule = html.Div(
    id='deployed-schedule', 
    children=[tracker_schedule_helper()],
    style={
        'width':'90%', 
        'border': '2px solid black',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
        )

# TRACKER PRESESSION TASK CHART
tracker_pressession_task_chart = dcc.Graph(id='tracker-presession-task-chart',config={'displayModeBar': False})
tracker_pressession_task_chart_html = html.Div(
    id='tracker-presession-task-chart-html',
    children=tracker_pressession_task_chart,
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

# TRACKER PRESESSION FOCUS CHART
tracker_pressession_focus_chart = dcc.Graph(id='tracker-presession-focus-chart',config={'displayModeBar': False})
tracker_pressession_focus_chart_html = html.Div(
    id='tracker-presession-focus-chart-html',
    children=tracker_pressession_focus_chart,
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

# TRACKER PRESESSION BUTTONS 
pre_session_start_button = html.Button(
    id='presession-start-button',children='START SESSION',  n_clicks=0, style={
        'font-size':'24px',
        'margin':'20px'
        })
pre_session_edit_button = html.Button(id='tracker-presession-edit-button', children='Edit Schedule', n_clicks=0, style={
        'font-size':'24px',
        'margin':'20px'
        }
    )

pre_session_buttons = html.Div(
    children=[pre_session_start_button, pre_session_edit_button], style={
        'width':'90%', 
        'text-align':'center',
        'padding' : '10px'
        })

presession_task_table, presession_focus_table = task_and_focus_tables_4_schedule_and_template('pression-task-table', 'presession-focus-table')
# side by side tables
presession_task_and_focus_tables_html = html.Div(
    children=[
        html.Div([presession_task_table], className="six columns"),
        html.Div([presession_focus_table], className="six columns"),
        ], className="row", style={'width':'90%','margin-left':'5%'})   

tracker_presession_html = html.Div(
    id='tracker-presession-html',
    children=[
        pre_session_buttons,
        deployed_schedule,
        tracker_pressession_task_chart_html,
        presession_task_and_focus_tables_html
    ])
##################### 

tracker_page = html.Div(
    # id='tracker-page',
    children=[
        tracker_init_html,
        tracker_presession_html,
        tracker_session_html
        ]
    )

##########################################################################################################
################################################ SCHEDULE ################################################
##########################################################################################################

#############################################################################
############################# SCHEDULE - CUSTOM #############################
#############################################################################

schedule_custom_checklist = html.Div(dcc.Checklist(
    id='schedule-custom-checklist',
    options=[
        {'label': 'Schedule', 'value': 'table', 'disabled':True},
        {'label': 'Summary Tables', 'value': 'summary'},
        {'label': 'Cumulative Task Chart', 'value': 'task-chart'},
        {'label': 'Cumulative Focus Chart', 'value': 'focus-chart'},
    ],
    value=['table', 'summary'],
    labelStyle={'display': 'inline-block'}
    ),
    style={'text-align':'center', 'margin-top':'10px', 'margin-bottom':'10px'})

schedule_task_table, schedule_focus_table = task_and_focus_tables_4_schedule_and_template('schedule-task-table', 'schedule-focus-table')
# side by side tables
schedule_custom_task_and_focus_tables_html = html.Div(
    id='schedule-custom-summary-table-html',
    children=[
        html.Div([schedule_task_table], className="six columns"),
        html.Div([schedule_focus_table], className="six columns"),
        ], className="row", style={'width':'90%','margin-left':'5%'})   

initial_schedule = PM_config.initial_schedule

#### DASH EDITABLE TABLE ####
schedule_table = dash_table.DataTable(
    id='schedule-custom',
    columns=[
            {'id': 'task', 'name': 'Task', 'presentation': 'dropdown'},
            {'id': 'length', 'name': 'Length','presentation': 'input', 'type' :'numeric'},
            {'id': 'focus', 'name': 'Focus', 'presentation': 'input', 'type' :'text'},
            {'id': 'notes', 'name': 'Notes', 'presentation': 'input', 'type' :'text'},
            {'id': 'hassler', 'name': 'Hassler', 'presentation': 'dropdown'},            
            {'id': 'applause', 'name': 'Applause', 'presentation': 'dropdown'},
            {'id': 'dinger', 'name': 'Dinger', 'presentation': 'input', 'type' :'numeric'},

        ],
    dropdown={
        'task': {'options' : [{'label': task.capitalize(), 'value': task} for task in ["work", "meditation", "movement", "break"]]
            },
        'hassler': {'options' : [
            {'label': 'Yes', 'value': True},
            {'label': 'No', 'value': False},]},
        'applause': {'options' : [
            {'label': 'Yes', 'value': True},
            {'label': 'No', 'value': False},]},
        },
    data=initial_schedule,
    style_header={
        'backgroundColor': 'grey',
        'color' : 'black',
        'text-align': 'center',
        'font-family': 'HelveticaNeue',
        'font-size': '14px',        
        'fontWeight': 'bold'
    },
    style_data_conditional=[
       
        ######## bad input for schedule
        {'if': {'filter_query': '{task} is nil || {hassler} is nil || {length} <= 0'},   
         'border': '2px solid red',
         'backgroundColor': colors['error'],
         'color': 'white'
         },    
        ########      

        ## TASK COLORS: THIS IS THE EASY TO READ, LONG WAY TO CONDITIONALLY FORMAT THE CELLS BASED ON TASK
        # {'if': {'filter_query': '{task} = work'},   
        #  'backgroundColor': colors['work'],
        #  'color': 'black'},
        # {'if': {'filter_query': '{task} = break'},   
        #  'backgroundColor': colors['break'],
        #  'color': 'black'},
        # {'if': {'filter_query': '{task} = meditation'},   
        #  'backgroundColor': colors['meditation'],
        #  'color': 'black'},
        # {'if': {'filter_query': '{task} = movement'},   
        #  'backgroundColor': colors['movement'],
        #  'color': 'black'},

        ## TASK COLORS: THIS^ IS EASIER TO READ, BUT THE MODULAR WAY TO CONDITIONALLY FORMAT THE CELLS BASED ON TASK (list comprehension) is as follows:
        ]+ [{'if': {'filter_query': '{task} = %()s' % {"": task}}, 'backgroundColor': colors[task],'color': 'black'} for task in tasks],

    css=[
        {
        'selector': '.Select-menu-outer',
        'rule': '''--accent: black;'''
        },
        {
        'selector': '.Select-arrow',
        'rule': '''--accent: black;'''
        },              
        ],
        
    style_cell={ #### FIX THIS UP!
        'backgroundColor': '#CFCFCF',
        'font-family': 'HelveticaNeue',
        'font-size': '12px',        
        'fontWeight': 'bold'
    },
    style_data={
        'color': 'black',
        'whiteSpace': 'normal',
        'textAlign': 'center'
        # 'height': 'auto',
        # 'lineHeight': '15px'
    },    
    row_deletable=True,
    row_selectable='multi',
    editable=True,
    style_as_list_view=True,
    persistence=True,
    )

schedule_table_html = html.Div(
    # id='schedule-custom-table',
    children=[schedule_table],
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'})

add_block_button = html.Button(children='Add Block', id='schedule-add-block', n_clicks_timestamp=-1)
replicate_blocks_button = html.Button(children='Replicate Blocks', id='schedule-replicate-blocks', n_clicks_timestamp=-1)
delete_selected_blocks_button = html.Button(children='Delete Selected', id='schedule-delete-selected', n_clicks_timestamp=-1)

save_template_html = html.Div([
    html.Div(dcc.Input(id='save-template-name', type='text')),
    html.Div(html.Button(children='Save Template', id='schedule-save-template-button', n_clicks_timestamp=-1)),
    html.Div(id='schedule-save-template-result')],
    style={'width':'90%', 'text-align':'right'})

deploy_schedule_button = html.Button(
    children='Deploy Schedule', 
    id='schedule-deploy-button', 
    style={'background-color': colors['accent'], 'font-weight':'bold', 'font-size': '12px'},
    n_clicks=0)
confirm_deployment = dcc.ConfirmDialog(
    id='schedule-confirm-deployment',
    message='Would you like deploy the current schedule? Note that any invalid blocks (highlighted) will not be deployed',
    submit_n_clicks=0
    )

schedule_buttons_html = html.Div(
    children=[add_block_button, 
              replicate_blocks_button,
              delete_selected_blocks_button, 
              deploy_schedule_button,
            save_template_html,
            ],
    style={
        'width':'90%', 
        'text-align':'center',
        'padding-top' : '10px'
        })

##################################
#### SCHEDULE - CUSTOM - PLOT ####
##################################
def format_schedule_for_plotting(df, tasks=['work', 'meditation', 'movement', 'break']):
    # tasks = set(df['task'])

    # IF empty dataframe OR no tasks in the task column match predetermined task names 
    # THEN return 
    # if df.shape[0]==0 or sum(df['task'].isin(tasks))==0:
    if df.shape[0]==0:
        return dict(zip(tasks, [{'x':[0],'y':[0],'text':[0]}]*len(tasks)))

    # df = df[df['task'].isin(tasks)]
    df['cum_len'] = np.cumsum(df['length'])
    df['task_cum_len'] = df.groupby("task").cumsum().loc[:,'length']

    # first_x = 0
    # first_y = 0
    last_x = df.iloc[-1]['cum_len']
    # last_x = df.loc[-1,'cum_len']
    output = {}

    for task in tasks:
        x = df[df["task"]==task]['cum_len']
        y = df[df["task"]==task]['task_cum_len']
        l = df[df["task"]==task]['length']

        focus = df[df["task"]==task]['focus']
        notes = df[df["task"]==task]['notes']

        # for y:
        # repeat everything except -1th element. 
        # append a zero at the beginning
        # reset index
        if len(x)!=0 and len(y)!=0:
            new_y = list(pd.Series(0).append(y.iloc[0:-1].repeat(2).append(pd.Series(y.iloc[-1]))).reset_index(drop=True))
            
            new_focus = list(focus.repeat(2).reset_index(drop=True))
            new_notes = list(notes.repeat(2).reset_index(drop=True))
            

            # for x:
            # alternate x-l and x
            new_x = [None]*len(x)*2
            new_x[::2]=x-l
            new_x[1::2]=x
            
            # make sure all tasks start at 0
            # if new_x[0]!=first_x:
            #     new_x.insert(first_x,0)
            #     new_y.insert(first_y,0)     
            # make sure all tasks finish at the session end time
            if new_x[-1]!=last_x:
                new_x.append(last_x)
                new_y.append(new_y[-1])
                # text.append('')

            # text = ["FOCUS: {} <br>NOTES: {} <br>".format(focus, notes) for focus,notes in zip(new_focus, new_notes)]

            text = []

            # print('new x: {}'.format(len(new_x)))
            # print('new y: {}'.format(len(new_y)))
            # print('new focus: {}'.format(len(new_focus)))
            # print('new notes: {}'.format(len(new_notes)))

            for x,y, focus, notes in zip(new_x, new_y, new_focus, new_notes):
                string = 'ELAPSED: {} <br>SPENT: {}'.format(timedelta_to_string(datetime.timedelta(minutes=x)), timedelta_to_string(datetime.timedelta(minutes=y)))
                if (focus is not None) and (focus is not ''):
                    string=string+'<br>FOCUS: {}'.format(focus)
                if (notes is not None) and (notes is not ''):
                    string=string+'<br>NOTES: {}'.format(notes)
                text.append(string)
            
            if len(text)<len(new_x):
                string = 'ELAPSED: {} <br>SPENT: {}'.format(timedelta_to_string(datetime.timedelta(minutes=float(new_x[-1]))), timedelta_to_string(datetime.timedelta(minutes=float(new_y[-1]))))
                text.append(string)

            if 'start' in list(df.columns):
                start_time = df.iloc[0]['start']
                start_time=datetime.datetime.strptime(start_time.split('.')[0], '%Y-%m-%d %H:%M:%S') 
                new_x = list(map(lambda x: datetime.timedelta(minutes=x)+start_time, new_x))
                text = ['TIME: '+str(x.strftime('%H:%M:%S'))+"<br>"+label for x, label in zip(new_x, text)]
            
                
        else: 
            new_x, new_y, text = [], [], []
        
        output[task] = {'x' : new_x, 'y':new_y, 'text':text}

    return output

def plot_custom_schedule(schedule_formatted_for_plotting, tasks=['work', 'meditation', 'movement', 'break'], cum_focus=False):
    fig = go.Figure()
    if cum_focus is False:
        for task in tasks:
            fig.add_trace(
                go.Scattergl(
                    x=schedule_formatted_for_plotting[task]['x'], 
                    y=schedule_formatted_for_plotting[task]['y'], 
                    name=task,
                    # name=None,
                    # name=task,
                    line=dict(color=colors[task], width=2),
                    mode='lines',
                    text=schedule_formatted_for_plotting[task]['text'],
                    hovertemplate="%{text}" 
                    # hovertemplate="<b>{}</b><br>".format(task.upper()) + "%{text}" 
                        # "Time Elapsed: %{x} minutes <br>" +
                        # "Time Spent On Task: %{y}" +
                        # "<extra></extra>",
                    )
                    )    
    else: 
        for task in tasks:
            fig.add_trace(
                go.Scattergl(
                    x=schedule_formatted_for_plotting[task]['x'], 
                    y=schedule_formatted_for_plotting[task]['y'], 
                    name=task,
                    # name=None,
                    # name=task,
                    line=dict(width=2),
                    mode='lines',
                    text=schedule_formatted_for_plotting[task]['text'],
                    hovertemplate="%{text}" 
                    # hovertemplate="<b>{}</b><br>".format(task.upper()) + "%{text}" 
                        # "Time Elapsed: %{x} minutes <br>" +
                        # "Time Spent On Task: %{y}" +
                        # "<extra></extra>",
                    )
                    )          

    fig.update_layout(
        legend=dict(y=-0.2, x=0, traceorder='normal', font_size=16),
        legend_orientation="h")
    # fig.update_layout(hovermode='x')
    fig.update_xaxes(
        title_text="Elapsed Time (minutes)",
        showspikes=True, 
        spikecolor="orange", 
        spikesnap="cursor", 
        spikethickness=0.75, 
        spikemode="across")
    fig.update_yaxes(
        title_text="Cumulative Time Spent on Task (minutes)",
        showspikes=True, 
        spikecolor="orange", 
        spikesnap="cursor", 
        spikethickness=0.75, 
        spikemode="across",
        side="right")

    fig.update_layout(spikedistance=1000, hoverdistance=1000)
    fig.update_layout(uirevision='dataset')
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=20))

    fig.update_layout(xaxis_fixedrange=True, yaxis_fixedrange=True,) ## DISABLE ZOOMING!
    return fig

def cumulative_plot(list_of_dicts, title=None, tasks=['work', 'meditation', 'movement', 'break'], cum_focus=False):
    df=pd.DataFrame(list_of_dicts)
    formatted = format_schedule_for_plotting(df, tasks)
    fig = plot_custom_schedule(formatted, tasks, cum_focus)
    if title is not None:
        fig.update_layout(title={
            'text': title,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    return fig

schedule_custom_task_chart = dcc.Graph(id='schedule-custom-task-chart',config={'displayModeBar': False})

schedule_custom_task_chart_html = html.Div(
    id='schedule-custom-task-chart-html',
    children=schedule_custom_task_chart,
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

schedule_custom_focus_chart = dcc.Graph(id='schedule-custom-focus-chart',config={'displayModeBar': False})

schedule_custom_focus_chart_html = html.Div(
    id='schedule-custom-focus-chart-html',
    children=schedule_custom_focus_chart,
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

schedule_custom_page_html=html.Div(
    children=[
    confirm_deployment,
    schedule_buttons_html, 
    schedule_table_html,
    schedule_custom_checklist,
    
    schedule_custom_task_and_focus_tables_html,
    schedule_custom_task_chart_html,
    schedule_custom_focus_chart_html
    ])

#############################################################################
############################# TEMPLATES - COMPONENTS ##########################
###### Template components
################################d#############################################

template_task_table, template_focus_table = task_and_focus_tables_4_schedule_and_template('template-task-table', 'template-focus-table')

# side by side tables
templates_task_and_focus_tables_html = html.Div(id='template-summary-table-html',
    children=[
        html.Div([template_task_table], className="six columns"),
        html.Div([template_focus_table], className="six columns"),
        ], className="row", style={'width':'90%','margin-left':'5%'})   

templates_checklist = dcc.Checklist(
    id='templates-checklist',
    options=[
        {'label': 'Schedule', 'value': 'table'},
        {'label': 'Cumulative Task Chart', 'value': 'task-chart'},
        {'label': 'Cumulative Focus Chart', 'value': 'focus-chart'},
        {'label': 'Summary Tables', 'value': 'summary'}
    ],
    value=['table','summary'],
    labelStyle={'display': 'inline-block'})  

template_table = html.Div(id='template-schedule-html', children=[tracker_schedule_helper(data=[],id='template-schedule')])

template_task_chart = dcc.Graph(id='template-task-chart', config={'displayModeBar': False})
template_task_chart_html = html.Div(id='template-task-chart-html', children=template_task_chart)

template_focus_chart = dcc.Graph(id='template-focus-chart', config={'displayModeBar': False})
template_focus_chart_html = html.Div(id='template-focus-chart-html', children=template_focus_chart)

get_templates_button = html.Button(children='Refresh', id='refresh-templates-button', n_clicks=0)
select_template_button = html.Button(children='Edit', id='edit-template-button', n_clicks=0)
delete_template_button = html.Button(children='Delete', id='delete-template-button', n_clicks=0)
deploy_template_button = html.Button(children='Deploy', id='deploy-template-button', n_clicks=0)

template_confirm_delete = dcc.ConfirmDialog(
    id='confirm-delete',
    message='Delete template?',
    submit_n_clicks=0
    )

templates_dropdown = html.Div(dcc.Dropdown(id='templates-dropdown',options=[]),style={'width':'30%','margin':'10px'})

templates_buttons_html = html.Div(
    children=[
        get_templates_button,
        select_template_button,
        delete_template_button,
        deploy_template_button
        ],
    )

template_init_html = html.Div(
    id='template-init-html',
    children=html.H1("Choose a template from the dropdown menu."),
    style={
        'text-align': 'center',
        'padding': '70px 0'
        },
    hidden=False
    )

templates_main_html = html.Div(
    id='schedule-templates-main',
    children=[template_table,
        templates_task_and_focus_tables_html,
        template_task_chart_html,
        template_focus_chart_html,])

templates_page_html = html.Div(
    children=[
        templates_buttons_html, 
        templates_dropdown, 
        templates_checklist,
        
        template_init_html,
        templates_main_html,

        hidden_div_5 ],style={'width':'90%', 'float':'left','margin':'30px', 'display':'inline-block'}) 

#############################################################################
###################### MULTI TEMPLATES - COMPONENTS ########################$
#############################################################################

save_multiple_templates_confirm = dcc.ConfirmDialog(id='multi-temp-save-confirm')

multi_templates_buttons = html.Div(
    children=[
        save_multiple_templates_confirm,
        html.Button(children='New Row', id='multi-template-new-row-button', n_clicks=0),
        html.Button(children='Refresh', id='multi-template-refresh-button', n_clicks=0),
        html.Button(children='Save', id='multi-template-save-button', n_clicks=0),
        dcc.Input(id='multi-temp-save-input', type="text", placeholder='Primary title (optional)', persistence=False),
        html.Div(id='multi-temp-save-output-text',children='')
        ],
    )

multi_temp_checklist = html.Div(dcc.Checklist(
    id='multi-temp-checklist',
    options=[
        {'label': 'Schedule', 'value': 'schedule'},
        {'label': 'Summary Tables', 'value': 'summary-tables'},
        {'label': 'Dist. Task Plot', 'value': 'dist-task'},
        {'label': 'Cum. Task Plot', 'value': 'cum-task'},
        {'label': 'Dist. Focus Plot', 'value': 'dist-focus'},
        {'label': 'Cum. Focus Plot', 'value': 'cum-focus'},
    ],value=['summary-charts', 'summary-tables'],labelStyle={'display': 'inline-block'}),
    style={'width':'40%'}
        )

multi_temp_controls_html = html.Div(
    # id='history-individual-controls',
    children=[
        html.Div([multi_templates_buttons], className="six columns",style={'float':'left','width':'25%'}),
        html.Div([multi_temp_checklist], className="six columns",style={'float':'left'}),
        ], className="row", style={'margin-left':'5%', 'margin-bottom':'10px'})    

######################## MULTI TEMP INDIVIDUAL 
multi_temp_schedule = html.Div(
    id='multi-temp-schedule-html', 
    children=[tracker_schedule_helper(data=[], id='multi-temp-schedule', cell_borders=False)],
    style={
        'width':'90%', 
        'border': '2px solid black',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
        )

multi_temp_individual_task_table, multi_temp_individual_focus_table = task_and_focus_tables_4_schedule_and_template('multi-temp-individual-task-table', 'multi-temp-individual-focus-table')
multi_temp_individual_task_and_focus_tables_html = html.Div(id='multi-temp-individual-summary-tables-html',
    children=[
        html.Div([multi_temp_individual_task_table], className="six columns"),
        html.Div([multi_temp_individual_focus_table], className="six columns"),
        ], className="row", style={'width':'90%','margin-left':'5%'})   

multi_temp_individual_task_chart = dcc.Graph(id='multi-temp-individual-task-chart', config={'displayModeBar': False})
multi_temp_individual_task_chart_html = html.Div(id='multi-temp-individual-task-chart-html', children=multi_temp_individual_task_chart)

multi_temp_individual_focus_chart = dcc.Graph(id='multi-temp-individual-focus-chart', config={'displayModeBar': False})
multi_temp_individual_focus_chart_html = html.Div(id='multi-temp-individual-focus-chart-html', children=multi_temp_individual_focus_chart)

multi_temp_individual_checklist_html = html.Div(
    children = [dcc.Checklist(
        id='multi-temp-individual-checklist',
        options=[
            {'label': 'Schedule', 'value': 'table'},
            {'label': 'Summary Tables', 'value': 'summary'},
            {'label': 'Cumulative Task Chart', 'value': 'task-chart'},
            {'label': 'Cumulative Focus Chart', 'value': 'focus-chart'},
        ],
        value=['summary'],
        labelStyle={'display': 'inline-block'}
    )]  ,
    style={'text-align':'center'})

multi_temp_individual_template = html.Div(
    id='multi-temp-individual-temp',
    children=[
        html.H3(id='multi-temp-individual-name', children='TESTING TEMPLATE',style={'text-align':'center'}),
        multi_temp_individual_checklist_html,
        multi_temp_schedule,
        multi_temp_individual_task_and_focus_tables_html,
        multi_temp_individual_task_chart_html,
        multi_temp_individual_focus_chart_html],
    style ={'border':'4px solid black', 'margin-left':'5%', 'margin-right':'5%', 'margin-top':'10px','margin-bottom':'10px','padding-bottom':'10px'})
########################

multi_template_list = dash_table.DataTable(
    id='multi-template-list',
    columns=[{'id': 'template_id', 'name': 'Template ID','presentation':'dropdown','editable':True}]+
            [{'id': 'session_name', 'name': 'Secondary Title','presentation':'input', 'type':'text','editable':True}],
    # hidden_columns = [task+'_numeric' for task in ['work', 'meditation','movement','break']+['total']],
    data = [{},{}],
    selected_rows = [],
    style_header={
        'backgroundColor': 'grey',
        'color' : 'black',
        'text-align': 'center',
        'font-family': 'HelveticaNeue',
        'font-size': '14px',        
        'fontWeight': 'bold'
    },
    css=[
        {'selector': '.Select-menu-outer','rule': '''--accent: black;'''},
        {'selector': '.Select-arrow','rule': '''--accent: black;'''},              
        ]+[{"selector": ".show-hide", "rule": "display: none"}],
            
    style_cell={ #### FIX THIS UP!
            'backgroundColor': '#CFCFCF',
            'font-family': 'HelveticaNeue',
            'font-size': '12px',        
            'fontWeight': 'bold', 
            'border': '2px solid black',
        },
    style_data={
        'color': 'black',
        'whiteSpace': 'normal',
        'textAlign': 'center'
    },    
    # css=[{"selector": ".show-hide", "rule": "display: none"}],
    row_deletable=True,
    row_selectable='single',
    style_as_list_view=True,
    persistence=True,
    )

multi_template_table = dash_table.DataTable(
    id='multi-template-table',
    columns=[{'id': 'template_id', 'name': 'template_id'}]+
            [{'id': task, 'name': task.capitalize(), 'editable':False} for task in ['work','meditation', 'movement','break']+['total']]+
            [{'id': task+'_numeric', 'name': task.capitalize(), 'type':'numeric', 'editable':False} for task in ['work', 'meditation','movement','break']+['total']]+
            [{'id': 'a', 'name': ' ','presentation':'dropdown','editable':True}],
    hidden_columns = [task+'_numeric' for task in ['work', 'meditation','movement','break']+['total']]+['template_id'],
    data = [],
    selected_rows = [],
    style_data_conditional = [{'if': {'column_id': task},'backgroundColor': colors[task]} for task in tasks],
    dropdown={
        'a': {'options' : []}
    },
    style_header={
        'backgroundColor': 'grey',
        'color' : 'black',
        'text-align': 'center',
        'font-family': 'HelveticaNeue',
        'font-size': '14px',        
        'fontWeight': 'bold'
    },
    css=[
        {'selector': '.Select-menu-outer','rule': '''--accent: black;'''},
        {'selector': '.Select-arrow','rule': '''--accent: black;'''},              
        ]+[{"selector": ".show-hide", "rule": "display: none"}],
            
    style_cell={ #### FIX THIS UP!
            'backgroundColor': '#CFCFCF',
            'font-family': 'HelveticaNeue',
            'font-size': '12px',        
            'fontWeight': 'bold', 
            'border': '2px solid black',
        },
    style_data={
        'color': 'black',
        'whiteSpace': 'normal',
        'textAlign': 'center'
    },    
    # css=[{"selector": ".show-hide", "rule": "display: none"}],
    # row_deletable=True,

    row_selectable=False,
    # row_selectable='single',

    # editable=True,
    style_as_list_view=True,
    persistence=True,
    )

multi_template_list_html = html.Div(
    children=[multi_template_list],
    style={
        'margin-top':'10px',
        'margin-bottom':'10px'})

multi_template_table_html = html.Div(
    children=[multi_template_table],
    style={
        'margin-top':'10px',
        'margin-bottom':'10px'})

# SIDE BY SIDE TEMPLATE LIST AND TEMPLATE TABLE
muli_list_and_table = html.Div(
    # id='history-schedule-cum-charts',
    children=[
        html.Div([multi_template_list_html], className="six columns",style={'margin-left':'5%' ,'width':'45%'}),
        html.Div([multi_template_table_html], className="six columns",style={'width':'40%'}),
        ], className="row")    

multi_template_task_table, multi_template_focus_table = task_and_focus_table_4_multi_templates('multi-template-task-table', 'multi-template-focus-table')
# side by side tables
multi_template_task_and_focus_tables = html.Div(
    id='multi-temp-summary-tables',
    children=[
        html.Div([multi_template_task_table], className="six columns"),
        html.Div([multi_template_focus_table], className="six columns"),
        ], className="row", style={'width':'90%','margin-left':'5%'})   

### MULTI TEMP CHARTS
multi_temp_dist_task_chart_html = html.Div(
    id='multi-temp-dist-task-chart-html',
    children=dcc.Graph(id='multi-temp-dist-task-chart',config={'displayModeBar': False}),
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

multi_temp_cum_task_chart_html = html.Div(
    id='multi-temp-cum-task-chart-html',
    children=dcc.Graph(id='multi-temp-cum-task-chart',config={'displayModeBar': False}),
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

multi_temp_dist_focus_chart_html = html.Div(
    id='multi-temp-dist-focus-chart-html',
    children=dcc.Graph(id='multi-temp-dist-focus-chart',config={'displayModeBar': False}),
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )

multi_temp_cum_focus_chart_html = html.Div(
    id='multi-temp-cum-focus-chart-html',
    children=dcc.Graph(id='multi-temp-cum-focus-chart',config={'displayModeBar': False}),
    style={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    )    

multi_templates_page = html.Div(children=[
    muli_list_and_table, 

    multi_temp_controls_html,

    multi_template_task_and_focus_tables,
    
    multi_temp_individual_template,

    multi_temp_dist_task_chart_html,
    multi_temp_cum_task_chart_html,
    multi_temp_dist_focus_chart_html,
    multi_temp_cum_focus_chart_html
])

#############################################################################
############################# SCHEDULE - ALL TABS ###########################
#############################################################################

schedule_tabs = dcc.Tabs(
    id='schedule-tabs',
    children=[
        dcc.Tab(label='Custom', id="schedule-custom-tab", 
                children=[schedule_custom_page_html], 
                style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Templates', id="schedule-my-templates-tab", 
                children=[
                    templates_page_html,
                    template_confirm_delete], 
                style=tab_style, selected_style=tab_selected_style),

        dcc.Tab(label='Multi-Template Analysis', id="schedule-multi-template-analysis", children=[multi_templates_page], style=tab_style, selected_style=tab_selected_style),
        ],
    value='tab-1',
    mobile_breakpoint=0,
    persistence=True,
    style=tabs_styles)    


##########################################################################################################
############################################### APP LAYOUT ###############################################
##########################################################################################################

app = Flask(__name__)

dash_app = dash.Dash(name="some_name", server=app, external_stylesheets=external_stylesheets)

dash_app.layout = html.Div(
    children=[
        html.Div(id='above-tabs-info'),
        dcc.Tabs(
            id="all-tabs", 
            children=[
                dcc.Tab(label='Tracker', id="tracker-tab", value="tracker-tab", children=[tracker_page], style=tab_style, selected_style=tab_selected_style, disabled_style=tab_disabled_style),
                dcc.Tab(label='Schedule', id="schedule-tab", value="schedule-tab", children=[schedule_tabs], style=tab_style, selected_style=tab_selected_style, disabled_style=tab_disabled_style),
                dcc.Tab(label='History', id="history-tab", value="history-tab", children=[history_page], style=tab_style, selected_style=tab_selected_style, disabled_style=tab_disabled_style),
                # dcc.Tab(label='Friends', id="friends-tab", value="friends-tab", children=[], style=tab_style, selected_style=tab_selected_style, disabled_style=tab_disabled_style),
            ],
            mobile_breakpoint=0,
            persistence=True,
            style=tabs_styles,
            value="schedule-tab"
            ),
        ],
    )

############################################################################################################
########################################### HISTORY CALLBACKS ##############################################
############################################################################################################

### HISTORY - REFRESH 
@dash_app.callback(
    Output('my-date-picker-range', 'max_date_allowed'),
    [Input('history-refresh-dates', 'n_clicks')])
def history_refresh(n_clicks):
    tomorrow=datetime.datetime.now()
    return tomorrow

### HISTORY - DELETE BUTTON  
@dash_app.callback(
    [Output('history-delete-selected-confirm', 'displayed'),
    Output('history-delete-selected-confirm', 'message')],
    [Input('history-delete-selected-button', 'n_clicks')],
    [State('history-table', 'selected_rows'),
    State('history-table', 'data')])
def delete_button(n_clicks, selected_rows, history_table):
    if (len(selected_rows)==0) or (n_clicks==0):
        return False, ''
    else: 
        selected_sessions = [history_table[j] for j in selected_rows]
        session_dates = [session['session_date'] for session in selected_sessions]
        session_names = [session['session_name'] for session in selected_sessions]

        list_of_date_name_combos = ['\n{} {}'.format(date, name) if name is not None else '\n{}'.format(date) for date, name in zip(session_dates, session_names) ]
        session_string=''
        for j in range(len(list_of_date_name_combos)):
            session_string=session_string+list_of_date_name_combos[j]
            
        message = "Are you sure you want to delete the following {} selected session(s)? \n".format(len(selected_rows))
        message=message+session_string
        return True, message

# HISTORY - SAVE SCHEDULE TO TEMPLATE - BUTTON
@dash_app.callback(
    Output('save-template-output', 'children'),
    [Input('history-save-schedule-to-templates','n_clicks')],
    [State('history-table', 'data'),
    State('history-table', 'selected_rows')])
def save_schedule_to_templates(n_clicks, history_table, selected_rows):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]    

    if button_id=='history-save-schedule-to-templates':
        
        session_date = history_table[selected_rows[0]]['session_date']
        session_id = history_table[selected_rows[0]]['session_id']
        session_name = history_table[selected_rows[0]]['session_name']
        
        if (session_name is not None) and (session_name is not ''):
            template_id = str(session_id)+' '+session_date+': '+session_name
        else: 
            template_id = str(session_id)+' '+session_date
        session = list(filter(lambda x: (x['session_date']==session_date) and (x['session_id']==session_id), wt.selected_history))

        schedule = deepcopy(session[0]['schedule'])
        result = wt.save_template(template_id, schedule)
        if result is 'saved':
            output = '"'+template_id+'"'+' saved!'
        if result =='invalid name':
            return "NOT SAVED - invalid template name (cannot be blank or contain apostrophe's)"
        if result =='overwritten':
            return "TEMPLATE OVERWRITTEN: {}".format(template_id)

        else: 
            output = 'There was an issue with saving the template.'
        
        return output
    else:
        return ''

## HISTORY - INDIVIDUAL - CHECKLIST
@dash_app.callback(
    [Output('individual-bar-charts', 'style'),
    Output('individual-summary-tables', 'style'),
    Output('history-schedule-html', 'style'),
    Output('history-individual-schedule-task-chart-html', 'style'),
    Output('history-individual-timeline-task-chart-html', 'style'),
    Output('history-individual-schedule-focus-chart-html', 'style'),
    Output('history-individual-timeline-focus-chart-html', 'style'),],
    [Input('history-individual-checklist', 'value')],)
def checklist_func(selected):
    chart_style_visible = {'width':'90%', 
            'display': 'block',
            'margin-left': 'auto',
            'margin-right': 'auto',
            'margin-top':'10px',
            'margin-bottom':'10px'}  

    style_hidden={'display':'none'}
    if 'summary-charts' in selected:
        bar_style = {'width':'90%','margin-left':'5%'}
    else: 
        bar_style = style_hidden

    if 'summary-tables' in selected:
        tables_style = {'width':'90%','margin-left':'5%'}
    else: 
        tables_style = style_hidden

    if 'schedule' in selected:
        schedule_style = {
            'width':'90%', 
            'border': '2px solid black',
            'display': 'block',
            'margin-left': 'auto',
            'margin-right': 'auto',
            'margin-top':'10px',
            'margin-bottom':'10px'}
    else: 
        schedule_style = style_hidden
            
    if 'schedule-task' in selected:
        schedule_task_style = chart_style_visible
    else: 
        schedule_task_style = style_hidden 

    if 'timeline-task' in selected:
        timeline_task_style = chart_style_visible
    else: 
        timeline_task_style = style_hidden 

    if 'schedule-focus' in selected:
        schedule_focus_style = chart_style_visible
    else: 
        schedule_focus_style = style_hidden 

    if 'timeline-focus' in selected:
        timeline_focus_style = chart_style_visible
    else: 
        timeline_focus_style = style_hidden 

    return bar_style, tables_style, schedule_style, schedule_task_style, timeline_task_style, schedule_focus_style, timeline_focus_style

## HISTORY - MULTI - CHECKLIST
@dash_app.callback(
    [Output('multi-bar-charts', 'style'),
    Output('multi-summary-tables', 'style'),
    Output('history-multi-dist-task-chart-html', 'style'),
    Output('history-multi-cum-task-chart-html', 'style'),
    Output('history-multi-dist-focus-chart-html', 'style'),
    Output('history-multi-cum-focus-chart-html', 'style'),],
    [Input('history-multi-checklist', 'value')],)
def checklist_func(selected):
    style_hidden={'display':'none'}

    style_visible = {
        'width':'90%', 
        # 'border': '2px solid black',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    if 'summary-bar-charts' in selected:
        bar_style = {'width':'90%','margin-left':'5%'}
    else: 
        bar_style = style_hidden

    if 'summary-tables' in selected:
        tables_style = {'width':'90%','margin-left':'5%'}
    else: 
        tables_style = style_hidden

    if 'dist-task-chart' in selected:
        dist_task = style_visible
    else: 
        dist_task = style_hidden

    if 'cum-task-chart' in selected:
        cum_task = style_visible
    else: 
        cum_task = style_hidden        

    if 'dist-focus-chart' in selected:
        dist_focus = style_visible
    else: 
        dist_focus = style_hidden
        
    if 'cum-focus-chart' in selected:
        cum_focus = style_visible
    else: 
        cum_focus = style_hidden             

    return bar_style, tables_style, dist_task, cum_task, dist_focus, cum_focus

# HISTORY - MAIN CALLBACK
@dash_app.callback(
    [Output('history-table', 'row_selectable'),

    Output('individual-analysis-page', 'style'),
    Output('multi-analysis-page', 'style'),

    Output('history-individual-schedule-task-chart', 'figure'),
    Output('history-individual-timeline-task-chart', 'figure'),
    
    Output('history-individual-schedule-focus-chart', 'figure'),
    Output('history-individual-timeline-focus-chart', 'figure'),
    
    Output('history-individual-task-table', 'data'),
    Output('history-individual-focus-table', 'data'),

    Output('history-schedule', 'data'),
    
    Output('history-multi-dist-task-chart', 'figure'),
    Output('history-multi-cum-task-chart', 'figure'),

    Output('history-multi-task-table', 'data'),
    Output('history-multi-focus-table', 'data'),

    Output('history-individual-focus-table', 'selected_rows'),
    Output('history-multi-focus-table', 'selected_rows'),

    Output('history-multi-dist-focus-chart', 'figure'),
    Output('history-multi-cum-focus-chart', 'figure'),

    Output('multi-select-all', 'style'),
    ],

    [Input('individual-multiple-radio', 'value'),
    Input('history-table', 'selected_rows'),

    Input('history-individual-schedule-task-chart-html', 'style'),
    Input('history-individual-timeline-task-chart-html', 'style'),
    Input('history-individual-schedule-focus-chart-html', 'style'),
    Input('history-individual-timeline-focus-chart-html', 'style'),
    
    Input('history-multi-dist-task-chart-html', 'style'),
    Input('history-multi-cum-task-chart-html', 'style'),
    Input('history-multi-dist-focus-chart-html', 'style'),
    Input('history-multi-cum-focus-chart-html', 'style'),
    ],
    [State('history-table', 'data'),
    State('history-table', 'row_selectable')]
    )
def history_radio(
    individual_multiple_radio, 
    selected_rows, 
    
    ind_sched_task,
    ind_timeline_task,
    int_sched_focus,
    ind_timeline_focus,

    multi_dist_task,
    multi_cum_task,
    multi_dist_focus,
    multi_cum_focus,
    
    history_table, 
    row_selectable_state,):
    
    empty_fig = go.Figure()
    style_visible={
        # 'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}

    style_hidden={'display':'none'}

    select_all_visible_style = {'margin-left':'5%'}
    
    if (individual_multiple_radio=='individual'): 
        ####
        if (len(selected_rows)==0) or (len(history_table) < selected_rows[0]):
            return 'single', style_hidden, style_hidden,empty_fig, empty_fig, empty_fig, empty_fig, [], [], [], empty_fig, empty_fig, [], [], [], [], empty_fig, empty_fig, style_hidden
        ####

        session_date = history_table[selected_rows[0]]['session_date']
        session_id = history_table[selected_rows[0]]['session_id']
        
        ###### produce title_pretext for schedule and timeline plots
        session_name = history_table[selected_rows[0]]['session_name']
        if (session_name=='') or (session_name is None):
            title_pre_text = session_date
        else: 
            title_pre_text = session_date+' ('+session_name+')'
        ######

        session = list(filter(lambda x: (x['session_date']==session_date) and (x['session_id']==session_id), wt.selected_history))

        schedule = deepcopy(session[0]['schedule'])
        timeline = deepcopy(session[0]['timeline'])

        #### SCHEDULE TASK CHART
        if ind_sched_task!=style_hidden:
            sched_task_chart = cumulative_plot(schedule, title="{} Tasks: Schedule Plot".format(title_pre_text))
            sched_task_chart.update_layout(height=450)
        else: 
            sched_task_chart = empty_fig

        #### TIMELINE TASK CHART
        if ind_timeline_task!=style_hidden:
            timeline_task_chart = cumulative_plot(timeline, title="{} Tasks: Timeline Plot".format(title_pre_text), tasks=['work', 'meditation', 'movement', 'break']+['hassler','pause'])
            timeline_task_chart.update_layout(height=450)
        else: 
            timeline_task_chart=empty_fig

        #### Schedule FOCUS CHART
        if int_sched_focus!=style_hidden:
            sched_focus_chart = cumulative_focus_chart(schedule, title="{} Foci: Schedule Plot".format(title_pre_text)) 
            sched_focus_chart.update_layout(height=450)
        else: 
            sched_focus_chart=empty_fig

        #### TIMELINE FOCUS CHART
        if ind_timeline_focus!=style_hidden:
            timeline_focus_chart = cumulative_focus_chart(timeline, title="{} Foci: Timeline Plot".format(title_pre_text)) 
            timeline_focus_chart.update_layout(height=450)
        else: 
            timeline_focus_chart=empty_fig

        #### TASK TABLE DATA 
        sesh = [history_table[j] for j in selected_rows]
        task_table_data = []
        for task in ['work','meditation','movement','break','total*','pause','hassler','total']:   
            row = {}
            
            row['task']=task
            row['result']=sesh[0][task]
            row['actual']=sesh[0][task+'_actual']
            if task not in ['hassler', 'pause']:
                row['goal']=sesh[0][task+'_goal']
            else: 
                row['goal']=0
            task_table_data.append(row)

        #### FOCUS TABLE DATA
        focus_table_data = compute_individual_focus_data(schedule, timeline)

        #### FOCUS SELECTED ROWS 
        task_focus_cum_list = [block['task']+": "+block['focus']  for block in schedule]
        focus_selected_rows = list(range(len(list(set(task_focus_cum_list)))))

        return 'single', style_visible, style_hidden, sched_task_chart, timeline_task_chart, sched_focus_chart, timeline_focus_chart, task_table_data, focus_table_data, schedule, empty_fig, empty_fig, [], [], focus_selected_rows, [], empty_fig, empty_fig, style_hidden

    elif (individual_multiple_radio=='multiple'):
        ####
        if (len(selected_rows)==0) or (len(history_table) < selected_rows[0]):
            return 'multi', style_hidden, style_hidden,empty_fig, empty_fig, empty_fig, empty_fig, [], [], [], empty_fig, empty_fig, [], [], [], [], empty_fig, empty_fig, select_all_visible_style
        ####

        selected_rows.sort()
        selected_sessions = [history_table[j] for j in selected_rows]

        # MULTI DIST. TASK CHART
        if multi_dist_task!=style_hidden:
            actual, goals = format_multi_session_task_lines(selected_sessions)
            dist_multi_task_fig = multisession_task_overview_plot(actual, goals, "Distributional Multi-Session Task Overview")
            dist_multi_task_fig.update_layout(height=600)
        else: 
            dist_multi_task_fig = empty_fig
            actual, goals = [], []
        
        # MULTI CUM TASK CHART
        if multi_cum_task!=style_hidden:
            if multi_dist_task==style_hidden:
                actual, goals = format_multi_session_task_lines(selected_sessions)

            unalterables =['session_name', 'session_date', 'session_id']
            cum_actual = {k:[float(j) for j in list(np.cumsum(v))] if k not in unalterables else v for k,v in actual.items()}
            cum_goals = {k:[float(j) for j in list(np.cumsum(v))] if k not in unalterables else v for k,v in goals.items()}

            cum_task_fig = multisession_task_overview_plot(cum_actual, cum_goals, "Cumulative Multi-Session Task Overview")
            cum_task_fig.update_layout(height=600)
        else: 
            cum_task_fig = empty_fig

        #### MULTI TASK DATA  
        multi_task_data = []
        for task in ['work','meditation','movement','break','total*','pause','hassler','total']:           
            row = {}
            row['task']=task
            row['actual']=sum([session[task+'_actual'] for session in selected_sessions])
            if task not in ['hassler', 'pause']:
                row['goal']=sum([session[task+'_goal'] for session in selected_sessions])
                # sesh[0][task+'_goal']
            else: 
                row['goal']=0
            multi_task_data.append(row)

        multi_task_data = list(map(convert_minutes_to_string, multi_task_data))
        
        #### MULTI FOCUS DATA
        full_sessions=[]
        for session in selected_sessions:
            session_date = session['session_date']
            
            session_id = session['session_id']
            full_sessions=full_sessions+list(filter(lambda x: (x['session_date']==session_date) and (x['session_id']==session_id), wt.selected_history))

        multi_focus_data = compute_multi_focus_data(full_sessions)
        focus_selected_rows = list(range(len(multi_focus_data)))

        # MULTI DIST FOCUS CHART
        if multi_dist_focus!=style_hidden:
            focus_actual, focus_goal, task_focus_list = format_multi_session_focus_lines(full_sessions)
            dist_focus_chart = multisession_focus_overview_plot(focus_actual, focus_goal, task_focus_list, "Distributional Multi-Session Focus Overview")
            dist_focus_chart.update_layout(height=600)
        else: 
            dist_focus_chart=empty_fig

        # MULTI CUM FOCUS CHART
        if multi_cum_focus!=style_hidden:
            if multi_dist_focus==style_hidden:
                focus_actual, focus_goal, task_focus_list = format_multi_session_focus_lines(full_sessions)
        
            unalterables =['session_name', 'session_date', 'session_id']
            cum_actual = {k:[float(j) for j in list(np.cumsum(v))] if k not in unalterables else v for k,v in focus_actual.items()}
            cum_goals = {k:[float(j) for j in list(np.cumsum(v))] if k not in unalterables else v for k,v in focus_goal.items()}

            cum_focus_chart = multisession_focus_overview_plot(cum_actual, cum_goals, task_focus_list, "Cumulative Multi-Session Focus Overview")
            cum_focus_chart.update_layout(height=600)
        else:
            cum_focus_chart=empty_fig

        return 'multi', style_hidden, style_visible, empty_fig, empty_fig,empty_fig, empty_fig, [], [], [], dist_multi_task_fig, cum_task_fig, multi_task_data, multi_focus_data, [], focus_selected_rows, dist_focus_chart, cum_focus_chart, select_all_visible_style
    else: 
        return row_selectable_state, style_hidden, style_hidden, empty_fig,empty_fig, empty_fig, empty_fig, [], [],[], empty_fig, empty_fig, [], [], [], [], empty_fig, empty_fig, style_hidden

## HISTORY - DATE SELECTOR
## HISTORY - CONFIRM DELETE 
@dash_app.callback(
    [Output('history-table', 'data'),
    Output('history-table', 'selected_rows'),
    Output('history-deleted-message', 'children')],
    [Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date'),
     Input('history-delete-selected-confirm', 'submit_n_clicks'),
     Input('multi-select-all', 'value')],
    [State('history-table', 'selected_rows'),
    State('history-table', 'data'),
    State('history-table', 'row_selectable')]
     )
def update_output(start_date, end_date, confirm_delete, select_all_check_list, selected_rows, history_table, row_selectable):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]    

    if (button_id=='multi-select-all') and (row_selectable=='multi'):
        # print(select_all_check_list)
        if 'select-all' in select_all_check_list:
            return history_table, list(range(len(history_table))), ''
        else:
            return history_table, [], ''

    if button_id=='history-delete-selected-confirm':
        selected_sessions = [history_table[j] for j in selected_rows]
        session_dates = [session['session_date'] for session in selected_sessions]
        session_ids = [session['session_id'] for session in selected_sessions]

        wt.delete_from_history(session_dates, session_ids)
        
        start_date = datetime.datetime.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
        start_date_string = start_date.strftime('%Y-%m-%d')
        end_date = datetime.datetime.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
        end_date_string = end_date.strftime('%Y-%m-%d')

        wt.selected_history = get_history(start_date_string, end_date_string)
        data = [history_compute_individual_task_data(item[0], item[1], item[2], item[3], item[4]) for item in wt.selected_history]
        # print(data)
        return data, [], "{} session(s) deleted.".format(len(selected_rows))

    if (start_date is not None) and (end_date is not None):
        start_date = datetime.datetime.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
        start_date_string = start_date.strftime('%Y-%m-%d')
        end_date = datetime.datetime.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
        end_date_string = end_date.strftime('%Y-%m-%d')

        wt.selected_history = get_history(start_date_string, end_date_string)
        data = [history_compute_individual_task_data(item[0], item[1], item[2], item[3], item[4]) for item in wt.selected_history]
        # print(data)
        return data, [], ''
    
    else:
        return [], [],''

### INDIVIDUAL FOCUS BAR CHART
@dash_app.callback(
    Output('history-individual-focus-bar-chart', 'figure'),
    [Input('history-individual-focus-table', 'data'),
    Input('history-individual-focus-table', 'selected_rows'),
    Input('individual-bar-charts', 'style')],
    [State('history-table', 'selected_rows'),
    State('history-table', 'data'),])
def task_table_to_bar_chart(data, selected_rows_focus_table, bar_style, selected_rows, history_table):
    style_hidden={'display':'none'}

    if (bar_style==style_hidden) or (len(data)==0) or (len(selected_rows_focus_table)==0) or (len(data)<selected_rows_focus_table[0]) or (len(history_table)<selected_rows[0]): 
        return go.Figure()
    else:    

        session_date = history_table[selected_rows[0]]['session_date']
        session_name = history_table[selected_rows[0]]['session_name']
        if (session_name=='') or (session_name is None):
            title_pre_text = session_date
        else: 
            title_pre_text = session_date+' ('+session_name+')'

        selected_rows_focus_table.sort()
        data = [data[j] for j in selected_rows_focus_table] 
        df=pd.DataFrame(data)
        x = [task+": "+focus for task, focus in zip(df['task'], df['focus'])]

        bar_chart = plot_bar_chart_goal_total(x, list(df['actual']), list(df['goal']), "{} Foci: Goals vs. Completed".format(title_pre_text))
        bar_chart.update_layout(height=450)
        bar_chart.update_layout(showlegend=False)

        bar_chart.update_layout(xaxis = dict(
            tickmode = 'array',
            tickvals = x,
            ticktext = [y.split(" ")[0]+"<br>"+y[(y.find(" ")+1):]  if len(y.split(" "))>0 else y for y in x]
            )
        )
        return bar_chart

### INDIVIDUAL TASK BAR CHART
@dash_app.callback(
    Output('history-individual-task-bar-chart', 'figure'),
    [Input('history-individual-task-table', 'data'),
    Input('history-individual-task-table', 'selected_rows'),
    Input('individual-bar-charts', 'style')],
    [State('history-table', 'selected_rows'),
    State('history-table', 'data'),])
def focus_table_to_bar_chart(data, selected_rows_task_table, bar_style, selected_rows, history_table):
    style_hidden={'display':'none'}

    if (bar_style==style_hidden) or (len(data)==0) or (len(selected_rows_task_table)==0): 
        return go.Figure()
    else:    
        session_date = history_table[selected_rows[0]]['session_date']
        session_name = history_table[selected_rows[0]]['session_name']
        if (session_name=='') or (session_name is None):
            title_pre_text = session_date
        else: 
            title_pre_text = session_date+' ('+session_name+')'
        
        selected_rows_task_table.sort()
        data = [data[j] for j in selected_rows_task_table] 

        df=pd.DataFrame(data)
        x = list(df['task'])+['total*', 'total']

        bar_chart = plot_bar_chart_goal_total(x, list(df['actual']), list(df['goal']), "{} Tasks: Goals vs. Completed".format(title_pre_text))
        bar_chart.update_layout(height=450)
        # bar_chart.update_layout(showlegend=False)

        return bar_chart        


 ### MULTI TASK BAR CHART

@dash_app.callback(
    Output('history-multi-task-bar-chart', 'figure'),
    [Input('history-multi-task-table', 'data'),
    Input('multi-bar-charts', 'style'),
    Input('history-multi-task-table', 'selected_rows')],)
def focus_table_to_bar_chart(data, bar_style, selected_rows):
    style_hidden={'display':'none'}
    if (bar_style==style_hidden) or (len(data)==0) or (len(selected_rows)==0): 
        return go.Figure()
    else:    
        selected_rows.sort()
        data = [data[j] for j in selected_rows] 
        df=pd.DataFrame(data)
        x = list(df['task'])+['total']

        bar_chart = plot_bar_chart_goal_total(x, list(df['actual']), list(df['goal']), "Multi-Session Task Analysis: Goals vs. Completed")
        bar_chart.update_layout(height=450)
        # bar_chart.update_layout(showlegend=False)

        return bar_chart     

### MULTI FOCUS BAR CHART
@dash_app.callback(
    Output('history-multi-focus-bar-chart', 'figure'),
    [Input('history-multi-focus-table', 'data'),
    Input('multi-bar-charts', 'style'),
    Input('history-multi-focus-table', 'selected_rows')])
def task_table_to_bar_chart(data, bar_style, selected_rows):
    style_hidden={'display':'none'}
    if (bar_style==style_hidden) or (len(data)==0) or (len(selected_rows)==0): 
        return go.Figure()
    else:    
        selected_rows.sort()
        data = [data[j] for j in selected_rows] 
        df=pd.DataFrame(data)
        x = [task+": "+focus for task, focus in zip(df['task'], df['focus'])]

        bar_chart = plot_bar_chart_goal_total(x, list(df['actual']), list(df['goal']), "Multi-Session Focus Analysis: Goals vs. Completed")
        bar_chart.update_layout(height=450)
        bar_chart.update_layout(showlegend=False)

        bar_chart.update_layout(xaxis = dict(
            tickmode = 'array',
            tickvals = x,
            ticktext = [y.split(" ")[0]+"<br>"+y[(y.find(" ")+1):] for y in x]
            )
        )
        return bar_chart

#############################################################################
########################### SCHEDULE - CALLABCKS ############################
#############################################################################

# SCHEDULE - CUSTOM - CHECKLIST
@dash_app.callback(
    [Output('schedule-custom-summary-table-html', 'style'),
    Output('schedule-custom-task-chart-html', 'style'),
    Output('schedule-custom-focus-chart-html', 'style'),],
    [Input('schedule-custom-checklist', 'value')])
def templates_checklist(value):
    style_visible={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    
    style_hidden={'display':'none'}

    schedule_style, task_chart_style, summary_style, focus_chart_style = style_hidden, style_hidden, style_hidden, style_hidden
    if 'task-chart' in value:
        task_chart_style = style_visible
    if 'focus-chart' in value:
        focus_chart_style = style_visible   
    if 'summary' in value:
        summary_style = {'width':'90%','margin-left':'5%'}
    return summary_style, task_chart_style ,focus_chart_style
    
## SCHEDULE - ADD NEW BLOCK, DELETE SELECTED BLOCK, SELECT FROM TEMPLATE **** ##############
@dash_app.callback(
    [Output('schedule-custom', 'data'),
    Output('schedule-custom', 'selected_rows'),
    Output('schedule-tabs', 'value'),
    Output('save-template-name', 'value')],
    [Input('schedule-add-block', 'n_clicks'),
     Input('schedule-delete-selected', 'n_clicks'),
    Input('schedule-replicate-blocks', 'n_clicks'),
    Input('edit-template-button', 'n_clicks')
     ],
    [State('schedule-custom', 'data'),
     State('schedule-custom', 'selected_rows'),
     State('templates-dropdown', 'value'),
     State('schedule-custom', 'data'),
     State('schedule-tabs', 'value'),
     State('save-template-name', 'value')
     ])
def customize_schedule(
    n_clicks_timestamp_addblock, 
    submit_n_clicks_timestamp_delete_selected, 
    replicate_blocks_button,
    n_clicks_template_select,
    rows,
    selected_rows,
    template_id, 
    custom_schedule_table,
    selected_schedule_tab,
    save_template_name):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    ## ADD NEW BLOCK
    if button_id=='schedule-add-block':
        rows.append({'task': None, 'length': 10, 'hassler': False, 'applause':True, 'focus': '', 'notes': ''})
        return rows, selected_rows, selected_schedule_tab, save_template_name

    if button_id=='schedule-replicate-blocks':
        return rows*2, selected_rows, selected_schedule_tab, save_template_name
    ## DELETE SELECTED ROWS
    if button_id=='schedule-delete-selected':
        selected_rows.sort() # sort the list in ascending order
        rows = [rows[i] for i in range(len(rows)) if i not in selected_rows]
        return rows, [], selected_schedule_tab, save_template_name

    ## EDIT TEMPLATE
    if (button_id=='edit-template-button') and (template_id is not None):
        return wt.templates_dict[template_id], [], 'tab-1', template_id

    else:
        return rows, [], selected_schedule_tab, save_template_name


### SCHEDULE - CUSTOM - DEPLOY SCHEDULE
### TRACKER - PRESESSION - START BUTTON
### TRACKER - PRESESSION - EDIT BUTTON 
### TRACKER - SESSION - FINISH BUTTON 
@dash_app.callback(
    [Output('tracker-presession-schedule', 'data'),
    Output('tracker-presession-task-chart', 'figure'),
    Output('all-tabs', 'value'),    

    Output('tracker-init-html','hidden'),
    Output('tracker-presession-html','hidden'),
    Output('tracker-session-html','hidden'),

    Output('pression-task-table','data'),
    Output('presession-focus-table','data'),

    Output('tracker-focus-table', 'selected_rows'),
    Output('tracker-task-table', 'selected_rows'),

    Output('interval-charts', 'disabled'),

    Output('tracker-session-schedule', 'data'),
    Output('tracker-session-schedule-task-chart', 'figure'),
    Output('tracker-session-schedule-focus-chart', 'figure'),

    ],
    [Input('schedule-confirm-deployment', 'submit_n_clicks'),
    Input('deploy-template-button', 'n_clicks'),
    
    Input('tracker-presession-edit-button', 'n_clicks'), ##### EDIT BUTTON IN TRACKER TAB!

    #
    Input('presession-start-button', 'n_clicks'),
    Input('confirm-finish', 'submit_n_clicks'),
    #
    
    ], 
    [State('schedule-custom', 'data'),
    State('tracker-presession-schedule', 'data'),

    State('template-schedule', 'data'),

    State('all-tabs', 'value'),
    State('schedule-custom-task-chart','figure'),
    State('tracker-focus-table', 'selected_rows'),
    State('tracker-task-table', 'selected_rows'),
    ]
    )
def deploy_button_pressed(
    confirm_deployment_clicks, 
    deploy_template_button,
    presession_edit_button, 
    presession_start_button,
    confirm_finish_button,
    data, 
    deployed_schedule_data, 
    template_schedule_data,
    current_tab, 
    schedule_custom_plot,
    tracker_focus_table_selected_rows,
    tracker_task_table_selected_rows):

    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id=='schedule-confirm-deployment':
        data = filter(lambda block: (block['task']!=None and block['length']>0) , data)
        data = list(data)  
        ####
        
        if (wt.session_complete is True):
            wt.set_schedule(data)
        ####

        presession_task_chart = cumulative_plot(data, title="Timeline")
        presession_task_chart.update_layout(height=450) ## THIS SHOULDN'T BE NECESSARY BUT SEEMS TO BE NEEDED ON THE FIRST DEPLOYMENT

        task_table_data = task_table_from_schedule(data)
        focus_table_data = focus_table_from_schedule(data)
        
        return data, presession_task_chart,'tracker-tab', True,  False, True, task_table_data, focus_table_data, [], [], True, [], go.Figure(), go.Figure()

    if button_id=='deploy-template-button':
        if len(template_schedule_data)>0:
            template_schedule_data = filter(lambda block: (block['task']!=None and block['length']>0) , template_schedule_data)
            template_schedule_data = list(template_schedule_data)  
            ####
            if (wt.session_complete is True):
                wt.set_schedule(template_schedule_data)
            ####

            presession_task_chart = cumulative_plot(template_schedule_data, title="Timeline")
            presession_task_chart.update_layout(height=450) ## THIS SHOULDN'T BE NECESSARY BUT SEEMS TO BE NEEDED ON THE FIRST DEPLOYMENT

            task_table_data = task_table_from_schedule(template_schedule_data)
            focus_table_data = focus_table_from_schedule(template_schedule_data)
            
            return template_schedule_data, presession_task_chart,'tracker-tab', True,  False, True, task_table_data, focus_table_data, [], [], True, [], go.Figure(), go.Figure()
    
    # PRESESSION EDIT BUTTON 
    if button_id=='tracker-presession-edit-button': #### EDIT BUTTON IN TRACKER TAB!!!
        return [], go.Figure(), 'schedule-tab', False,  True, True, [], [], [], [], True, [], go.Figure(), go.Figure()

    # PRESESSION START BUTTON 
    if button_id=='presession-start-button':
        schedule=wt.schedule
        if len(schedule)==0:
            focus_selected_rows=[]
            task_selected_rows=[]
        else:
            task_focus_cum_list = [block['task']+": "+block['focus']  for block in schedule]
            unique_task_focus_pairs = list(set(task_focus_cum_list))
            focus_selected_rows = list(range(len(unique_task_focus_pairs)))

            tasks_list = [block['task'] for block in schedule]
            unique_tasks = list(set(tasks_list))
            task_selected_rows = list(range(len(unique_tasks)+3))

        if (wt.session_complete is True):
            s=threading.Thread(name="main-thread", target=wt.start, daemon=True)
            s.start()

        session_schedule_task_chart = cumulative_plot(schedule, title="Session Schedule: Tasks Overview")
        session_schedule_task_chart.update_layout(height=450)
        session_schedule_focus_chart = cumulative_focus_chart(schedule, title="Session Schedule: Foci Overview") 
        session_schedule_focus_chart.update_layout(height=450)
        return  wt.schedule, go.Figure(), current_tab,  True, True, False, [], [] ,focus_selected_rows, task_selected_rows, False, wt.schedule, session_schedule_task_chart, session_schedule_focus_chart

    if button_id=='confirm-finish':
        wt.set_input_from_dash("finish")
        session_schedule_task_chart = cumulative_plot(wt.schedule, title="Session Schedule: Tasks Overview")
        session_schedule_task_chart.update_layout(height=450)
        session_schedule_focus_chart = cumulative_focus_chart(wt.schedule, title="Session Schedule: Foci Overview") 
        session_schedule_focus_chart.update_layout(height=450)
        return [], go.Figure(), current_tab, True, True, False, [], [], tracker_focus_table_selected_rows, tracker_task_table_selected_rows, True, deployed_schedule_data, session_schedule_task_chart, session_schedule_focus_chart

    # Output('tracker-init-html','hidden'),
    # Output('tracker-presession-html','hidden'),
    # Output('tracker-session-html','hidden'),

    else:
        # fig = go.Figure()
        if wt.session_complete is False:
            charts_interval_disabled = False
            tracker_init_hidden = True
            tracker_presession_hidden = True
            tracker_session_hidden = False
            landing_tab = 'tracker-tab'

            schedule=wt.schedule
            task_focus_cum_list = [block['task']+": "+block['focus']  for block in schedule]
            unique_task_focus_pairs = list(set(task_focus_cum_list))
            focus_selected_rows = list(range(len(unique_task_focus_pairs)))

            tasks_list = [block['task'] for block in schedule]
            unique_tasks = list(set(tasks_list))
            task_selected_rows = list(range(len(unique_tasks)+3))

            session_schedule_task_chart = cumulative_plot(schedule, title="Session Schedule: Tasks Overview")
            session_schedule_task_chart.update_layout(height=450)
            session_schedule_focus_chart = cumulative_focus_chart(schedule, title="Session Schedule: Foci Overview") 
            session_schedule_focus_chart.update_layout(height=450)

        else: 
            charts_interval_disabled = True
            tracker_init_hidden = False
            tracker_presession_hidden = True
            tracker_session_hidden = True
            landing_tab = current_tab
            schedule = []
            focus_selected_rows = []
            task_selected_rows = []
            session_schedule_task_chart, session_schedule_focus_chart = go.Figure(), go.Figure()
        return [], go.Figure(), landing_tab, tracker_init_hidden, tracker_presession_hidden, tracker_session_hidden, [], [], focus_selected_rows, task_selected_rows, charts_interval_disabled, schedule, session_schedule_task_chart, session_schedule_focus_chart

# ABOVE TABS         
@dash_app.callback(
    [Output('above-tabs-info','children')],
    [Input('all-tabs', 'value'),],)
def disable_tabs(value):
    if (wt.session_complete is False) and (value in ['schedule-tab', 'history-tab', 'friends-tab']) and (wt.task is not None):
        if wt.pause is False:
            return [html.H3("{} IN SESSION!".format(wt.task.upper()))]
        else:
            return [html.H3("{} PAUSED!".format(wt.task.upper()))]
    else:
        return ['']

### SCHEDULE - CONFIRM DEPLOYMENT
@dash_app.callback(Output('schedule-confirm-deployment', 'displayed'),
              [Input('schedule-deploy-button', 'n_clicks')])
def display_confirm(n_clicks):
    if n_clicks > 0:
        return True
    return False

### SCHEDULE - PLOT CUSTOM SCHEDULE
@dash_app.callback(
    [Output('schedule-custom-task-chart', 'figure'),
    Output('schedule-custom-focus-chart', 'figure'),
    Output('schedule-task-table', 'data'),
    Output('schedule-focus-table', 'data'),],
    [Input('schedule-custom', 'data'),
    
    Input('schedule-custom-summary-table-html', 'style'),
    Input('schedule-custom-task-chart-html', 'style'),
    Input('schedule-custom-focus-chart-html', 'style'),
    
    ])
def update_custom_schedule_plot(schedule, summary_tables_style, task_style, focus_style):    
    schedule = list(filter(lambda x: (x['length'] is not ''),schedule))

    style_hidden={'display':'none'}
    empty_fig = go.Figure()
    if task_style!=style_hidden:
        task_chart = cumulative_plot(schedule, title="Schedule: Cumulative Task Plot")
        task_chart.update_layout(height=450)
    else: 
        task_chart = empty_fig

    if focus_style!=style_hidden:
        focus_chart = cumulative_focus_chart(schedule, title="Schedule: Cumulative Foci Plot") 
        focus_chart.update_layout(height=450)
    else: 
        focus_chart= empty_fig

    if  (summary_tables_style==style_hidden) or (len(schedule)==0):
        focus_table_data = []
        task_table_data = []
    else:
        focus_table_data = focus_table_from_schedule(schedule)
        task_table_data = task_table_from_schedule(schedule)

    return task_chart, focus_chart, task_table_data, focus_table_data

### SAVE TEMPLATE BUTTON
@dash_app.callback(
    Output('schedule-save-template-result', 'children'),
    [Input('schedule-save-template-button', 'n_clicks')],
    [State('save-template-name', 'value'),
    State('schedule-custom', 'data'),])
def finish_and_record(n_clicks, template_id, template):
    if template_id is not None: 
        template_id = template_id.strip()
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id=="schedule-save-template-button":
        result = wt.save_template(template_id, template)
        if result =='invalid name':
            return "NOT SAVED - invalid template name (cannot be blank or contain apostrophe's)"
        if result =='overwritten':
            return "TEMPLATE OVERWRITTEN: {}".format(template_id)
        else:
            return "SAVED: {}".format(template_id)
    else: 
        return 'Enter a name to save this template.'

################################################################################################################
########################################### MULTI TEMPLATE CALLBACKS ###########################################
################################################################################################################

# MULTI TEMPLATE REFRESH 
@dash_app.callback(
    Output('multi-template-list', 'dropdown'),
    [Input('multi-template-refresh-button', 'n_clicks')])
def finish_and_record(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id=='multi-template-refresh-button':
        wt.get_templates()
    options = [{'label': template, 'value': template} for template in wt.template_names]
    output= {'template_id': {'options' : options}}

    return output

# MULTI TEMPLATE ADD ROW 
@dash_app.callback(
    Output('multi-template-list', 'data'),
    [Input('multi-template-new-row-button', 'n_clicks')],
    [State('multi-template-list', 'data')],)
def finish_and_record(n_clicks, data):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id=='multi-template-new-row-button':
        data.append({})
    return data

# MULTI TEMP TABLE TO TASK + FOCUS SUMMARY TABLES
@dash_app.callback(
    [Output('multi-template-task-table', 'data'),
    Output('multi-template-focus-table', 'data'),],
    [Input('multi-template-table', 'data'),
    Input('multi-temp-summary-tables', 'style')])
def multi_template_table(data, summary_tables_style):
    style_hidden={'display':'none'}
    if summary_tables_style==style_hidden:
        return [], []
    non_empty_rows = list(filter(lambda x: 'template_id' in x.keys() , data))
    if len(non_empty_rows)==0:
        return [], []
    else:
        multi_temp_task_table = multi_temp_task_table_calc(non_empty_rows)

        list_of_templates = [x['template_id'] for x  in non_empty_rows]
        multi_temp_focus_table = multi_temp_focus_table_calc(list_of_templates)
        return multi_temp_task_table, multi_temp_focus_table 

# MULTI TEMPLATE: TEMPLATE LIST TO TEMPLATE TABLE
@dash_app.callback(
    [Output('multi-template-table', 'data'),

    Output('multi-temp-dist-task-chart', 'figure'),
    Output('multi-temp-cum-task-chart', 'figure'),
    Output('multi-temp-dist-focus-chart', 'figure'),
    Output('multi-temp-cum-focus-chart', 'figure'),] ,  

    [Input('multi-template-list', 'data'),
    Input('multi-temp-dist-task-chart-html', 'style'),
    Input('multi-temp-cum-task-chart-html', 'style'),
    Input('multi-temp-dist-focus-chart-html', 'style'),
    Input('multi-temp-cum-focus-chart-html', 'style'),],

    [State('multi-template-table', 'data'),])
def finish_and_record(data_list, dist_task_style, cum_task_style, dist_focus_style, cum_focus_style, data_table): 

    non_empty_rows = list(filter(lambda x: 'template_id' in x.keys() , data_list))
    if len(non_empty_rows)==0:
        return [], go.Figure(), go.Figure(), go.Figure(),  go.Figure()
    
    style_hidden = {'display':'none'}

    ################################### PRODUCE TEMPLATE TABLE FROM TEMPLATE LIST
    if len(data_list)>0:
        output=[]
        for j in range(len(data_list)):
            datum = data_list[j]
            new_row = {}
            if (datum is not None) and (len(datum)>0) and ('template_id' in datum.keys()):
                if datum['template_id'] is None: continue;
                new_row['template_id']=datum['template_id']
                schedule = wt.templates_dict[datum['template_id']]
                # print(schedule)
                for k,v in multi_template_individual_task(schedule).items():
                    new_row[k]=v
            output.append(new_row)
        if len(output)==0:
            return output, go.Figure(), go.Figure(), go.Figure(),  go.Figure()
    
        # MULTI TEMP DIST TASK CHART
        if dist_task_style!=style_hidden:
            multi_temp_dist_task_line_data = format_multi_temp_dist_task_data(output, data_list)
            dist_task = multi_template_task_overview_plot(multi_temp_dist_task_line_data, "Multi Template Dist. Task Plot")
            dist_task.update_layout(height=600)
        else: 
            dist_task=go.Figure()

        # MULTI TEMP CUM TASK CHART
        if cum_task_style!=style_hidden:
            unalterables =['template_id', 'session_name']
            multi_temp_dist_task_line_data = format_multi_temp_dist_task_data(output, data_list)
            multi_temp_cum_task_line_data = {k:[float(j) for j in list(np.cumsum(v))] if k not in unalterables else v for k,v in multi_temp_dist_task_line_data.items()}
            cum_task = multi_template_task_overview_plot(multi_temp_cum_task_line_data, "Multi Template Cum. Task Plot")
            cum_task.update_layout(height=600)
        else: 
            cum_task=go.Figure()

        # MULTI TEMP DIST FOCUS CHART
        if dist_focus_style!=style_hidden:
            multi_temp_dist_focus_line_data, task_focus_pairs = format_multi_temp_dist_focus_data(data_list)
            dist_focus = multi_temp_focus_overview_plot(multi_temp_dist_focus_line_data, task_focus_pairs, "Multi Template Dist. Focus Plot")
            dist_focus.update_layout(height=600)
        else: 
            dist_focus=go.Figure()

        # MULTI TEMP CUM FOCUS CHART 
        if cum_focus_style!=style_hidden:
            multi_temp_dist_focus_line_data, task_focus_pairs = format_multi_temp_dist_focus_data(data_list)
            unalterables =['template_id', 'session_name']
            multi_temp_cum_focus_line_data = {k:[float(j) for j in list(np.cumsum(v))] if k not in unalterables else v for k,v in multi_temp_dist_focus_line_data.items()}
            cum_focus = multi_temp_focus_overview_plot(multi_temp_cum_focus_line_data,task_focus_pairs, "Multi Template Cum. Focus Plot")
            cum_focus.update_layout(height=600)
        else: 
            cum_focus=go.Figure()
        return output, dist_task, cum_task, dist_focus, cum_focus
    else:
        return data_table, go.Figure(), go.Figure(), go.Figure(),  go.Figure()

### MULTI TEMP INDIVIDUAL TEMPLATE VIEW
@dash_app.callback(
    [Output('multi-temp-individual-name','children'),
    Output('multi-temp-schedule','data')],
    [Input('multi-template-list','selected_rows')],
    [State('multi-template-list','data')])
def selected_row(selected_rows, data_list):
    if (len(selected_rows)==0) or (len(data_list)==0) or (len(data_list)<selected_rows[0]):
        return '', []
    datum = [data_list[j] for j in selected_rows]
    datum= datum[0]
    if ('template_id' not in datum.keys()):
        return '', []

    schedule = wt.templates_dict[datum['template_id']]
    return 'template ID: '+datum['template_id'], schedule

### MULTI TEMP INDIVIDUAL TEMPLATE VIEW
@dash_app.callback(
    [Output('multi-temp-individual-task-table','data'),
    Output('multi-temp-individual-focus-table','data'),
    Output('multi-temp-individual-task-chart','figure'),
    Output('multi-temp-individual-focus-chart','figure')],
    [Input('multi-temp-schedule','data'),
    Input('multi-temp-individual-summary-tables-html', 'style'),
    Input('multi-temp-individual-task-chart-html', 'style'),
    Input('multi-temp-individual-focus-chart-html', 'style'),])
def selected_row(data, summary_tables_style, task_chart_style, focus_chart_style):
    style_hidden = {'display':'none'}

    if summary_tables_style!=style_hidden:
        task_table_data = task_table_from_schedule(data)
        focus_table_data = focus_table_from_schedule(data)
    else: 
        task_table_data=[]
        focus_table_data=[]

    if task_chart_style!=style_hidden:
        task_chart = cumulative_plot(data, title="Template Schedule")
        task_chart.update_layout(height=450)
    else:
        task_chart=go.Figure()

    if focus_chart_style!=style_hidden:
        focus_chart = cumulative_focus_chart(data, title="Template: Cumulative Foci Plot") 
        focus_chart.update_layout(height=450)
    else:
        focus_chart=go.Figure()

    return task_table_data, focus_table_data, task_chart, focus_chart

# MULTI TEMP CHEKLIST
@dash_app.callback(
    [Output('multi-temp-individual-temp', 'style'),
    Output('multi-temp-summary-tables', 'style'),
    Output('multi-temp-dist-task-chart-html', 'style'),
    Output('multi-temp-cum-task-chart-html', 'style'),
    Output('multi-temp-dist-focus-chart-html', 'style'),
    Output('multi-temp-cum-focus-chart-html', 'style'),],
    [Input('multi-temp-checklist', 'value')],)
def checklist_func(selected):
    style_hidden={'display':'none'}

    style_visible = {
        'width':'90%', 
        # 'border': '2px solid black',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        # 'margin-top':'10px',
        # 'margin-bottom':'10px'
        }
    
    if 'schedule' in selected:
        schedule = {'border':'4px solid black', 'margin-left':'5%', 'margin-right':'5%', 'margin-top':'10px','margin-bottom':'10px','padding-bottom':'10px'}
    else: 
        schedule = style_hidden

    if 'summary-tables' in selected:
        tables_style = {'width':'90%','margin-left':'5%'}
    else: 
        tables_style = style_hidden

    if 'dist-task' in selected:
        dist_task = style_visible
    else: 
        dist_task = style_hidden

    if 'cum-task' in selected:
        cum_task = style_visible
    else: 
        cum_task = style_hidden        

    if 'dist-focus' in selected:
        dist_focus = style_visible
    else: 
        dist_focus = style_hidden
        
    if 'cum-focus' in selected:
        cum_focus = style_visible
    else: 
        cum_focus = style_hidden             

    return schedule, tables_style, dist_task, cum_task, dist_focus, cum_focus

# MULTI TEMP INDIVIDUAL CHEKLIST
@dash_app.callback(
    [Output('multi-temp-schedule-html', 'style'),
    Output('multi-temp-individual-summary-tables-html', 'style'),
    Output('multi-temp-individual-task-chart-html', 'style'),
    Output('multi-temp-individual-focus-chart-html', 'style'),],
    [Input('multi-temp-individual-checklist', 'value')],)
def checklist_func(selected):
    style_hidden={'display':'none'}

    style_visible = {
        'width':'90%', 
        # 'border': '2px solid black',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    
    if 'table' in selected:
        schedule = {'border':'4px solid black', 'margin-left':'5%', 'margin-right':'5%', 'margin-top':'10px','margin-bottom':'10px','padding-bottom':'10px'}
    else: 
        schedule = style_hidden

    if 'summary' in selected:
        tables_style = {'width':'90%','margin-left':'5%'}
    else: 
        tables_style = style_hidden

    if 'task-chart' in selected:
        task_chart = style_visible
    else: 
        task_chart = style_hidden

    if 'focus-chart' in selected:
        focus_chart = style_visible
    else: 
        focus_chart = style_hidden

    return schedule, tables_style, task_chart, focus_chart

# MULTI TEMP SAVE MULTIPLE TEMPLATES BUTTON
@dash_app.callback(
    [Output('multi-temp-save-confirm', 'displayed'),
    Output('multi-temp-save-confirm', 'message')],
    [Input('multi-template-save-button', 'n_clicks')],
    [State('multi-temp-save-input','value'),
    State('multi-template-list', 'data')])
def save_templates_button(n_clicks, primary_name, template_list):
    if len(template_list)==0:
        return False, ''
    non_empty_rows = list(filter(lambda x: 'template_id' in x.keys() , template_list))
    if len(non_empty_rows)==0:
        return False, ''
    
    template_names = return_template_names(non_empty_rows, primary_name)

    output_string=''
    for template_name in template_names:
        output_string=output_string+'\n'+template_name
    
    output_string= "Are you sure you want to save the following: "+output_string
    return True, output_string
    
# MULTI TEMP SAVE MULTIPLE TEMPLATES CONFIRM
@dash_app.callback(
    [Output('multi-temp-save-output-text','children')],
    [Input('multi-temp-save-confirm', 'submit_n_clicks')],
    [State('multi-temp-save-input','value'),
    State('multi-template-list', 'data')])
def save_templates_confirm(submit_n_clicks, primary_name, template_list):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]    
        
    if button_id=='multi-temp-save-confirm':
        non_empty_rows = list(filter(lambda x: 'template_id' in x.keys() , template_list))
        template_names = return_template_names(non_empty_rows, primary_name)
        template_ids = [x['template_id'] for x in non_empty_rows]

        saving_results_good = True
        results_vector=[]
        for template_id, template_name in zip(template_ids, template_names):

            result = wt.save_template(template_name, wt.templates_dict[template_id], vocalize=False)
            results_vector.append(result)
            if result not in ['saved', 'overwritten']:
                saving_results_good = False
        
        total_saved = sum([True if v=='saved' else False for v in results_vector])
        total_overwritten = sum([True if v=='overwritten' else False for v in results_vector])
        if saving_results_good is True:
            if total_saved>0:
                wt.system_wrapper('say "{} templates saved!"'.format(total_saved))
                string_output_1 = '{} templates saved!'.format(total_saved)
            else: string_output_1=''
            if total_overwritten>0:
                wt.system_wrapper('say " {} templates overwritten!"'.format(total_overwritten))  
                string_output_2 = ' {} templates overwritten!'.format(total_overwritten)
            else: string_output_2=''
                      
            return [(string_output_1+string_output_2).strip()]
        else:
            wt.system_wrapper('say "there was an issue with saving."'.format(len(template_ids)))
            return ["issue with saving some templates :("]
    else:
        return ['']

######################################################################################################################################################
############################################################### TRACKER CALLBACKS ####################################################################
######################################################################################################################################################

# TRACKER - SESSION - CHECKLIST
@dash_app.callback(
    [Output('tracker-session-bar-charts', 'style'),
    Output('tracker-session-summary-tables', 'style'),

    Output('tracker-timeline-task-chart-html', 'style'),
    Output('tracker-timeline-focus-chart-html', 'style'),
    
    Output('tracker-session-schedule-task-chart-html', 'style'),
    Output('tracker-session-schedule-focus-chart-html', 'style'),
    Output('tracker-session-schedule-html', 'style'),],

    [Input('tracker-session-checklist', 'value')])
def templates_checklist(value):
    style_visible={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    
    style_hidden={'display':'none'}

    bar_charts_style, summary_tables_style, timeline_task_chart_style, timeline_focus_chart_style = style_hidden, style_hidden, style_hidden, style_hidden
    schedule_task_chart_style, schedule_focus_chart_style, schedule_style = style_hidden, style_hidden, style_hidden
    if 'summary-bars' in value:
        bar_charts_style = {'width':'90%','margin-left':'5%'}
    if 'summary-tables' in value:
        summary_tables_style = {'width':'90%','margin-left':'5%'}   
    if 'timeline-task' in value:
        timeline_task_chart_style = style_visible
    if 'timeline-focus' in value:
        timeline_focus_chart_style = style_visible

    if 'schedule-task' in value:
        schedule_task_chart_style = style_visible
    if 'schedule-focus' in value:
        schedule_focus_chart_style = style_visible
    if 'tracker-schedule' in value:
        schedule_style = style_visible

    return bar_charts_style, summary_tables_style ,timeline_task_chart_style, timeline_focus_chart_style, schedule_task_chart_style, schedule_focus_chart_style, schedule_style
    
### PLAY / PAUSE BUTTON
@dash_app.callback(
    Output('hidden-div-2', 'children'),
    [Input('tracker-start-button', 'n_clicks')])
def on_button_click(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id=='tracker-start-button':
        if wt.pause==False:
            wt.set_input_from_dash("pause")
        elif wt.pause==True:
            wt.set_input_from_dash("unpause")        
    return ''

#### RECORD BUTTON (CONFIRMATION)
@dash_app.callback(
    Output('confirm-record', 'displayed'),
    [Input('tracker-record', 'n_clicks')])
def record(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id=="tracker-record":
        return True
    return False

#### RECORD BUTTON DIALOG
@dash_app.callback(
    Output('hidden-div-4', 'children'),
    [Input('confirm-record', 'submit_n_clicks'),],
    [State('input-save-session','value')])
def record_session(submit_n_clicks, session_name):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id=='confirm-record':
        wt.record_session(session_name)
    return ''

#### FINISH BUTTON (CONFIRMATION)
@dash_app.callback(
    Output('confirm-finish', 'displayed'),
    [Input('tracker-finish', 'n_clicks')])
def finish_and_record(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id=="tracker-finish":
        return True

### NEXT BUTTON
@dash_app.callback(
    Output('hidden-div', 'children'),
    [Input('tracker-next', 'n_clicks')])
def next_button_callback(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id=="tracker-next":
        wt.set_input_from_dash("next")
    return ['']
        
### INFO INTERVAL
@dash_app.callback(
    [Output('current-info-html', 'children'),

    Output('tracker-task-table', 'data'),
    Output('tracker-focus-table', 'data'),
    
    Output('tracker-start-button', 'children'),
    Output('interval-hassler', 'disabled'),
    Output('input-hassler-html', 'hidden'),
    Output('block-page', 'hidden'),
    Output('tracker-session-schedule', 'style_data_conditional')],
    [Input('interval-info', 'n_intervals')],
    [State('tracker-session-zen-mode', 'value')])
def interval_info(n_intervals, zen_value):
    total_string, goal_string = wt.return_totals_and_goals_string()
    # session_info_table_data = [total_string, goal_string]
    if len(zen_value)>0:
        current_info_html = current_info_html_output(wt.task, wt.current_focus, wt.current_notes, wt.length, wt.block_time_elapsed, wt.pause, wt.pause_elapsed_timedelta, wt.session_complete, zen_mode=True)    
    else: 
        current_info_html = current_info_html_output(wt.task, wt.current_focus, wt.current_notes, wt.length, wt.block_time_elapsed, wt.pause, wt.pause_elapsed_timedelta, wt.session_complete)

    if wt.pause==True:
            pause_button = "Unpause"
    elif wt.pause==False:
            pause_button = "Pause"

    if wt.hassler_status is True:
        interval_hassler = False
        input_hassler_html = False
        block_page = True
    else: 
        interval_hassler = True
        input_hassler_html = True
        block_page = False

    focus_table_data = compute_individual_focus_data(wt.schedule, wt.timeline_completed())
    
    total_numeric, goal_numeric = wt.return_totals_and_goals_numeric()

    output = []
    if len(total_numeric)>0:        
        for task in ['work', 'meditation', 'movement','break', 'total*', 'pause','hassler', 'total']:
            if task not in goal_numeric.keys():
                continue;
            row = {}
            row['task']=task
            row['actual']=total_numeric[task].total_seconds()/60
            if task not in ['hassler', 'pause']:
                row['goal']=goal_numeric[task].total_seconds()/60
                row['result']= total_string[task]+' / '+ goal_string[task]
            else: 
                row['goal']=0
                row['result']= total_string[task]
            output.append(row)
    
    
    session_schedule_style_output = [{'if': {'filter_query': '{task} = %()s' % {"": task}}, 'backgroundColor': colors[task],'color': 'black'} for task in tasks]
    session_schedule_style_output.append({'if': {'row_index': wt.current_block_index},'font-size': '30px'})


    # return current_info_html, session_info_table_data, output, focus_table_data, pause_button, interval_hassler, input_hassler_html, block_page
    return current_info_html, output, focus_table_data, pause_button, interval_hassler, input_hassler_html, block_page, session_schedule_style_output

### DISABLE INFO INTERVAL IF CHARTS INTERVAL IS DISABLED
@dash_app.callback(
    Output('interval-info','disabled'),
    [Input('interval-charts', 'disabled')])
def interval_charts_info(charts_interval_disabled):
    return charts_interval_disabled

### TRACKER - ZEN MODE CHECKLIST
@dash_app.callback(
    Output('tracker-session-checklist', 'value'),
    [Input('tracker-session-zen-mode', 'value')],
    [State('tracker-session-checklist', 'value'),])
def zenmode_checklist(zen_mode, tracker_checklist):
    if len(zen_mode)>0:
        return []
    else: 
        return tracker_checklist

### CHARTS INTERVAL
@dash_app.callback(
    [Output('tracker-timeline-task-chart', 'figure'),
    
    Output('tracker-timeline-focus-chart', 'figure'),

    Output('tracker-task-bar-chart', 'figure'),
    Output('tracker-focus-bar-chart', 'figure'),],
    [Input('interval-charts', 'n_intervals'),
    
    Input('tracker-session-bar-charts', 'style'),
    Input('tracker-timeline-task-chart-html', 'style'),
    Input('tracker-timeline-focus-chart-html', 'style'),

    ],
    [State('tracker-task-table', 'data'),
    State('tracker-task-table', 'selected_rows'),
    State('tracker-focus-table', 'data'),
    State('tracker-focus-table', 'selected_rows'),]
    )
def interval_charts(
    n_intervals, 

    bar_style,
    task_style,
    focus_style,

    task_table,
    task_selected_rows, 
    focus_table, 
    focus_selected_rows):
    
    style_hidden={'display':'none'}
    empty_fig=go.Figure()

    if (task_style!=style_hidden) or (focus_style!=style_hidden):
        timeline = wt.timeline_completed()
    
    if (task_style!=style_hidden):
        timeline_task_chart = cumulative_plot(timeline, title="Timeline: Cumulative Task Plot", tasks=tasks)
        timeline_task_chart.update_layout(height=450) 
    else: 
        timeline_task_chart = empty_fig

    if (focus_style!=style_hidden):
        timeline_focus_chart = cumulative_focus_chart(timeline, title="Timeline: Cumulative Foci Plot") 
        timeline_focus_chart.update_layout(height=450) 
    else: 
        timeline_focus_chart = empty_fig
    
    if (bar_style==style_hidden) or (len(task_selected_rows)==0) or (sum([j>=len(task_table) for j in task_selected_rows])>0):
        task_bar_chart = empty_fig
    else: 
        df=pd.DataFrame([task_table[j] for j in task_selected_rows])
        # x = list(df['task'])+['total']
        task_bar_chart = plot_bar_chart_goal_total(list(df['task']), list(df['actual']), list(df['goal']), "Tasks: Goals vs. Progress")
        task_bar_chart.update_layout(height=450)
        # bar_chart.update_layout(showlegend=False)

    if (bar_style==style_hidden) or (len(focus_selected_rows)==0) or (sum([j>=len(focus_table) for j in focus_selected_rows])>0):
        focus_bar_chart = empty_fig
    else: 
        df=pd.DataFrame([focus_table[j] for j in focus_selected_rows])
        x = [task+": "+focus for task, focus in zip(df['task'], df['focus'])]
        focus_bar_chart = plot_bar_chart_goal_total(x, list(df['actual']), list(df['goal']), "Foci: Goals vs. Progress")
        focus_bar_chart.update_layout(height=450)
        focus_bar_chart.update_layout(showlegend=False)
        focus_bar_chart.update_layout(xaxis = dict(
                tickmode = 'array',
                tickvals = x,
                ticktext = [y.split(" ")[0]+"<br>"+y[(y.find(" ")+1):] for y in x]
                )
            )

    return timeline_task_chart, timeline_focus_chart, task_bar_chart, focus_bar_chart

### HASSLER INPUT INTERVAL
@dash_app.callback(
    Output('input-hassler', 'value'),
    [Input('interval-hassler', 'n_intervals')],
    [State('input-hassler', 'value'),]
    )
def hassler_input_interval(n_intervals, value):
    if wt.hassler_status == True:
        return value
    else: 
        return ''

### HASSLER INPUT
@dash_app.callback(
    Output('hidden-div-3', 'children'),
    [Input('input-hassler', 'value')]
    )
def hassler_input(value):
    wt.set_input_from_dash(value)
    return ['']

######################################################################################################################################################
############################################################## TEMPLATES CALLBACKS ###################################################################
######################################################################################################################################################

# TEMPLATES CHECKLIST
@dash_app.callback(
    [Output('template-schedule-html', 'style'),
    Output('template-task-chart-html', 'style'),
    Output('template-summary-table-html', 'style'),
    Output('template-focus-chart-html', 'style'),],
    [Input('templates-checklist', 'value')])
def templates_checklist(value):
    style_visible={
        'width':'90%', 
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top':'10px',
        'margin-bottom':'10px'}
    
    style_hidden={'display':'none'}

    schedule_style, task_chart_style, summary_style, focus_chart_style = style_hidden, style_hidden, style_hidden, style_hidden
    if 'table' in value:
        schedule_style = style_visible
    if 'task-chart' in value:
        task_chart_style = style_visible
    if 'focus-chart' in value:
        focus_chart_style = style_visible        
    if 'summary' in value:
        summary_style = {'width':'90%','margin-left':'5%'}
    return schedule_style, task_chart_style, summary_style, focus_chart_style
    
# REFRESH TEMPLATES
@dash_app.callback(
    Output('templates-dropdown', 'options'),
    [Input('refresh-templates-button', 'n_clicks')])
def finish_and_record(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id=='refresh-templates-button':
        wt.get_templates()
    options = [{'label': template, 'value': template} for template in wt.template_names]
    return options

# #### DELETE TEMPLATE DIALOG
@dash_app.callback(
    Output('hidden-div-5', 'children'),
    [Input('confirm-delete', 'submit_n_clicks'),],
    [State('templates-dropdown', 'value'),],)
def delete_template_dialog(submit_n_clicks, value):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if (button_id=='confirm-delete') and (value is not None):
        wt.delete_template(value)
        wt.get_templates(audio=False)
        return ''
    else:
        return ''

### DELETE TEMPLATE (CONFIRMATION)
@dash_app.callback(
    Output('confirm-delete', 'displayed'),
    [Input('delete-template-button', 'n_clicks')])
def finish_and_record(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id=='delete-template-button':
        return True
    return False

## TEMPLATE - DROPDOWN - CALLBACK
@dash_app.callback(
    [Output('template-schedule', 'data'),
    Output('template-task-chart', 'figure'),
    Output('template-focus-chart', 'figure'),
    Output('template-task-table', 'data'),
    Output('template-focus-table', 'data'),
    Output('template-init-html', 'hidden'),
    Output('schedule-templates-main', 'hidden'),],
    [Input('templates-dropdown', 'value'),
    Input('template-task-chart-html', 'style'),
    Input('template-summary-table-html', 'style'),
    Input('template-focus-chart-html', 'style'),]
    )
def template_update(
    value, 

    task_style,
    summary_style,
    focus_style,
    
    tasks=['work', 'meditation', 'movement', 'break']):

    style_hidden={'display':'none'}
    
    empty_fig = go.Figure()

    if value is None:
        schedule = []
        return [], go.Figure(), go.Figure(), [], [], False, True
    
    schedule = wt.templates_dict[value]

    if task_style != style_hidden:
        task_chart = cumulative_plot(schedule, title="Template Schedule")
        task_chart.update_layout(height=450)
    else: 
        task_chart=empty_fig

    if focus_style!=style_hidden:
        focus_chart = cumulative_focus_chart(schedule, title="Template: Cumulative Foci Plot") 
        focus_chart.update_layout(height=450)
    else:
        focus_chart=empty_fig

    if (summary_style==style_hidden) or len(schedule)==0:
        focus_table_data = []
        task_table_data = []
    else:
        focus_table_data = focus_table_from_schedule(schedule)
        task_table_data = task_table_from_schedule(schedule)
    

    return schedule, task_chart, focus_chart, task_table_data, focus_table_data, True, False

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

if __name__ == '__main__':

    wt = work_timer(applause_sound_location=PM_config.applause_sound_location, ding_sound_location=PM_config.ding_sound_location)
    wt.postgres_startup()  
    t=threading.Thread(name="input", target=wt.get_input, daemon=True)
    t.start()
    dash_app.run_server(host='127.0.0.1', port=PM_config.dash_app_port, debug=True)

