#!/usr/bin/env python
# coding: utf-8

# # Distribuição de Renda de 2020 no Brasil
# 
# Este notebook analisa alguns aspectos da distribuição de renda no Brasil.
# 
# Os dados da  Receita Federal estão disponíveis através do portal de [Dados Abertos do Governo Federal](https://dados.gov.br/dados/conjuntos-dados/distribuio-de-renda).
# 
# ### Perguntas respondidas
# 
# - Como é a distribuição de renda no Brasil em 2020 (últimos dados)?
# - E a isenção fiscal de até 5k?
# - A concentração de renda piorou ou melhorou ao longo dos anos disponíveis?
# - Qual a tributação que cada centil paga?
# 
# ### Perguntas em aberto
# 
# - Como é a distribuição em outros países? É local ou sistemático essa diferença?
# 
# ## Código

# In[1]:
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# In[2]:
def convert_brazilian_number(value):
    """
    Convert Brazilian-formatted number string to float
    - Removes dots used as thousand separators
    - Replaces comma with dot for decimal separation
    """
    if pd.isna(value):
        return np.nan

    value = value.replace('.', '')
    value = value.replace(',', '.')
    return float(value)

def create_one_indexed_df(_df):
    _df = _df.reset_index()
    _df = _df.drop(["index"], axis=1)
    _df.index = _df.index + 1
    return _df

# In[4]:
def map_x_position(centil):
    if centil <= 99:
        return centil
    elif 1001 <= centil <= 1009:
        return 99 + (centil - 1000) * 0.1
    elif 100101 <= centil <= 100110:
        return 99.9 + (centil - 100100) * 0.01
    elif centil == 1001010:
        return 100
    return centil

def map_width(centil):
    std_width = 2.0
    if centil <= 99:
        return std_width
    elif 1001 <= centil <= 1009:
        return std_width / 2
    elif 100101 <= centil:
        return std_width / 2
    return std_width

def prepare_data_for_plotting(df, limit):
    df_graphed = df[(df['Centil'] <= limit)].copy()
    df_graphed = df_graphed[df_graphed["Ano-calendário"] == 2020]

    # Add position and width columns
    df_graphed['x_position'] = df_graphed['Centil'].apply(map_x_position)
    df_graphed['width'] = df_graphed['Centil'].apply(map_width)

    # Sort by x position
    return df_graphed.sort_values('x_position')

#%%
# Load and preprocess data
df_orig = pd.read_csv("data/distribuicao-renda.csv", sep=";")

# Apply initial filters to df_orig
df_orig["Quantidade de Contribuintes"] = df_orig["Quantidade de Contribuintes"]*1000
df_orig = df_orig[df_orig["Ente Federativo"] == "BRASIL"]
df_orig = df_orig.drop(["Ente Federativo"], axis=1)

# Convert Brazilian number format to float
for column in df_orig.columns:
    if df_orig[column].dtype == "object":
        try:
            df_orig[column] = df_orig[column].apply(convert_brazilian_number)
        except Exception as e:
            print(f"Error converting column {column}: {e}")

# Drop redundant centils
df_orig = df_orig[~df_orig["Centil"].isin([100, 10010])]

# Create one-indexed DataFrame
df_orig = create_one_indexed_df(df_orig)

# Create Razao Rendimentos Tributaveis - Limite Superior
df_orig['Razao_Rendimentos'] = ((df_orig['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'] / df_orig['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'].shift(1)) - 1)*100
df_orig['Razao_Rendimentos'] = df_orig['Razao_Rendimentos'].fillna(0)

#%%
df_orig.tail(33)

#%%
def plot_razao_rendimentos(df, year):
    # Prepare data for plotting
    df_graphed = df.copy()
    df_graphed['x_position'] = df_graphed['Centil'].apply(map_x_position)
    df_graphed = df_graphed[df_graphed["Ano-calendário"] == year]
    
    # Create filtered version without centil 7 and 99.99
    df_filtered = df_graphed[~df_graphed['Centil'].isin([1, 2, 3, 4, 5, 6, 7, 8, 1001010])].copy()
    
    # Create the plot
    fig = go.Figure()
    
    # Add line trace for full data
    fig.add_trace(go.Scatter(
        x=df_graphed['x_position'],
        y=df_graphed['Razao_Rendimentos'],
        mode='lines+markers',
        line=dict(color='rgb(33, 102, 172)', width=2),
        marker=dict(size=6),
        hovertemplate='Centil: %{x}<br>Razão: %{y:.2f}<extra></extra>',
        name='Todos os Centis',
        visible=True
    ))
    
    # Add line trace for filtered data
    fig.add_trace(go.Scatter(
        x=df_filtered['x_position'],
        y=df_filtered['Razao_Rendimentos'],
        mode='lines+markers',
        line=dict(color='rgb(33, 102, 172)', width=2),
        marker=dict(size=6),
        hovertemplate='Centil: %{x}<br>Razão: %{y:.2f}<extra></extra>',
        name='Excluindo Centil 7 e 99.99',
        visible=False
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'Razão entre Consecutivos Rendimentos Tributáveis por Centil {year}',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 14}
        },
        xaxis_title='Centil',
        yaxis_title='Razão entre Consecutivos Rendimentos',
        template='plotly_white',
        width=1200,
        height=600,
        showlegend=False
    )
    
    # Add buttons for switching between views
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                buttons=list([
                    dict(
                        args=[{"visible": [True, False]},
                              {"title": f"Razão entre Consecutivos Rendimentos Tributáveis por Centil {year}"}],
                        label="Todos os Centis",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, True]},
                              {"title": f"Razão entre Consecutivos Rendimentos Tributáveis por Centil {year} (Excluindo Centil 7 e 99.99)"}],
                        label="Excluindo Centil 7 e 99.99",
                        method="update"
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.1,
                yanchor="top"
            )
        ]
    )
    
    fig.show()

#%%
def plot_razao_rendimentos_multiple_years(df_orig):
    # Get unique years
    years = sorted(df_orig['Ano-calendário'].unique())
    
    # Create the plot
    fig = go.Figure()
    
    def get_color_for_year(year):
        # Define start and end colors (RGB)
        start_color = (33, 102, 172)  # Blue
        end_color = (127, 188, 65)    # Green
        
        # Calculate interpolation factor (0 to 1)
        min_year = min(years)
        max_year = max(years)
        factor = (year - min_year) / (max_year - min_year)
        
        # Interpolate each RGB component
        r = int(start_color[0] + (end_color[0] - start_color[0]) * factor)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * factor)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * factor)
        
        return f'rgb({r}, {g}, {b})'
    
    # Add traces for each year
    for year in years:
        # Filter data for this year
        df_year = df_orig[df_orig['Ano-calendário'] == year].copy()
        first_centils = [i for i in range(1,15)]
        df_year = df_year[~df_year['Centil'].isin( first_centils + [100, 10010, 1001010])]
        df_year['x_position'] = df_year['Centil'].apply(map_x_position)
        
        # Calculate ratio
        df_year['Razao_Rendimentos'] = ((df_year['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'] / df_year['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'].shift(1)) - 1) * 100
        df_year['Razao_Rendimentos'] = df_year['Razao_Rendimentos'].fillna(0)
        
        # Get color for this year
        year_color = get_color_for_year(year)
        
        # Add trace
        fig.add_trace(go.Scatter(
            x=df_year['x_position'],
            y=df_year['Razao_Rendimentos'],
            mode='lines+markers',
            line=dict(color=year_color, width=2),
            marker=dict(size=6),
            hovertemplate='Ano: ' + str(year) + '<br>Centil: %{x}<br>Razão: %{y:.2f}<extra></extra>',
            name=str(year),
            visible=True if year == 2020 else False
        ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Razão entre Consecutivos Rendimentos Tributáveis por Centil (2006-2020)',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 14}
        },
        xaxis_title='Centil',
        yaxis_title='Razão entre Consecutivos Rendimentos',
        template='plotly_white',
        width=1200,
        height=600,
        showlegend=True
    )
    
    # Create buttons for each year
    buttons = []
    for year in years:
        # Create visibility list for this button
        visibility = [True if y == year else False for y in years]
        
        # Create color list for this button
        colors = [get_color_for_year(y) if y == year else 'rgb(200, 200, 200)' for y in years]
        
        # Create button
        buttons.append(
            dict(
                args=[{"visible": visibility},
                      {"title": f'Razão entre Consecutivos Rendimentos Tributáveis por Centil ({year})'}],
                label=str(year),
                method="update"
            )
        )
    
    # Add buttons to layout
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                buttons=buttons,
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.1,
                yanchor="top"
            )
        ]
    )
    
    fig.show()

#%%
def plot_renda_custom_plotly(df):
    # Prepare data for each range
    df_graphed_99 = prepare_data_for_plotting(df, 99)
    df_graphed_100101 = prepare_data_for_plotting(df, 100101)
    df_graphed_100107 = prepare_data_for_plotting(df, 100107)
    df_graphed_100109 = prepare_data_for_plotting(df, 100109)
    df_graphed_all = prepare_data_for_plotting(df, 1001111)

    # Get maximum values for each range to use in annotations
    max_99 = df_graphed_99['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'].max()
    max_100101 = df_graphed_100101['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'].max()
    max_100107 = df_graphed_100107['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'].max()
    max_100109 = df_graphed_100109['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'].max()

    # Get x positions for the maximum values
    x_99 = df_graphed_99[df_graphed_99['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'] == max_99]['x_position'].iloc[0]
    x_100101 = df_graphed_100101[df_graphed_100101['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'] == max_100101]['x_position'].iloc[0]
    x_100107 = df_graphed_100107[df_graphed_100107['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'] == max_100107]['x_position'].iloc[0]
    x_100109 = df_graphed_100109[df_graphed_100109['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'] == max_100109]['x_position'].iloc[0]

    # Create the plot
    fig = go.Figure()

    # Add line traces
    fig.add_trace(go.Scatter(
        x=df_graphed_99['x_position'],
        y=df_graphed_99['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'],
        name='Até Centil 99',
        visible=True,
        mode='lines+markers',
        line=dict(color='rgb(33, 102, 172)', width=2),
        marker=dict(size=6),
        hovertemplate='Centil: %{x}<br>Rendimentos: %{y:.2f} R$ milhões<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df_graphed_100101['x_position'],
        y=df_graphed_100101['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'],
        name='Até 99.90% (Linha)',
        visible=False,
        mode='lines+markers',
        line=dict(color='rgb(33, 102, 172)', width=2),
        marker=dict(size=6),
        hovertemplate='Centil: %{x}<br>Rendimentos: %{y:.2f} R$ milhões<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df_graphed_100107['x_position'],
        y=df_graphed_100107['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'],
        name='Até 99.97% (Linha)',
        visible=False,
        mode='lines+markers',
        line=dict(color='rgb(33, 102, 172)', width=2),
        marker=dict(size=6),
        hovertemplate='Centil: %{x}<br>Rendimentos: %{y:.2f} R$ milhões<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df_graphed_100109['x_position'],
        y=df_graphed_100109['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'],
        name='Até 99.99% (Linha)',
        visible=False,
        mode='lines+markers',
        line=dict(color='rgb(33, 102, 172)', width=2),
        marker=dict(size=6),
        hovertemplate='Centil: %{x}<br>Rendimentos: %{y:.2f} R$ milhões<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df_graphed_all['x_position'],
        y=df_graphed_all['Rendimentos Tributaveis - Limite Superior da RTB do Centil [R$ milhões]'],
        name='Todos os Centis (Linha)',
        visible=False,
        mode='lines+markers',
        line=dict(color='rgb(33, 102, 172)', width=2),
        marker=dict(
            size=6
        ),
        hovertemplate='Centil: %{x}<br>Rendimentos: %{y:.2f} R$ milhões<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title={
            'text': 'Rendimentos Tributáveis por Centil 2020',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 14}
        },
        xaxis_title='Centil',
        yaxis_title='Rendimentos Tributáveis - Limite Superior',
        template='plotly_white',
        width=1200,
        height=600,
        showlegend=False,
        barmode='overlay'
    )

    # Create annotations for each range
    annotations_100101 = [
        dict(
            x=x_99,
            y=max_99,
            text=f"Centil 99:<br>{max_99:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor="red",
            ax=-60,
            ay=-60,
            standoff=10  # Add some spacing between arrow and point
        )
    ]

    annotations_100107 = annotations_100101 + [
        dict(
            x=x_100101,
            y=max_100101,
            text=f"Centil 99.90:<br>{max_100101:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor="red",
            ax=-60,
            ay=-60,
            standoff=10
        )
    ]

    annotations_100109 = annotations_100107 + [
        dict(
            x=x_100107,
            y=max_100107,
            text=f"Centil 99.97:<br>{max_100107:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor="red",
            ax=-60,
            ay=-60,
            standoff=10
        )
    ]

    annotations_all = [
        dict(
            x=x_100109,
            y=max_100109,
            text=f"Centil 99.99:<br>{max_100109:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor="red",
            ax=-60,
            ay=-60,
            standoff=10
        )
    ]

    # Add buttons for different centil ranges with annotations
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                buttons=list([
                    dict(
                        args=[{"visible": [True, False, False, False, False]},
                              {"annotations": []}],
                        label="Até Centil 99",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, True, False, False, False]},
                              {"annotations": annotations_100101}],
                        label="Até 99.90%",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, False, True, False, False]},
                              {"annotations": annotations_100107}],
                        label="Até 99.97%",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, False, False, True, False]},
                              {"annotations": annotations_100109}],
                        label="Até 99.99%",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, False, False, False, True]},
                              {"annotations": annotations_all}],
                        label="Todos os Centis",
                        method="update"
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.1,
                yanchor="top"
            )
        ]
    )

    fig.show()


# In[7]:

# ## Análises
# 
# ### Qual a parcela da população presente nos dados da Receita?
# 
# Segundo o Censo 2022 do IBGE (Censo mais perto do ano de 2020, ano que consideramos os dados da Receita), a população brasileira era de 203.080.756 pessoas.
# 
# O número total de contribuintes nestes dados é de 31.634.843 pessoas - cerca de 16% da população.

# In[8]:
POPULACAO_2022 = 203_080_756
df2020 = df_orig[df_orig["Ano-calendário"] == 2020]
total_contributors = df2020['Quantidade de Contribuintes'].sum()
print(f"Total de Contribuintes: {total_contributors:,.0f}".replace(',', '.'))
print(f"Percentual de contribuintes: {total_contributors*100 / POPULACAO_2022:.2f}%")


# ## Distribuição de Renda do Brasil em 2020

# Estes são os dados da distribuição de renda do Brasil em 2020, do 1º ao 99º centil.
# 
# Pegue a população brasileira (que pagou imposto de renda) e divida em 100 partes iguais.
# 
# Isto é um centil.
# 
# O primeiro centil são as 316.349 pessoas de menor renda.
# 
# O último centil são as 316.349 pessoas de maior renda.
# 
# A Renda Tributável Bruta começa a aparecer no 7º centil - abaixo disso as pessoas estão isentas da tributação.
# 
# A pessoa com maior renda do 7º centil possui uma renda tributável bruta de 100 reais - ou seja, pagam imposto em cima de 100 reais.
# 
# Abaixo estão as curvas de distribuição de renda.
# 
# Para ajudar na visualização, dividi em 5 gráficos diferentes.
# 
# Cada gráfico possui a curva até uma determinada parcela da população: 99%, 99.90%, 99.97%, 99.99% e 100%.
# 
# Repare as mudanças do eixo Y.
# 
# Eis os gráficos.

# In[9]:

plot_renda_custom_plotly(df_orig)

#%%
plot_razao_rendimentos(df_orig, 2020)

#%%
# Plot multiple years
plot_razao_rendimentos_multiple_years(df_orig)


# %%
