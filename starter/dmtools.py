from io import StringIO
import pandas as pd
import json
from urllib.request import Request, urlopen

import ssl
import urllib
from urllib.parse import urlencode
from urllib.parse import quote
context = ssl._create_unverified_context()

from itertools import cycle
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import matplotlib.pyplot as plt
import numpy as np
import ast

# for legend
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

# for fills
from matplotlib.patches import Polygon

# for placing plot in the middle of the canvas
import matplotlib.gridspec as gridspec

class DMToolsClient():
    def __init__(self, dmtools_userid_in, dmtools_apikey_in):
        self.context = ssl._create_unverified_context()
        self.dmtools_userid = dmtools_userid_in
        self.dmtools_apikey = dmtools_apikey_in
        self.api_server = "https://dmtools.brown.edu/"
        self.data_api = "dmtool/fastapi_data/open/data/"
        self.api_version = '0.0'
        self.api_server_url = self.api_server + self.data_api +  self.api_version + "/" 
        self.current_df = pd.DataFrame()
        self.create_request_header()
        self.BARN_CM2 = 1e-24
        self.PlotTrace = PlotlyTrace()
        self.scale_factor_dict = {"b":self.BARN_CM2,
                                  "mb": 1e-3*self.BARN_CM2,
                                  "ub":1e-6*self.BARN_CM2,
                                  "nb":1e-9*self.BARN_CM2,
                                  "pb":1e-12*self.BARN_CM2,
                                  "fb":1e-15*self.BARN_CM2,
                                  "ab":1e-18*self.BARN_CM2,
                                  "zb":1e-21*self.BARN_CM2,
                                  "yb":1e-24*self.BARN_CM2,
                                  "cm2":1,
                                  "cm^2":1}
    def make_api_server_internal(self):
        self.api_server = "http://container_fastapi_data_1:8014/"
        self.data_api = "dmtool/fastapi_data/internal/data/"
        #self.api_version = '0.0'
        self.api_server_url = self.api_server + self.data_api + self.api_version + "/" 
    
    # Define scale factors
    def get_scale_factor(self, unit):
        return self.scale_factor_dict[unit]
    
    def create_request_header(self):
        self.request_header = {'dmtool-userid': self.dmtools_userid ,\
                               'dmtool-apikey': self.dmtools_apikey, \
                                'Content-Type': 'application/x-www-form-urlencoded'}
    
    def create(self,subject='data',data={},url='',output='json'):
        """
        Create function.
        
        :param subject: This parameter defaults to data and can be data, data_display, plot, plot_ownership, data_ownership.
        :param data: This should be a json
        :param output: the default output is json and can be json, dataframe, array
        :param url: This is an internal input and is used when a redirect happens
        :return: A json outout of the response from the server.
        """
        
        create_url = self.api_server_url + subject + "/create/" 
        if url == '':
            encoded_data = json.dumps(data).encode('utf-8')
            create_request = urllib.request.Request(create_url, data=encoded_data, method='POST')
            create_request.add_header('dmtool-userid', str(self.dmtools_userid))
            create_request.add_header('dmtool-apikey', self.dmtools_apikey)
            create_request.add_header('Content-Type', 'application/json')
        else:
            encoded_data = json.dumps(data).encode('utf-8')
            create_request = urllib.request.Request(url, data=encoded_data, method='POST')
            create_request.add_header('dmtool-userid', str(self.dmtools_userid))
            create_request.add_header('dmtool-apikey', self.dmtools_apikey)
            create_request.add_header('Content-Type', 'application/json')
        
        try:
            with urllib.request.urlopen(create_request, context=self.context) as response:
                response_data = response.read().decode('utf-8')
                response_json_obj = json.loads(response_data)
                return response_json_obj
        except urllib.error.HTTPError as e:
            if e.code == 307:
                redirect_url = e.headers['Location']
                return self.create(data=data, url=redirect_url)
            else:
                raise
        return 1

    def read(self,subject='data',id=-1,url='',output='json'):
        if id == -1:
            read_url = self.api_server_url + subject + '/read_all'
        else:
            read_url = self.api_server_url + subject + "/read/?id_in=" + str(id)

        current_request = Request(read_url, headers=self.request_header)
        r = urllib.request.urlopen(current_request, context=self.context)
        string = r.read().decode('utf-8')
        _data_json_obj = json.loads(string)
        return _data_json_obj

    def query(self,subject='data',query_criteria={},url='',output='json'):
        data_dict = json.loads(query_criteria)
    
        # Convert the dictionary to a query string
        query_string = urlencode(data_dict)
        
        # Encode the entire query string to ensure special characters are properly encoded
        encoded_query_string = quote(query_string)
    
        print("query function encoded query string >>> ", encoded_query_string)
        query_url = self.api_server_url + subject + "/query/?query_in=" + encoded_query_string
        print("query_url >>>>>>>>>>>",  query_url)
        
        current_request = Request(query_url, headers=self.request_header)
        r = urllib.request.urlopen(current_request, context=self.context)
        string = r.read().decode('utf-8')
        _data_json_obj = json.loads(string)
        return _data_json_obj

    def read_by_plot_id(self,subject='data',id=-1,url='',output='json'):
        read_url = self.api_server_url + subject + "/read_by_plot_id/?id_in=" + str(id)

        current_request = Request(read_url, headers=self.request_header)
        r = urllib.request.urlopen(current_request, context=self.context)
        string = r.read().decode('utf-8')
        _data_json_obj = json.loads(string)
        return _data_json_obj

    def read_by_data_id(self,subject='data',id=-1,url='',output='json'):
        read_url = self.api_server_url + subject + "/read_by_data_id/?id_in=" + str(id)

        current_request = Request(read_url, headers=self.request_header)
        r = urllib.request.urlopen(current_request, context=self.context)
        string = r.read().decode('utf-8')
        _data_json_obj = json.loads(string)
        return _data_json_obj

    def read_by_user_id(self,subject='data',id=-1,url='',output='json'):
        read_url = self.api_server_url + subject + "/read_by_user_id/?id_in=" + str(id)

        current_request = Request(read_url, headers=self.request_header)
        r = urllib.request.urlopen(current_request, context=self.context)
        string = r.read().decode('utf-8')
        _data_json_obj = json.loads(string)
        return _data_json_obj
    
    def update(self,subject='data',id=-1,data={},url='',output='json'):
        if url == '':
            data_as_json = json.loads(data)
            subject_check = data_as_json['subject']
            if subject != subject_check:
                return {'message': 'wrong subject'}
            encoded_data = data.encode('utf-8')
            update_url = self.api_server_url + subject + "/update/?id_in=" + str(id)
            update_request = urllib.request.Request(update_url, data=encoded_data, method='PATCH')
            update_request.add_header('dmtool-userid', str(self.dmtools_userid))
            update_request.add_header('dmtool-apikey', self.dmtools_apikey)
            #update_request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            update_request.add_header('Content-Type', 'application/json')
        else:
            encoded_data = data.encode('utf-8')
            update_request = urllib.request.Request(url, data=encoded_data, method='PATCH')
            update_request.add_header('dmtool-userid', str(self.dmtools_userid))
            update_request.add_header('dmtool-apikey', self.dmtools_apikey)
            update_request.add_header('Content-Type', 'application/json')
            #create_request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        try:
            with urllib.request.urlopen(update_request, context=self.context) as response:
                response_data = response.read().decode('utf-8')
                response_json_obj = json.loads(response_data)
                return response_json_obj
        except urllib.error.HTTPError as e:
            if e.code == 307:
                redirect_url = e.headers['Location']
                print('redirect_url >>>>>>>>>>>>>>' , redirect_url)
                return self.update(id=id,data=data,url=redirect_url)
            elif e.code == 422:
                print("HTTP 422 Unprocessable Entity")
                error_response = e.read().decode('utf-8')
                return "Response content:", error_response
            else:
                print(f"Error: {e.code}")
                error_response = e.read().decode('utf-8')
                return "Response content:", error_response
        return 1

    def delete(self, subject='data',id=-1,data={},url='',output='json'):
        if url == '':
            delete_url = self.api_server_url + subject + "/delete/?id_in=" + str(id)
            delete_request = urllib.request.Request(delete_url, method='DELETE')
            delete_request.add_header('dmtool-userid', str(self.dmtools_userid))
            delete_request.add_header('dmtool-apikey', self.dmtools_apikey)
            delete_request.add_header('Content-Type', 'application/json')
        else:
            delete_request = urllib.request.Request(url, data=encoded_data, method='PATCH')
            delete_request.add_header('dmtool-userid', str(self.dmtools_userid))
            delete_request.add_header('dmtool-apikey', self.dmtools_apikey)
            delete_request.add_header('Content-Type', 'application/json')
            #create_request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        try:
            with urllib.request.urlopen(delete_request, context=self.context) as response:
                response_data = response.read().decode('utf-8')
                response_json_obj = json.loads(response_data)
                return response_json_obj
        except urllib.error.HTTPError as e:
            if e.code == 307:
                redirect_url = e.headers['Location']
                return self.delete_current(data_id_in, redirect_url)
            elif e.code == 422:
                print("HTTP 422 Unprocessable Entity")
                error_response = e.read().decode('utf-8')
                return "Response content:", error_response
            else:
                print(f"Error: {e.code}")
                error_response = e.read().decode('utf-8')
                return "Response content:", error_response

    def schema(self,subject='data',url='',output='json'):
        schema_url = self.api_server_url + subject + '/schema'
        current_request = Request(schema_url, headers=self.request_header)
        r = urllib.request.urlopen(current_request, context=self.context)
        string = r.read().decode('utf-8')
        _data_json_obj = json.loads(string)
        return _data_json_obj
    
    def clean_data_values(self, data_id_in):
        '''
        fastapi_url_data =self.api_server_url + "data/read/?id_in=" + str(data_id_in)
        request = Request(fastapi_url_data, headers=self.request_header)
        r = urllib.request.urlopen(request, context=self.context)
        string = r.read().decode('utf-8')
        a_data_json_obj = json.loads(string)
        data_string = a_data_json_obj[0]['data_values']
        '''
        a_data_json_obj = self.read(subject='data',id=data_id_in,url='',output='json')
        data_string = a_data_json_obj[0]['data_values']
        #all_plots_json_obj[1]
        #a_data_df = pd.DataFrame(a_data_json_obj, index=[0])
        data_string = data_string.replace("{[", "")
        data_string = data_string.replace("]}", "")
        #print(data_string)
        data_series = data_string.split("]")
        len(data_series)
        lol = []
        for l in range(0,len(data_series)):
            series_lol = []
            series_id = 0
            trace_id = l + 1
            single_set = data_series[l]
            set_list = single_set.split(";")
            for i in set_list:
                ## the following was added due to a different approach to data_string format
                r0 = i.replace(',[','')
                r1 = r0.replace('  ',' ')
                r2 = r1.replace('  ',' ')
                r3 = r2.replace('  ',' ')
                r4 = r3.replace('\r\n','')
                r5 = r4.replace('\t',' ')
                r6 = r5.replace(',',' ')
                r7 = r6.replace('  ',' ')
                r8 = r7.replace('  ',' ')
                r9 = r8.replace('\n',' ')
                r10 = r9.replace("', '"," ")
                r11 = r10.replace("['[",'')
                r12 = r11.replace(']','')
                r13 = r12.replace('[','')
                r14 = r13.replace(',','')
                s = r14.lstrip()
                z = s.split(" ");
                try:
                    raw_y = z[1]
                    raw_x = z[0].replace(",[", "")
                    #print('print split z >>>>', z)
                except:
                    #print(z)
                    raw_y = '0'
                    raw_x = '0'
                
                try:
                    x = float(raw_x)
                    y = float(raw_y)
                    #masses =  float(raw_x)
                    #cross_sections = float(raw_y)
                    formatted_x = "{:.5e}".format(x)
                    formatted_y = "{:.5e}".format(y)
                    append_x = float(formatted_x)
                    append_y = float(formatted_y)
                    #append_this = str(trace_id) + "," + formatted_x + "," + formatted_y
                    #append_this = '['+formatted_x+','+formatted_y+'],'
                    append_this = [append_x, append_y]
                    series_lol = series_lol + [append_this]
                except:
                    print('rejected z >> ', z)
            lol = lol + [series_lol]
            

        # Convert the nested data to a JSON string

        nested_data_string = json.dumps(lol)
        
        # Construct the payload with the nested JSON string
        payload = {
            "subject" : "data", 
            "data": nested_data_string
        }
        
        json_data = json.dumps(payload)
        print(json_data)
        #r = self.update_current(data_id_in, json_data,'')
        r = self.update(subject='data',id=data_id_in,data=json_data,url='',output='json')
        print(r)

    # the following were required by Dash to render an empty chart

    def initialise_plot(self):
        #self.this_plot = all_plots_df_in[all_plots_df_in['id']==plot_id_in]
        read_plot_url = self.api_server_url + "plot/read/?id_in="+ str(0)
        current_request = Request(read_plot_url, headers=self.request_header)
        r = urllib.request.urlopen(current_request, context=self.context)
        string = r.read().decode('utf-8')
        data_json_obj = json.loads(string)
        self.plot_df = pd.DataFrame(data_json_obj)
        self.plot_df['row_id'] = self.plot_df.index
        self.plot_df['updated_at'] = pd.to_datetime(self.v['updated_at'], errors='coerce')
        self.plot_df['updated_at'] = self.plot_df['updated_at'].dt.strftime('%Y%m%d%H%M')
        self.plot_start_x_range = float(self.plot_df.iloc[0]['x_min'])
        self.plot_stop_x_range = float(self.plot_df.iloc[0]['x_max'])
        self.plot_start_y_range = float(self.plot_df.iloc[0]['y_min'])
        self.plot_stop_y_range = float(self.plot_df.iloc[0]['y_max'])
        self.plot_name = self.plot_df.iloc[0]['name']
        self.plot_old_id = self.plot_df.iloc[0]['old_id']
        self.plot_fig_chart_empty = go.Figure(data=[go.Scatter(x=[], y=[])])
        self.make_blank_chart()
        
    ## need this for the inital build of the dash layout
    def make_blank_chart(self, height_in=800, width_in=800):
        y_title_text = r"$\text{WIMP Mass [GeV}/c^{2}]$"
        x_title_text = r"$\text{Cross Section [cm}^{2}\text{] (normalized to nucleon)}$"
        plot_title = 'Blank Chart'
        #plot_title
        ## create empty chart
        self.plot_fig_chart_empty = go.Figure(data=[go.Scatter(x=[], y=[])])
        self.plot_fig_chart_empty.update_layout( autosize=False, width=width_in, height=height_in, )
        self.plot_fig_chart_empty.update_layout(xaxis_range=[-1,-4])
        self.plot_fig_chart_empty.update_layout(yaxis_range=[-1,-4])
        self.plot_fig_chart_empty.update_layout(
                margin=dict(l=0, r=0, t=20, b=0),
                paper_bgcolor="LightSteelBlue",)
    
        self.plot_fig_chart_empty.update_layout(
            title=dict(text=plot_title , font=dict(size=18), automargin=True, yref='paper')
        )
        self.plot_fig_chart_empty.update_xaxes(
            #title_text=x_title_text,
            type="log"
            #type="linear"
        )
        self.plot_fig_chart_empty.update_yaxes(
            #title_text=y_title_text,
            type="log"
            #type="linear"
        )
    
    def get_data_for_plot(self, plot_id_in):
        self.plot_id = plot_id_in
        self.data_df = pd.DataFrame()
        self.data_data_df = pd.DataFrame()
        r = self.read_by_plot_id(subject='data_display',id=plot_id_in,url='',output='json')
        #data_display_json_obj = json.loads(string)
        self.data_display_df = pd.DataFrame(r)
        self.data_display_df['row_id'] = self.data_display_df.index
        self.data_display_df['updated_at'] = pd.to_datetime(self.data_display_df['updated_at'], errors='coerce')
        self.data_display_df['updated_at'] = self.data_display_df['updated_at'].dt.strftime('%Y%m%d%H%M')
        for index, row in self.data_display_df.iterrows():
            #print(row['c1'], row['c2']
            #print('data id from data >>>>', row['data_id'])
            data_id = row['data_id']
            r = self.read(subject='data',id=data_id ,url='',output='json')
            a_data_json_obj = r[0]
            data_label = a_data_json_obj['data_label']
            data_string = a_data_json_obj['data']
            list_data = ast.literal_eval(data_string)
            # Convert the string back to a list of lists of lists
            # reconstructed_list = json.loads(data_string)
            # print("Deserialized list:", reconstructed_list)
            
            # Flatten the list and add a reference to the top-level list
            flattened_data = []
            for i, sublist in enumerate(list_data):
                for inner_list in sublist:
                    flattened_data.append([i+1] + inner_list)
            
            # Create a DataFrame from the flattened list
            columns = ['trace_id', 'x', 'y']
            data_data_resp_df = pd.DataFrame(flattened_data, columns=columns)

            data_df_resp = pd.DataFrame(data=a_data_json_obj, index=[0])

            try:
                y_rescale = float(a_data_json_obj['y_rescale'])
            except:
                y_rescale = 1
            try:
                x_rescale = float(a_data_json_obj['x_rescale'])
            except:
                x_rescale = 1
            
            ## when do we rescale?
            data_data_resp_df['cross_sections'] = data_data_resp_df['y'].astype(float).apply(lambda y: y * y_rescale)
            data_data_resp_df['masses'] = data_data_resp_df['x'].astype(float).apply(lambda x: x * x_rescale)
            data_data_resp_df['trace_name'] = data_label
            data_data_resp_df['data_id'] = row['data_id']

            self.data_data_df = pd.concat([self.data_data_df,data_data_resp_df])
            self.data_df = pd.concat([self.data_df,data_df_resp])

        print("self.data_data_df >>>>>>>>>>>", self.data_data_df)
        print("self.data_df >>>>>>>>>>>>>>>>" , self.data_df)
              
        
        #trace_list = data_data_df[['data_id','trace_id']].drop_duplicate()
        trace_list_refs = self.data_data_df[['data_id','trace_id','trace_name']].copy()
        self.trace_list = trace_list_refs.drop_duplicates()

        #data_data_df.head(5)
        self.plot_min_cross_sections = self.data_data_df['cross_sections'].min()
        self.plot_max_cross_sections = self.data_data_df['cross_sections'].max()
        self.plot_min_masses = self.data_data_df['masses'].min()
        self.plot_max_masses = self.data_data_df['masses'].max()

    
    def create_plot(self, height_in=800, width_in=800):
        r = self.read(subject='plot',id=self.plot_id,url='',output='json')
        self.plot_name = r[0]['name']
        self.plot_old_id = r[0]['old_id']
        
        #plot_square_dimensions = height_in

        m1 = go.layout.Margin(l=20,r=10,b=20,t=20,pad=0)
        hw = go.Layout(autosize=False,width=width_in,height=height_in)
        y_title_text = r"$\text{Cross Section [cm}^{2}\text{] (normalized to nucleon)}$"

        y1 = go.layout.YAxis(#title=y_title_text,
                            title_standoff = 0,
                            #range=[start_y_range,stop_y_range],
                            type="log",
                            #type="linear",
                            titlefont=go.layout.yaxis.title.Font(color='SteelBlue'))

        x_title_text = r"$\text{WIMP Mass [GeV}/c^{2}]$"
        x1 = go.layout.XAxis(#title=x_title_text,
                            title_standoff = 0,
                            type="log",
                            #type="linear",
                            #range=[start_x_range,stop_x_range],
                            titlefont=go.layout.xaxis.title.Font(color='SteelBlue'))


        ##title1=go.layout.Title(text="Dark Matter Detection Results")

        self.fig_chart_populated = go.Figure(
            data=[go.Scatter(x=[], y=[])],
            layout=go.Layout(
                margin=m1,
                yaxis= y1,
                xaxis= x1
            )
        )

        self.plot_title = self.plot_name + " - P: " + str(self.plot_id) + " - O: " + str(self.plot_old_id)

        self.fig_chart_populated.update_layout(
            title=dict(text=self.plot_title ,font=dict(size=16),automargin=True,yref='paper')
        )

        self.fig_chart_populated.update_layout(hw)

        for index, row in self.data_display_df.iterrows():
            #print(row['limit_id'])
            data_id_selected = row['data_id']
            #print('selected data_id >>', data_id_selected)
            #data_about_selected_df = self.data_about_df[self.data_about_df['data_id']==data_id_selected].copy()
            data_display_selected_df = self.data_display_df[self.data_display_df['data_id']==data_id_selected].copy()
            #data_data_selected_df = self.data_data_df[self.data_data_df['data_id']==data_id_selected].copy()
            trace_style = data_display_selected_df['style'].iloc[0]
            trace_color = data_display_selected_df['color'].iloc[0]
            pt = PlotlyTrace()
            print("trace_color, trace_style >>>>>>>>>>>" , trace_color, trace_style)
            pt.set_values(trace_color, trace_style)
            traces = self.trace_list[self.trace_list['data_id']==data_id_selected]
            for index, trace_row in traces.iterrows():
                #print(row)
                trace_data = self.data_data_df[(self.data_data_df['data_id']==\
                                                trace_row['data_id']) & (self.data_data_df['trace_id']==trace_row['trace_id'])]
                #print(trace_data)
                #print("trace_data >>>>" , trace_data)
                trace_name = trace_row['trace_name']
                print("trace_name, pt.__dict__ >>>>", trace_name, pt.__dict__)
                self.fig_chart_populated.add_trace(go.Scatter(pt.__dict__,
                                                x=trace_data['masses'],
                                                y=trace_data['cross_sections'],
                                                name=trace_name,
                                                        showlegend=False
                                                    ))
    def create_populated_legend(self):
        rows_list = list(range(1,20))
        cols_list = list(range(1,4))

        table_rows=20
        table_cols=3
        #plot_square_dimensions = screen_height_in / 2
        legend_width = 600 ## this will be a maximum and will shrink if screen size < 800
        legend_height = 20 * 16
        self.fig_chart_legend = make_subplots(
                        column_titles = ['data_id','format'],
                        rows=table_rows,
                        cols=table_cols,
                        horizontal_spacing = 0.00,
                        vertical_spacing = 0.00,
                        #subplot_titles=(titles)
                        column_widths=[0.1,0.8,0.1])

        self.fig_chart_legend.update_layout(
            #    autosize=False,
                width=legend_width,
                height=legend_height,
                margin=dict(
                    l=0,
                    r=0,
                    b=0,
                    t=0,
                    pad=0
                ),
                paper_bgcolor="LightSteelBlue",
            )

        self.fig_chart_legend.update_xaxes(showgrid=False)
        self.fig_chart_legend.update_yaxes(showgrid=False)
        #legend
        self.fig_chart_legend.update_layout(showlegend=False)
        #x axis
        self.fig_chart_legend.update_xaxes(visible=False)
        #y axis
        self.fig_chart_legend.update_yaxes(visible=False)

        self.fig_chart_legend.data = []
        #fig_legend_out.show()

        # Any changes to the fig must be applied to the DataFrame as the dataframe
        # will be used when the plot is saved.
        # Saving zoom is still to be implemented

        #print("CD : data_display_df>>>>>>>>>", data_display_df_in)

        self.display_legend_df = self.data_display_df[['data_id','color','style']].copy()
        self.display_legend_df.drop_duplicates(inplace=True)
        print("self.display_legend_df >>>>>>>>>>>>>>>>",  self.display_legend_df)
        
        rowloop = 1
        for index, row in self.display_legend_df.iterrows():
            print("row['data_id' >>>>", row['data_id'])
            print("self.data_df >>>>>>>>>>", self.data_df)
            print(type(row['data_id']))
            print(self.data_df.dtypes)
            data_selected_df = self.data_df[self.data_df['id']==int(row['data_id'])].copy()
            print("data_selected_df >>>>>>>>>>>>>>>>", data_selected_df)
            trace_name = data_selected_df['data_label'].iloc[0]
            for c in cols_list: #enumerate here to get access to i
                # STEP 2, notice position of arguments!
                #table_column_names = ['data_id','data_label','format']
                scatter_mode_list = ['text-number','text-text','format']
                table_column_names = ['data_id','trace_name','format']
                trace_style = row['style']
                trace_color = row['color']
                data_id = row['data_id']
                pt = PlotlyTrace()
                pt.set_values(trace_color, trace_style)
                #tc.set_row_col(rowloop, c)
                #scatter_mode_list = ['text-number','text-text','format']
                #current_column = table_column_names[c-1]
                #current_mode = scatter_mode_list[c-1]
                current_column = table_column_names[c-1]
                current_mode = scatter_mode_list[c-1]
                #print(rowloop,current_column, current_mode )
                if current_mode =='format':
                    mode = pt.__dict__['mode']
                    #fill = 'toself'
                    fill = pt.__dict__['fill']
                    if mode == 'lines' and fill == 'none':
                        x_data = [0,1]
                        y_data = [0.5,0.5]
                    elif mode == 'lines' and fill == 'toself':
                        x_data = [0,1,1,0,0]
                        y_data = [0,0,1,1,0]
                    else:
                        x_data = [0,1]
                        y_data = [0.5,0.5]

                    self.fig_chart_legend.add_trace(go.Scatter(pt.__dict__,x=x_data,
                                                y=y_data),
                                row=rowloop, #index for the subplot, i+1 because plotly starts with 1
                                col=c)

                if current_mode =='text-number':
                    self.fig_chart_legend.add_trace(go.Scatter(x=[1,2],
                                            textposition='middle right',
                                            y=[1,1],
                                            mode='text',
                                            text=[str(data_id),'']
                                            ),
                                row=rowloop, #index for the subplot, i+1 because plotly starts with 1
                                col=c)
                if current_mode =='text-text':
                    self.fig_chart_legend.add_trace(go.Scatter(x=[1,2],
                                            textposition='middle right',
                                            y=[1,1],
                                            mode='text',
                                            text=[trace_name,'']
                                            ),
                                row=rowloop, #index for the subplot, i+1 because plotly starts with 1
                                col=c)

            rowloop=rowloop+1
            self.fig_chart_legend.update_xaxes(showgrid=False)
            self.fig_chart_legend.update_yaxes(showgrid=False)
            #legend
            self.fig_chart_legend.update_layout(showlegend=False)
            #x axis
            self.fig_chart_legend.update_xaxes(visible=False)
            #y axis
            self.fig_chart_legend.update_yaxes(visible=False)
    
    def get_mpl_plot(self, plot_id_in, width_in=600, height_in=600, font_size_in=6, small_trigger=200):
        
        datasets = self.read_by_plot_id(subject='data_display',id=plot_id_in)
        
        px = 1/100
        
        # Create the figure
        fig = plt.figure(figsize=(width_in*px, height_in*px), linewidth=1, edgecolor='black', facecolor='#98A4AE')
        
        # Create an 8x8 grid of subplots
        gs = gridspec.GridSpec(64, 64)
        
        # Define the grid positions for the middle 4 grid boxes
        # This spans rows 2-5 and columns 2-5
        ax = fig.add_subplot(gs[2:63, 2:63])
        ax.set_facecolor('white')
        ax.tick_params(axis='both', labelsize=8)
        
        for d in datasets:
            data_id = d['data_id']
            trace_data = self.read(id=data_id)
            try:
                y_rescale = float(trace_data[0]['y_rescale'])
            except:
                y_rescale = 1
            try:
                x_rescale = float(trace_data[0]['x_rescale'])
            except:
                x_rescale = 1
            trace_name = trace_data[0]['data_label']
            string_data = trace_data[0]['data']
            style = d['style']
            color = d['color']
            pt = MplTrace()
            pt.set_values(color, style)
            list_data = ast.literal_eval(string_data)
            trace_count = len(list_data)
            trace_names_int = list(range(0,trace_count))
            trace_names_int
            trace_names = []
            for t in trace_names_int:
                trace_names.append(str(t))
                x = [item[0] for item in list_data[t]]
                y = [item[1] for item in list_data[t]]
                cross_sections =  [float(yi) * y_rescale for yi in y]
                masses =  [float(xi) * x_rescale for xi in x]
        
                if pt.fill == False:
                    ax.plot(masses, cross_sections,**pt.line_plot_kwargs)
                else:
                    ax.plot(masses, cross_sections, **pt.fill_plot_kwargs)  # `marker='o'` shows points on vertices
                    ax.fill(masses, cross_sections, **pt.fill_plot_kwargs) 
        
        plt.xscale('log')
        plt.yscale('log')

        y_title_text = r"$\text{WIMP Mass} \, [\mathrm{GeV}/c^{2}]$"
        x_title_text = r"$\text{Cross Section} \, [\mathrm{cm}^{2}] \, \text{(normalized to nucleon)}$"
        plot_title = r"$\text{WIMP Cross Section vs Mass (Plot ID: " + str(plot_id_in) + r")}$"

    
        # Add text manually (adjust coordinates to position it above the plot)
        ax.text(0.5, 1.02, plot_title, fontsize=8, ha='center', va='bottom', transform=ax.transAxes)
        
        # Set axis limits to ensure the plot is in view
        x_title_text = r"$\text{Cross Section} \, [\mathrm{cm}^{2}] \, \text{(normalized to nucleon)}$"
        y_title_text = r"$\text{WIMP Mass} \, [\mathrm{GeV}/c^{2}]$"
        
        # Add text manually (adjust coordinates to position it correctly)
        # Rotate the text to make it vertical
        ax.text(-0.12, 0.5, y_title_text, fontsize=8, va='center', ha='center', rotation=90, transform=ax.transAxes)
        
        # Add text manually (adjust coordinates to position it correctly)
        ax.text(0.5, -0.08, x_title_text, fontsize=8, ha='center', transform=ax.transAxes)

        return plt

    def get_mpl_legend(self, plot_id_in):
        datasets = self.read_by_plot_id(subject='data_display',id=plot_id_in)
        
        handles = []
        
        for d in datasets:
            data_id = d['data_id']
            trace_data = self.read(id=data_id)
            trace_name = trace_data[0]['data_label']
            string_data = trace_data[0]['data']
            style = d['style']
            color = d['color']
            pt = MplTrace()
            pt.set_values(color, style)
            list_data = ast.literal_eval(string_data)
            trace_count = len(list_data)
            trace_names_int = list(range(0,trace_count))
            #trace_names_int
            trace_names = []
            for t in trace_names_int:
                trace_names.append(str(t))
                x = [item[0] for item in list_data[t]]
                y = [item[1] for item in list_data[t]]
                
                if pt.fill == False:
                    append_this = mlines.Line2D([], [], label=trace_name, **pt.line_plot_kwargs)
                else:
                    append_this = mpatches.Patch(label=trace_name, **pt.fill_plot_kwargs)
                handles.append(append_this)
        
        labels = [handle.get_label() for handle in handles]

        #px = 1/plt.rcParams['figure.dpi']  # pixel in inches
        px = 1/100  # pixel in inches

        num_points = len(trace_names_int)
        fig_height = num_points * 10 * px
        fig_width = 5
        
        fig, ax = plt.subplots(figsize=(fig_width,fig_height))
        # Create a new figure just for the legend

        ax.legend(handles=handles, labels=labels, loc='center', fontsize=8, labelspacing=1)
        ax.axis('off')  # Hide the axes
        return plt
        

class PlotlyTrace():
    def __init__(self):
      self.mode = 'lines' ### ['lines', 'lines+markers', 'markers']
      self.line = {'color' :'red', 'width': 1, 'dash' : 'solid'}
      #self.color = 'red'
      self.marker = {'symbol':'x'}
      #self.symbol = 'x'
      self.fillcolor = 'rgba(0,255,255,0.05)'
      self.opacity = 1
      self.fill = 'toself'
    
    def color_rgba(self, color_in):
      if color_in == 'cyan':
          self.fillcolor = 'rgba(0,255,255,0.05)'
      elif color_in == 'red':
          self.fillcolor = 'rgba(255,0,0,0.05)'
      elif color_in == 'blue':
          self.fillcolor = 'rgba(0,0,255,0.05)'
      elif color_in == 'green':
          self.fillcolor = 'rgba(0,255,0,0.05)'
      elif color_in == 'black':
          self.fillcolor = 'rgba(0,0,0,0.05)'
      elif color_in == 'magenta':
          self.fillcolor = 'rgba(255,0,255,0.05)'
      elif color_in == 'yellow':
          self.fillcolor = 'rgba(255,255,0,0.05)'
      elif color_in == 'white':
          self.fillcolor = 'rgba(255,255,255,0.05)'
      else:
          self.fillcolor = 'rgba(255,0,0,0.05)'
    
    def clean_the_color_in(self, color_in):
        if color_in in ('k', 'black', 'Blk'):
            return 'black'
        elif color_in in ('r', 'red', 'Red'):
            return 'red'
        elif color_in in  ('dkg','DkG', 'green', 'Grn'):
            return 'green'
        elif color_in in  ('ltg', 'LtG'):
            return 'green'
        elif color_in in ('LtR', 'ltr'):
            return 'red'
        elif color_in in  ('b'):
            return 'blue'
        elif color_in in  ('LtB','ltb', 'Blue'):
            return 'blue'
        elif color_in in  ('c', 'Cyan'):
            return 'cyan'
        elif color_in in ('g10','g20','g30','g40','g50','g60','g70','g80','g90', 'G60'):
            return 'grey'
        elif color_in in ('blue', 'dkb', 'DkB'):
            return 'blue'
        elif color_in in ('red','dkr'):
            return 'red'
        elif color_in in ('g', 'grey'):
            return 'grey'
        elif color_in in ('m', 'magenta', 'Mag'):
            return 'magenta'
        elif color_in in ('y', 'yellow'):
            return 'yellow'
        elif color_in in ('w', 'white'):
           return 'white'
        else :
            return 'purple'
    
    def set_values(self, color_in, style_in):
        cleaned_color = self.clean_the_color_in(color_in)
        #self.color = cleaned_color
        if style_in in ('dot', 'dotted', 'Dot'):
            self.mode = 'lines' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.marker = {'symbol':'x'}
            #self.symbol = 'x'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'none'
        elif style_in in ('dash', 'Dash'):
            self.mode = 'lines' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'dash'}
            self.marker = {'symbol':'x'}
            #self.symbol = 'x'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'none'
        elif style_in in ('fill', 'Fill'):
            self.mode = 'lines' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.marker = {'symbol':'x'}
            #self.symbol = 'x'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'toself'
        elif style_in in ('Line', 'line', 'lines'):
            self.mode = 'lines' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.marker = {'symbol':'x'}
            #self.symbol = 'x'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'none'
        elif style_in == "point":
            self.mode = 'lines+markers' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.marker = {'symbol':'x-dot'}
            #self.symbol = 'x-dot'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'toself'
        elif style_in in ('cross', 'Cross'):
            #self.style = 'cross'
            self.mode = 'lines+markers' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.line_width = 1
            self.marker = {'symbol':'cross'}
            #self.symbol = 'cross'
            self.opacity = 1
            self.fill = 'none'
        elif style_in ==  "circle":
            self.mode = 'lines+markers' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.marker = {'symbol':'circle'}
            #self.symbol = 'circle'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'none'
        elif style_in ==  "plus":
            self.mode = 'lines+markers' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.marker = {'symbol':'square-cross'}
            #self.symbol = 'square-cross'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'toself'
        elif style_in in ("asterisk",'star'):
            self.mode = 'lines+markers' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.marker = {'symbol':'star'}
            #self.symbol = 'star'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'none'
        elif style_in in ('pentagon', "pent"):
            self.mode = 'lines+markers' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.marker = {'symbol':'pentagon'}
            #self.symbol = 'pentagon'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'toself'
        elif style_in == ("hex", 'hexagon'):
            self.mode = 'lines+markers' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.marker = {'symbol':'hexagon'}
            #self.symbol = 'hexagon'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'none'
        elif style_in == ("triu", 'triangle'):
            self.mode = 'lines+markers' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.marker = {'symbol':'triangle-up'}
            #self.symbol = 'triangle'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'none'
        elif style_in ==  "trid":
            self.mode = 'lines+markers' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.marker = {'symbol':'triangle-down'}
            #self.symbol = 'triangle-down'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'toself'
        elif style_in ==  "tril":
            self.mode = 'lines+markers' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.marker = {'symbol':'triangle-left'}
            #self.symbol = 'triangle-left'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'none'
        elif style_in ==  "trir":
            self.mode = 'lines+markers' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.marker = {'symbol':'triangle-right'}
            #self.symbol = 'triangle-right'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'none'
        else:
            self.mode = 'lines' ### ['lines', 'lines+markers', 'markers']
            self.line = {'color' :cleaned_color, 'width': 1, 'dash' : 'solid'}
            self.marker = {'symbol':'x'}
            #self.symbol = 'x'
            _rgba = self.color_rgba(cleaned_color)
            self.fillcolor = _rgba
            self.opacity = 1
            self.fill = 'none'


class MplTrace():
    def __init__(self):
      self.color = 'red'
      self.linestyle = None
      self.linewidth = 1
      self.marker = None
      self.markersize = 0
      self.alpha = 1
      self.fill = False
      self.line_plot_kwargs = {
                "color": self.color,        # Line color
                "linestyle": self.linestyle,      # Dashed line
                "linewidth": self.linewidth,         # Line width
                "marker": self.marker,          # Circle marker
                "markersize": self.markersize,        # Marker size
                "alpha": self.alpha         # Transparency level
            }
      self.fill_plot_kwargs = {
                "color":  self.color,        # Line color
                "linestyle": self.linestyle,      # Dashed line
                "linewidth": self.linewidth,         # Line width
                "alpha": self.alpha          # Transparency level
            }
    
    def refresh_kwargs(self):
        self.line_plot_kwargs = {
                "color": self.color,        # Line color
                "linestyle": self.linestyle,      # Dashed line
                "linewidth": self.linewidth,         # Line width
                "marker": self.marker,          # Circle marker
                "markersize": self.markersize,        # Marker size
                "alpha": self.alpha         # Transparency level
            }

        self.fill_plot_kwargs = {
                "color":  self.color,        # Line color
                "linestyle": self.linestyle,      # Dashed line
                "linewidth": self.linewidth,         # Line width
                "alpha": self.alpha          # Transparency level
            }
        
    
    def set_color(self, color_in):
        if color_in in ('k', 'black', 'Blk'):
            self.color = 'black'
            self.alpha = 1
        elif color_in in ('r', 'red', 'Red'):
            self.color =  'red'
            self.alpha = 1
        elif color_in in  ('dkg','DkG', 'green', 'Grn'):
            self.color =  'green'
            self.alpha = 1
        elif color_in in  ('ltg', 'LtG'):
            self.color =  'green'
            self.alpha = 0.5
        elif color_in in ('LtR', 'ltr'):
            self.color =  'red'
            self.alpha = 0.5
        elif color_in in  ('b'):
            self.color =  'blue'
            self.alpha = 1
        elif color_in in  ('LtB','ltb', 'Blue'):
            self.color =  'blue'
            self.alpha = 0.5
        elif color_in in  ('c', 'Cyan'):
            self.color =  'cyan'
            self.alpha = 1
        elif color_in in ('g10','g20','g30','g40','g50','g60','g70','g80','g90', 'G60'):
            self.color =  'grey'
            try:
                shade = int(color_in[1:])/100
                self.alpha = shade
            except:
                 self.alpha = 1
        elif color_in in ('blue', 'dkb', 'DkB'):
            self.color =  'blue'
            self.alpha = 1
        elif color_in in ('red','dkr'):
            self.color =  'red'
            self.alpha = 1
        elif color_in in ('g', 'grey'):
            self.color =  'grey'
            self.alpha = 1
        elif color_in in ('m', 'magenta', 'Mag'):
            self.color =  'magenta'
            self.alpha = 1
        elif color_in in ('y', 'yellow'):
            self.color =  'yellow'
            self.alpha = 1
        elif color_in in ('w', 'white'):
            self.color =  'white'
            self.alpha = 1
        else :
            self.color =  'purple'
            self.alpha = 1
    
    def set_values(self, color_in, style_in):
        self.set_color(color_in)
        #self.color = cleaned_color
        if style_in in ('dot', 'dotted', 'Dot'):
            self.linestyle = ":"
            self.linewidth = 1
            self.marker = None
            self.markersize = 0
            self.alpha = 1
            self.fill = False
        elif style_in in ('dash', 'Dash'):
            self.linestyle = '--'
            self.linewidth = 1
            self.marker = None
            self.markersize = 0
            self.alpha = 1
            self.fill = False
        elif style_in in ('fill', 'Fill'):
            self.linestyle = None
            self.linewidth = 0
            self.marker = None
            self.markersize = 0
            self.alpha = 0.3
            self.fill = True
        elif style_in in ('Line', 'line', 'lines'):
            self.linestyle = None
            self.linewidth = 1
            self.marker = None
            self.markersize = 0
            self.alpha = 1
            self.fill = False
        elif style_in == "point":
            self.linestyle = None
            self.linewidth = 1
            self.marker = '.'
            self.markersize = 1
            self.alpha = 1
            self.fill = False
        elif style_in in ('cross', 'Cross'):
            self.linestyle = None
            self.linewidth = 1
            self.marker = 'x'
            self.markersize = 0
            self.alpha = 1
            self.fill = False
        elif style_in ==  "circle":
            self.linestyle = None
            self.linewidth = 1
            self.marker = 'o'
            self.markersize = 1
            self.alpha = 1
            self.fill = False
        elif style_in ==  "plus":
            self.linestyle = None
            self.linewidth = 1
            self.marker = '+'
            self.markersize = 1
            self.alpha = 1
            self.fill = False
        elif style_in in ("asterisk",'star'):
            self.linestyle = None
            self.linewidth = 1
            self.marker = '*'
            self.markersize = 0
            self.alpha = 1
            self.fill = False
        elif style_in in ('pentagon', "pent"):
            self.linestyle = None
            self.linewidth = 1
            self.marker = "p"
            self.markersize = 0
            self.alpha = 1
            self.fill = False
        elif style_in == ("hex", 'hexagon'):
            self.linestyle = None
            self.linewidth = 1
            self.marker = "h"
            self.markersize = 0
            self.alpha = 1
            self.fill = False
        elif style_in == ("triu", 'triangle'):
            self.linestyle = None
            self.linewidth = 1
            self.marker = "^"
            self.markersize = 1
            self.alpha = 1
            self.fill = False
        elif style_in ==  "trid":
            self.linestyle = None
            self.linewidth = 1
            self.marker = "v"
            self.markersize = 1
            self.alpha = 1
            self.fill = False
        elif style_in ==  "tril":
            self.linestyle = None
            self.linewidth = 1
            self.marker = "<"
            self.markersize = 0
            self.alpha = 1
            self.fill = False
        elif style_in ==  "trir":
            self.linestyle = None
            self.linewidth = 1
            self.marker = ">"
            self.markersize = 1
            self.alpha = 1
            self.fill = False
        else:
            self.linestyle = None
            self.linewidth = 1
            self.marker = None
            self.markersize = 0
            self.alpha = 1
            self.fill = True
        self.refresh_kwargs()


class DMToolTestData():
    def __init__(self):
        self.mstring = StringIO("""x,y
          70,50
          90,100
          90,0
          70,0
          70,50
          60,25
          50,0
          30,50
          30,0
          10,0
          10,100
          30,100
          60,25
        """)
        
        self.mdf = pd.read_csv(self.mstring, sep=",")
        self.mdf =  self.mdf.astype(float)
        
        self.ostring = StringIO("""x,y
          50,0
          65,5
          80,15
          87,30
          90,50
          87,70
          80,90
          65,97
          50,100
          60,85
          65,70
          67,65
          70,50
          67,35
          65,25
          60,12
          50,0
          """)
       
        self.ReadLetterO()
    
        self.tstring = StringIO("""x,y
          10,80
          10,100
          90,100
          90,80
          60,80
          60,0
          40,0
          40,80
          10,80
          """)
    
        self.tdf = pd.read_csv(self.tstring, sep=",")
        self.tdf =  self.tdf.astype(float)
    
        self.lstring = StringIO("""x,y
          10,0
          100,0
          100,20
          30,20
          30,100
          10,100
          10,0
          """)
    
        self.ldf = pd.read_csv(self.lstring, sep=",")
        self.ldf =  self.ldf.astype(float)
    
        self.dstring = StringIO("""x,y
          30,0
          65,5
          90,25
          100,50
          90,75
          65,95
          30,100
          60,85
          75,75
          80,50
          75,35
          60,15
          30,0
          10,0
          10,100
          30,100
          30,0
          """)
    
        self.ddf = pd.read_csv(self.dstring, sep=",")
        self.ddf =  self.ddf.astype(float)
    
        #self.MakeDMTool()
    
    #################################
    def ReadLetterO(self):
        
        odf_stage = pd.read_csv(self.ostring, sep=",")
        odf_stage =  odf_stage.astype(float)
        
        odf_out = odf_stage.copy()
        
        def reflectx(x_in):
            return 50 - (x_in-50)

        odf_out['x'] = odf_out['x'].apply(reflectx)
        
        #odf_out['x'] = 50 - (odf_out['x']-50)
        
        #odf_out = odf_out.assign(x=50)
        
        odf_out = pd.concat([odf_out, odf_stage],ignore_index=True)
        self.odf = odf_out
   
    def MakeDMTool(self,data_id_in,trace_id_in):
        
        def add100(x_in):
            return (x_in + 100)
        
        dmtool_out = self.ddf.copy()
        
        dmtool_out['data_id'] = data_id_in
        dmtool_out['trace_id'] = trace_id_in
        dmtool_out['trace_name'] = 'd'
        
        #"M"
        df_working = self.mdf.copy()
        df_working['data_id'] = data_id_in
        df_working['trace_id'] = trace_id_in + 1
        df_working['trace_name'] = 'm'

        df_working['x'] = df_working['x'].apply(add100)
        
        dmtool_out = pd.concat([dmtool_out, df_working], ignore_index=True)
        
        #"T"
        
        df_working = self.tdf.copy()
        df_working['data_id'] = data_id_in
        df_working['trace_id'] = trace_id_in + 2
        df_working['trace_name'] = 't'

        df_working['x'] = df_working['x'].apply(add100)
        df_working['x'] = df_working['x'].apply(add100)
        
        dmtool_out = pd.concat([dmtool_out, df_working], ignore_index=True)
        
        #"O1 & O2"
        
        df_working = self.odf.copy()
        df_working['data_id'] = data_id_in
        df_working['trace_id'] = trace_id_in + 3
        df_working['trace_name'] = 'o1'

        df_working['x'] = df_working['x'].apply(add100)
        df_working['x'] = df_working['x'].apply(add100)
        df_working['x'] = df_working['x'].apply(add100)
        
        dmtool_out = pd.concat([dmtool_out, df_working], ignore_index=True)
        
        df_working['data_id'] = data_id_in
        df_working['trace_id'] = trace_id_in + 4
        df_working['trace_name'] = 'o2'
        df_working['x'] = df_working['x'].apply(add100)
        
        dmtool_out = pd.concat([dmtool_out, df_working], ignore_index=True)
        
        #"L"
        
        df_working = self.ldf.copy()
        df_working['data_id'] = data_id_in
        df_working['trace_id'] = trace_id_in + 5
        df_working['trace_name'] = 'l'

        df_working['x'] = df_working['x'].apply(add100)
        df_working['x'] = df_working['x'].apply(add100)
        df_working['x'] = df_working['x'].apply(add100)
        df_working['x'] = df_working['x'].apply(add100)
        df_working['x'] = df_working['x'].apply(add100)
        
        dmtool_out = pd.concat([dmtool_out, df_working], ignore_index=True)
        
        ## out
        
        self.dmtdf = dmtool_out
