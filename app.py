import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import dash_table as dt
import sys
from datetime import datetime
from Acorn import Acorn

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

avail_df = pd.read_csv("avail_df.csv", index_col=0)
wait_df = pd.read_csv('wait_df.csv', index_col=0)
loan_df = pd.read_csv('borrow_df.csv', index_col=0)

app.layout = html.Div(children=[
    html.Div([
        html.Div([
            html.H1(['Little Acorn'], style = {"padding":"0px", "margin":"0px"}),
            html.H6(['Scan your Goodreads to-read list for available audiobooks at the Arlington library!'], style = {"padding":"0px", "margin":"0px", "padding-bottom":"10px"}),
            html.Div([
                html.Div([
                    html.Div(["Goodreads Username:"], style = {"display":"table-cell"}),
                    html.Div([dcc.Input(id='input-username-on-submit', type='text')], style = {"display":"table-cell", "padding": "5px"}),
                    html.Div(["Arlington Public Library Card Number:"], style = {"display":"table-cell"}),
                    html.Div([dcc.Input(id='input-library-on-submit', type='text')], style = {"display":"table-cell", "padding": "5px"}),
                ], style = {"display":"table", "padding": "2px"})
            ], style = {"display":"table-cell"}),
            html.Button('Submit', id='submit-val', n_clicks=0),
            ], style = {"display":"table-cell", "vertical-align":"middle", "float":"left"}),
        html.Img(src=app.get_asset_url('little_acorn_logo.jpg'), style={"height":"200px", "width":"200px", 'float':'right', 'display':'table-cell'})
        ], style = {"display":"table", "width":"100%"}),
    html.Div([
        html.Button('Export', id='export-data', n_clicks=0)
        ], style = {"float":"right"}),
    html.Div(id="export-update"),
    html.H6(['Available Audiobooks'], style = {"padding":"2px", "margin":"0px", "padding-top":"10px"}),
        html.Div([dt.DataTable(
        id = 'avail-table',
        row_selectable='multi',
        selected_rows = [],
        columns=[{"name":i, "id": i} for i in ['Title', 'Author', 'Status']],
        style_cell={'textAlign': 'left'},
        style_cell_conditional=[
            {'if': {'column_id': 'Title'},
                'width': '45%'},
            {'if': {'column_id': 'Author'},
                'width': '40%'},
            {'if': {'column_id': 'Status'},
                'width': '15%'},
        ]
        )], style = {"padding-bottom":"5px"}),
        html.Div([
        html.Button(['Check-Out'], id='check-out-val', n_clicks=0, style = {"display":"table-cell"}),
        html.Div(id ="checkout-update", style = {"display":"table-cell"}),
        ], style = {'display':"table"}),
        html.H6(['Wait List Audiobooks'], style = {"padding":"2px", "margin":"0px", "padding-top":"10px"}),
        html.Div([dt.DataTable(
            id = 'wait-table',
            row_selectable='multi',
            selected_rows = [],
            columns=[{"name":i, "id": i} for i in ['Title', 'Author', 'Wait Time', 'Status']],
            style_cell={'textAlign': 'left'},
            style_cell_conditional=[
                {'if': {'column_id': 'Title'},
                    'width': '45%'},
                {'if': {'column_id': 'Author'},
                    'width': '25%'},
                {'if': {'column_id': 'Status'},
                    'width': '15%'},
                {'if': {'column_id': 'Wait time'},
                    'width':'15%'}
            ]
            )], style = {"padding-bottom":"5px"}),
        html.Div([
        html.Button(['Wait List'], id='wait-list-val', n_clicks=0, style = {"display":"table-cell"}),
        html.Div(id ="waitlist-update", style = {"display":"table-cell"}),
        ], style = {'display':"table"}),
        html.H6(['My Audiobooks on Loan'], style = {"padding":"2px", "margin":"0px", "padding-top":"10px"}),
        html.Div([dt.DataTable(
            id = 'loan-table',
            row_selectable='multi',
            columns=[{"name":i, "id": i} for i in ['Title', 'Author', 'Status']],
            style_cell={'textAlign': 'left'},
            style_cell_conditional=[
                {'if': {'column_id': 'Title'},
                    'width': '45%'},
                {'if': {'column_id': 'Author'},
                    'width': '40%'},
                {'if': {'column_id': 'Status'},
                    'width': '15%'},
            ]
            )], style = {"padding-bottom":"5px"}),
        html.Div([
            html.Button(['Return'], id='return-val', n_clicks=0, style = {"display":"table-cell"}),
            html.Div(id ="return-update", style = {"display":"table-cell"}),
            ], style = {'display':"table"}),
        html.H6(['My Waitlisted Audiobooks'], style = {"padding":"2px", "margin":"0px", "padding-top":"10px"}),
        html.Div([dt.DataTable(
            id = 'my-wait-table',
            row_selectable='multi',
            columns=[{"name":i, "id": i} for i in ['Title', 'Author', 'Position', 'Wait Time Left']],
            style_cell={'textAlign': 'left'},
            style_cell_conditional=[
                {'if': {'column_id': 'Title'},
                    'width': '45%'},
                {'if': {'column_id': 'Author'},
                    'width': '25%'},
                {'if': {'column_id': 'Position'},
                    'width': '15%'},
                {'if': {'column_id': 'Wait Time Left'},
                    'width':'15%'}
            ]
            )], style = {"padding-bottom":"5px"}),
        html.Div([
            html.Button(['Release'], id='release-val', n_clicks=0, style = {"display":"table-cell"}),
            html.Div(id ="release-update", style = {"display":"table-cell"}),
            ], style = {'display':"table"}),
    ])

@app.callback(
    dash.dependencies.Output('avail-table', 'data'),
    dash.dependencies.Output('wait-table', 'data'),
    dash.dependencies.Output('loan-table', 'data'),
    dash.dependencies.Output('my-wait-table', 'data'),
    [dash.dependencies.Input('submit-val', 'n_clicks')],
    [dash.dependencies.State('input-username-on-submit', 'value'),
    dash.dependencies.State('input-library-on-submit', 'value')])
def update_output(n_clicks, gr_username, library_card):
    if n_clicks != 0:
        if gr_username == None:
            return "Please Enter Your Username :)"
        acorn_test = Acorn(library_card, gr_username)
        if 'goodreads.com' in gr_username:
            acorn_test.getListBooks()
        else:
            acorn_test.get_to_read()
        avail_df, wait_df, loan_df, hold_df = acorn_test.find_audiobook()
        return avail_df.to_dict('rows'), wait_df.to_dict('rows'), loan_df.to_dict('rows'), hold_df.to_dict('rows')
    else:
        return None, None, None, None

@app.callback(
    dash.dependencies.Output('checkout-update', 'children'),
    [dash.dependencies.Input('check-out-val', 'n_clicks')],
    [dash.dependencies.State('avail-table', 'data'),
    dash.dependencies.State('avail-table', 'selected_rows'),
    dash.dependencies.State('input-library-on-submit', 'value'),
    dash.dependencies.State('loan-table', 'data')])
def checkoutBooks(nclicks, data, selected_rows, library_card, onLoan):
    if nclicks != 0:
        if len(onLoan) + len(selected_rows) > 10:
            return "Nah bro you can't checkout that many books. You have " + str(len(onLoan)) + " books checked out already. Max you can do is 10 at a time."
        selected_rows=[data[i] for i in selected_rows]
        titles = []
        for book in selected_rows:
            titles.append(book['Title'])
        acorn = Acorn(library_card)
        acorn.checkout_books(titles)
        return "Successfully Checked Out " + ", ".join(str(x) for x in titles) + ". Enjoy!"
    else:
        return None

@app.callback(
    dash.dependencies.Output('waitlist-update', 'children'),
    [dash.dependencies.Input('wait-list-val', 'n_clicks')],
    [dash.dependencies.State('wait-table', 'data'),
    dash.dependencies.State('wait-table', 'selected_rows'),
    dash.dependencies.State('input-library-on-submit', 'value'),
    dash.dependencies.State('my-wait-table', 'data')])
def waitListBooks(nclicks, data, selected_rows, library_card, onHold):
    if nclicks != 0:
        if len(onHold) + len(selected_rows) > 10:
            return "Nah bro you can't waitlist that many books. You have " + str(len(onHold)) + " books on hold already. Max you can do is 10 at a time."
        selected_rows=[data[i] for i in selected_rows]
        titles = []
        for book in selected_rows:
            titles.append(book['Title'])
        acorn = Acorn(library_card)
        acorn.waitList_books(titles)
        return "Successfully Wait Listed " + ", ".join(str(x) for x in titles) + ". Enjoy!"
    else:
        return None

@app.callback(
    dash.dependencies.Output('return-update', 'children'),
    [dash.dependencies.Input('return-val', 'n_clicks')],
    [dash.dependencies.State('avail-table', 'data'),
    dash.dependencies.State('avail-table', 'selected_rows'),
    dash.dependencies.State('input-library-on-submit', 'value')])
def returnBooks(nclicks, data, selected_rows, library_card):
    if nclicks != 0:
        selected_rows=[data[i] for i in selected_rows]
        titles = []
        for book in selected_rows:
            titles.append(book['Title'])
        acorn = Acorn(library_card)
        acorn.returnBooksOnLoan(titles)
        return "Successfully Checked Out " + ", ".join(str(x) for x in titles) + ". Enjoy!"
    else:
        return None

@app.callback(
    dash.dependencies.Output('release-update', 'children'),
    [dash.dependencies.Input('release-val', 'n_clicks')],
    [dash.dependencies.State('my-wait-table', 'data'),
    dash.dependencies.State('my-wait-table', 'selected_rows'),
    dash.dependencies.State('input-library-on-submit', 'value')])
def releaseBooks(nclicks, data, selected_rows, library_card):
    if nclicks != 0:
        selected_rows=[data[i] for i in selected_rows]
        titles = []
        for book in selected_rows:
            titles.append(book['Title'])
        acorn = Acorn(library_card)
        acorn.releaseBooksOnHold(titles)
        return "Successfully Checked Out " + ", ".join(str(x) for x in titles) + ". Enjoy!"
    else:
        return None

@app.callback(
    dash.dependencies.Output('export-update', 'children'),
    [dash.dependencies.Input('export-data', 'n_clicks')],
    [dash.dependencies.State('input-username-on-submit', 'value'),
    dash.dependencies.State('avail-table', 'data'),
    dash.dependencies.State('wait-table', 'data')])
def exportBooks(nclicks, username, avail, wait):
    if nclicks != 0:
        now = datetime.now()
        dt_string = now.strftime("%m_%d_%y")
        avail_df = pd.DataFrame.from_records(avail)
        wait_df = pd.DataFrame.from_records(wait)
        avail_df['Wait Time'] = ""
        final_df = pd.concat([avail_df, wait_df], sort=False)
        final_df.to_csv("exports/" + username + "_" + dt_string + "_export.csv")
        return "Successfully Exported as " + username + "_" + dt_string + "_export.csv" + ". Enjoy!"
    else:
        return None

if __name__ == '__main__':
    app.run_server(debug=True)
