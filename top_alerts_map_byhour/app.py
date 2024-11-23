############
#   APP2   #
############

from shiny import App, render, ui, reactive
from shinywidgets import render_altair, output_widget
import pandas as pd
import json
import altair as alt 

# import top alerts data as df
df = pd.read_csv('top_alerts_map_byhour/top_alerts_map_byhour.csv')
df['type_subtype'] = df['updated_type'] + '_' + df['updated_subtype']


# import geodata
alt.data_transformers.disable_max_rows()
file_path = "Boundaries - Neighborhoods.geojson"
with open(file_path) as f:
    chicago_geojson = json.load(f)
geo_data = alt.Data(values=chicago_geojson["features"])  

# UI
app_ui = ui.page_fluid(
    ui.input_slider('hour','Select hour',min=0,max=23,value=12,step=1),
    ui.input_select('type_subtype', 'Choose type and subtype', choices=[]),
    output_widget('top_alerts_byhour_plot')  
)


# Server
def server(input, output, session):
    # Update dropdown
    @reactive.effect
    def update_dropdown():
        type_list = sorted(df['type_subtype'].unique())
        ui.update_select('type_subtype', choices=type_list)
    
    # Create Altair plot
    @render_altair
    def top_alerts_byhour_plot():

         # Filtered data for points
        selected_combination = input.type_subtype()
        selected_time = f"{input.hour():02d}:00"
        filtered_data = df[
            (df['type_subtype'] == selected_combination) &
            (df['hour'] == selected_time)
        ]

        # Background map
        background = alt.Chart(geo_data).mark_geoshape(
            fill='lightgray',
            stroke='white'
        ).project('albersUsa').properties(width=500, height=300)

        # points
        points = alt.Chart(filtered_data).mark_point().transform_window(
            rank='rank(count)',
            sort=[alt.SortField('count', order='descending')]
        ).transform_filter(
            alt.datum.rank <= 10
        ).encode(
            longitude='longitude_bin:Q',
            latitude='latitude_bin:Q',
            size='count:Q',
            tooltip=['longitude_bin', 'latitude_bin', 'count']
        )

        return background + points

# App
app = App(app_ui, server)

