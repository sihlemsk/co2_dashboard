import pandas as pd
import numpy as np
import panel as pn
import hvplot.pandas

#Enable Panel extensions
pn.extension('tabulator')

#Load data
df = pd.read_csv('https://raw.githubusercontent.com/sihlemsk/co2_dashboard/master/owid-co2-data.csv')

#Data Preprocessing
df = df.fillna(0)
df['gdp_per_capita'] = np.where(df['population'] != 0, df['gdp'] / df['population'], 0)
idf = df.interactive()

#Create widgets
year_slider = pn.widgets.IntSlider(name='Year Slider', start=1750, end=2020, step=5, value=1850)
yaxis_co2 = pn.widgets.RadioButtonGroup(name='Y axis', options=['co2', 'co2_per_capita'], button_type='success')
yaxis_co2_source = pn.widgets.RadioButtonGroup(name='Y axis', options=['coal_co2', 'oil_co2', 'gas_co2'], button_type='success')

#Define continents list
continents = ['World', 'Asia', 'Oceania', 'Europe', 'Africa', 'North America', 'South America', 'Antarctica']
continents_excl_world = ['Asia', 'Oceania', 'Europe', 'Africa', 'North America', 'South America', 'Antarctica']

#CO2 emissions by continent pipeline
co2_pipeline = (
    idf[(idf.year <= year_slider) & (idf.country.isin(continents))]
    .groupby(['country', 'year'])[yaxis_co2].mean()
    .to_frame()
    .reset_index()
    .sort_values(by='year')
    .reset_index(drop=True)
)

#CO2 emissions vs GDP pipeline
co2_vs_gdp_scatterplot_pipeline = (
    idf[(idf.year == year_slider) & (~idf.country.isin(continents))]
    .groupby(['country', 'year', 'gdp_per_capita'])['co2'].mean()
    .to_frame()
    .reset_index()
    .sort_values(by='year')
    .reset_index(drop=True)
)

#CO2 sources by continent pipeline
co2_source_bar_pipeline = (
    idf[(idf.year == year_slider) & (idf.country.isin(continents_excl_world))]
    .groupby(['year', 'country'])[yaxis_co2_source].sum()
    .to_frame()
    .reset_index()
    .sort_values(by='year')
    .reset_index(drop=True)
)

#Plots and tables
co2_plot = co2_pipeline.hvplot(x='year', by='country', y=yaxis_co2, line_width=2, title="CO2 emission by continent")

co2_vs_gdp_scatterplot = co2_vs_gdp_scatterplot_pipeline.hvplot(
    x='gdp_per_capita', y='co2', by='country', size=80, kind="scatter", alpha=0.7, legend=False, height=500, width=700)

co2_source_bar_plot = co2_source_bar_pipeline.hvplot(kind='bar', x='country', y=yaxis_co2_source, title="CO2 source by continent")

co2_table = co2_pipeline.pipe(pn.widgets.Tabulator, pagination='remote', page_size=10, sizing_mode='stretch_width')

# Dashboard layout
template = pn.template.FastListTemplate(
    title = 'World CO2 Emission Dashboard',
    sidebar = [pn.pane.Markdown('# CO2 Emissions and Climate Change'),
               pn.pane.Markdown('#### CO2 emissions are the primary driver of global climate change'),
               pn.pane.PNG('https://raw.githubusercontent.com/sihlemsk/co2_dashboard/master/Climate-Change-Transparent.png', sizing_model = 'scale_both'),
               pn.pane.Markdown('## Settings'),
               year_slider],
    main=[pn.Row(pn.Column(yaxis_co2, 
                           co2_plot.panel(width=700), margin=(0,25)), 
                 co2_table.panel(width=500)), 
          pn.Row(pn.Column(co2_vs_gdp_scatterplot.panel(width=600), margin=(0,25)), 
                 pn.Column(yaxis_co2_source, co2_source_bar_plot.panel(width=600)))],
    accent_base_color="#88d8b0",
    header_background="#88d8b0",
)

template.show()