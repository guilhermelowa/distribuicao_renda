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
# 
# ### Perguntas em aberto
# 
# - Qual a tributação que cada centil paga?
# - Como é a distribuição em outros países? É local ou sistemático essa diferença?
# 
# ## Código

# In[1]:


import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# In[2]:


df_orig = pd.read_csv("data/distribuicao-renda.csv", sep=";")
df_orig.head()


# In[3]:


df20 = df_orig[df_orig["Ano-calendário"] == 2020]
df20 = df20.drop(["Ano-calendário"], axis=1)
df20.head()


# In[4]:


df20br = df20[df20["Ente Federativo"] == "BRASIL"]
df20br = df20br.reset_index()
df20br = df20br.drop(["Ente Federativo" , "index"], axis=1)
df20br.index = df20br.index + 1
df20br.head()


# In[5]:


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

# Convert all columns in df20br
for column in df20br.columns:
    if df20br[column].dtype == "object":
        try:
            df20br[column] = df20br[column].apply(convert_brazilian_number)
        except Exception as e:
            print(f"Error converting column {column}: {e}")

# Verify the data types
df20br.dtypes


# In[13]:


# Helper functions

def create_one_indexed_df(_df):
    _df = _df.reset_index()
    _df = _df.drop(["index"], axis=1)
    _df.index = _df.index + 1
    return _df

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

    # Add position and width columns
    df_graphed['x_position'] = df_graphed['Centil'].apply(map_x_position)
    df_graphed['width'] = df_graphed['Centil'].apply(map_width)

    # Sort by x position
    return df_graphed.sort_values('x_position')


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
    annotations_99 = []  # Empty for first range

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

    annotations_100107 = [
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

    annotations_100109 = [
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
                              {"annotations": annotations_99}],
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


# Filter the DataFrame to remove rows with centil values 100 and 1001 to 10010
df_all_info = df20br[(df20br['Centil'] != 100) & (df20br['Centil'] != 10010)]
df_all_info = create_one_indexed_df(df_all_info)
df_all_info


# ## Análises
# 
# ### Qual a parcela da população presente nos dados da Receita?

# Resultado aqui
# 

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

# In[14]:


plot_renda_custom_plotly(df_all_info)

