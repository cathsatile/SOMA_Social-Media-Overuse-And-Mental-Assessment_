import os
import pandas as pd
import plotly.express as px
from django.shortcuts import render
from django.conf import settings

def dashboard_index(request):
    # 1. Captura qual eixo o usuário quer ver (Padrão é '1')
    selected_axis = request.GET.get('eixo', '0')
    
    # Dicionário de contexto inicial (Títulos e descrições dinâmicos)
    context = {
        'selected_axis': selected_axis,
        'kpi_time': '-',
        'kpi_risk': '-',
        'graph_pie': None,
        'graph_box': None,
        'graph_extra': None,
        # Títulos Padrão (serão sobrescritos dentro dos IFs)
        'section_title': 'Selecione um Eixo',
        'section_desc': 'Navegue pelo menu inferior para ver as análises.',
        'chart_section_title': 'Visualizações'
    }

    # =========================================================
    # EIXO 0: Introdução e Visão Geral
    # =========================================================
    if selected_axis == '0':
        context['show_intro'] = True # Flag para mudar o layout no HTML
        # Não calculamos KPIs nem gráficos aqui, apenas texto explicativo

    # =========================================================
    # LÓGICA DO EIXO 1: Fundamentação e Prevalência
    # =========================================================
    if selected_axis == '1':
        context['section_title'] = 'Análise de Prevalência (Eixo 1)'
        context['section_desc'] = 'Comparativo demográfico e estrutural do vício digital.'
        context['chart_section_title'] = 'Visão Geral da População'

        # --- CARREGAMENTO DATASET 1 ---
        csv_path = os.path.join(settings.BASE_DIR, 'data', 'dataset_1.csv')
        
        try:
            df = pd.read_csv(csv_path)
            # Limpeza
            df['Internet_Addiction_Level'] = df['Internet_Addiction_Level'].astype(str).str.strip()
            
            # --- KPIs ---
            avg_hours = df['hours_per_day'].mean()
            context['kpi_time'] = f"{avg_hours:.1f}h"
            context['kpi_label_1'] = 'Tempo Médio Diário'
            context['kpi_sub_1'] = 'Média geral dos participantes'

            total_users = len(df)
            addicted_users = len(df[df['Internet_Addiction_Level'] == 'Addicted'])
            percent_addicted = (addicted_users / total_users) * 100
            context['kpi_risk'] = f"{percent_addicted:.1f}%"
            context['kpi_label_2'] = 'Nível "Viciado"'
            context['kpi_sub_2'] = 'Participantes em alto risco'

            # --- GRÁFICO 1: Pizza (Distribuição) ---
            df_counts = df['Internet_Addiction_Level'].value_counts().reset_index()
            df_counts.columns = ['Nível', 'Quantidade']
            
            fig_pie = px.pie(
                df_counts, values='Quantidade', names='Nível',
                title='Distribuição dos Níveis de Vício',
                color='Nível',
                color_discrete_map={'Moderate': '#4A90E2', 'Problematics': '#9B59B6', 'Addicted': '#FF4B91'},
                hole=0.5
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A',
                height=380,
                legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            context['graph_pie'] = fig_pie.to_html(full_html=False, include_plotlyjs='cdn', config={'responsive': True})

            # --- GRÁFICO 2: Box Plot (Tempo de Uso) ---
            df_filtered = df[df['Internet_Addiction_Level'].isin(['Moderate', 'Addicted', 'Problematics'])]
            fig_box = px.box(
                df_filtered, x='Internet_Addiction_Level', y='hours_per_day',
                color='Internet_Addiction_Level',
                title='Impacto no Tempo de Uso',
                color_discrete_map={'Moderate': '#4A90E2', 'Addicted': '#FF4B91', 'Problematics': '#9B59B6'}
            )
            fig_box.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A',
                showlegend=False, height=380,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            context['graph_box'] = fig_box.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

            # --- GRÁFICO 3: Prevalência por Gênero (Barras Agrupadas) ---
            # Definindo categorias de risco conforme PDF (Addicted+Problematics = Alto Risco)
            def classificar_risco(nivel):
                if nivel in ['Addicted', 'Problematics']:
                    return 'Alto Risco'
                return 'Baixo Risco'
            
            df['Risk_Category'] = df['Internet_Addiction_Level'].apply(classificar_risco)
            
            # Agrupando os dados
            df_gender = df.groupby(['Gender', 'Risk_Category']).size().reset_index(name='Contagem')
            
            fig_gender = px.bar(
                df_gender, x='Gender', y='Contagem', color='Risk_Category',
                barmode='group',
                title='Prevalência de Risco por Gênero',
                color_discrete_map={'Alto Risco': '#FF4B91', 'Baixo Risco': '#4A90E2'}
            )
            fig_gender.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A',
                height=380,
                legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            context['graph_gender'] = fig_gender.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

        except FileNotFoundError:
            context['error'] = 'Dataset 1 não encontrado.'

        # --- CARREGAMENTO DATASET 3 (Para Nível Acadêmico) ---
        csv_path_3 = os.path.join(settings.BASE_DIR, 'data', 'dataset_3.csv')
        
        try:
            df3 = pd.read_csv(csv_path_3)
            
            # Definindo Alto Risco: Score > 7 (Conforme PDF)
            df3['High_Risk'] = df3['Addicted_Score'] > 7
            
            # Calculando % de alunos em risco por nível
            df_academic = df3.groupby('Academic_Level')['High_Risk'].mean().reset_index()
            df_academic['Percentage'] = df_academic['High_Risk'] * 100 # Convertendo para %
            
            fig_academic = px.bar(
                df_academic, x='Academic_Level', y='Percentage',
                title='% Alto Risco por Nível Acadêmico',
                text_auto='.1f', # Mostra o número na barra
                color='Academic_Level',
                color_discrete_sequence=['#4A90E2', '#9B59B6', '#FF4B91']
            )
            fig_academic.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A',
                height=380, showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                yaxis_title='% de Alunos em Alto Risco'
            )
            context['graph_academic'] = fig_academic.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})
            
        except FileNotFoundError:
            # Se não achar o arquivo, apenas não exibe o gráfico (não quebra a página)
            print("Dataset 3 não encontrado")

    # =========================================================
    # LÓGICA DO EIXO 2 (PREPARAÇÃO)
    # =========================================================
    elif selected_axis == '2':
        context['section_title'] = 'Impacto na Saúde Mental (Eixo 2)'
        context['section_desc'] = 'Correlações entre vício digital, ansiedade, depressão e autoestima.'
        context['chart_section_title'] = 'Matriz de Risco e Fatores de Proteção'

        csv_path = os.path.join(settings.BASE_DIR, 'data', 'dataset_1.csv')
        
        try:
            df = pd.read_csv(csv_path)

            # 1. Selecionar apenas as colunas numéricas de interesse para a correlação
            cols_interesse = [
                'Internet_Addiction_Score', 
                'Depression_Score', 
                'Anxiety_Score', 
                'Stress_Score', 
                'Self-Esteem_Score'
            ]
            
            # Matriz de Correlação (Cálculo matemático)
            corr_matrix = df[cols_interesse].corr()

            # --- KPIs Específicos do Eixo 2 ---
            # Pegamos a correlação exata entre Vício e Depressão
            corr_depressao = corr_matrix.loc['Internet_Addiction_Score', 'Depression_Score']
            context['kpi_time'] = f"r = {corr_depressao:.2f}" # Reusando o card da esquerda
            
            # Pegamos a correlação entre Vício e Autoestima (Proteção)
            corr_autoestima = corr_matrix.loc['Internet_Addiction_Score', 'Self-Esteem_Score']
            context['kpi_risk'] = f"r = {corr_autoestima:.2f}" # Reusando o card do meio

            # Atualizando os textos dos Cards de KPI para este contexto
            context['kpi_label_1'] = 'Correlação: Depressão' # Vamos criar isso no HTML jajá
            context['kpi_sub_1'] = 'Forte associação positiva'
            
            context['kpi_label_2'] = 'Correlação: Autoestima'
            context['kpi_sub_2'] = 'Fator de proteção (Negativo)'


            # --- GRÁFICO 1 (ESQUERDA): Heatmap de Correlações ---
            # Renomeando colunas para ficar bonito no gráfico
            labels_map = {
                'Internet_Addiction_Score': 'Vício',
                'Depression_Score': 'Depressão',
                'Anxiety_Score': 'Ansiedade',
                'Stress_Score': 'Estresse',
                'Self-Esteem_Score': 'Autoestima'
            }
            
            fig_heatmap = px.imshow(
                corr_matrix,
                text_auto='.2f', # Mostra os números dentro dos quadrados
                aspect="auto",
                color_continuous_scale='RdBu_r', # Vermelho = Positivo, Azul = Negativo
                title='Matriz de Correlação: Vício vs. Saúde Mental',
                x=[labels_map.get(c, c) for c in corr_matrix.columns],
                y=[labels_map.get(c, c) for c in corr_matrix.columns]
            )
            
            fig_heatmap.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#1C2E4A',
                height=380,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            # Jogamos o Heatmap na variável "graph_pie" (que é o slot da esquerda)
            context['graph_pie'] = fig_heatmap.to_html(full_html=False, include_plotlyjs='cdn', config={'responsive': True})


            # --- GRÁFICO 2 (DIREITA): Scatter Plot (Vício vs Autoestima) ---
            # Mostra a linha de tendência negativa
            fig_scatter = px.scatter(
                df, 
                x='Self-Esteem_Score', 
                y='Internet_Addiction_Score',
                trendline="ols", # Linha de regressão (Requer statsmodels)
                trendline_color_override="red",
                title='Autoestima como Fator de Proteção',
                labels={'Self-Esteem_Score': 'Nível de Autoestima', 'Internet_Addiction_Score': 'Score de Vício'},
                opacity=0.6 # Bolinhas levemente transparentes para ver a aglomeração
            )

            fig_scatter.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#1C2E4A',
                height=380,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            # Jogamos o Scatter na variável "graph_box" (que é o slot da direita)
            context['graph_box'] = fig_scatter.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

        except FileNotFoundError:
            context['error'] = 'Dataset 1 não encontrado.'
        except Exception as e:
            print(f"Erro no Eixo 2: {e}") # Ajuda a debugar no terminal
            context['error'] = 'Erro ao processar dados do Eixo 2.'
        
    elif selected_axis == '3':
        context['section_title'] = 'Plataformas e Consequências (Eixo 3)'
        context['section_desc'] = 'Análise detalhada por plataforma, impacto no sono e conflitos sociais.'
        context['chart_section_title'] = 'Métricas de Uso e Sintomas'

        # Caminhos dos arquivos
        path_d2 = os.path.join(settings.BASE_DIR, 'data', 'dataset_2.csv')
        path_d3 = os.path.join(settings.BASE_DIR, 'data', 'dataset_3.csv')

        try:
            # Carregando Datasets
            df2 = pd.read_csv(path_d2)
            df3 = pd.read_csv(path_d3)
            
            # =========================================================
            # CÁLCULO DE KPIS (EIXO 3)
            # =========================================================
            
            # KPI 1: Plataforma de Maior Risco (Dataset 3)
            # Agrupa por plataforma e pega a que tem a maior MEDIANA de Score de Vício
            # (Conforme PDF: TikTok deve ganhar com 8.0)
            risk_ranking = df3.groupby('Most_Used_Platform')['Addicted_Score'].median().sort_values(ascending=False)
            top_platform = risk_ranking.index[0]  
            top_score = risk_ranking.iloc[0]      
            
            context['kpi_label_1'] = 'Plataforma de Risco'
            context['kpi_time'] = f"{top_platform}"
            context['kpi_sub_1'] = f"Maior Mediana de Vício ({top_score:.1f})"

            # KPI 2: Correlação Uso vs. Conflitos (Dataset 3)
            # (Conforme PDF: Deve dar aprox 0.80)
            corr_conflicts = df3['Avg_Daily_Usage_Hours'].corr(df3['Conflicts_Over_Social_Media'])
            
            context['kpi_label_2'] = 'Conflitos Sociais'
            context['kpi_risk'] = f"r = {corr_conflicts:.2f}"
            context['kpi_sub_2'] = 'Correlação com tempo de uso'
            
            # ---------------------------------------------------------
            # GRÁFICO 1: Barras - Cognitivo vs Comportamental (PDF 1)
            # ---------------------------------------------------------
            # Objetivo: Comparar correlação de 'think_time' e 'actual_time' com 'anxious_stressed'
            plataformas = ['instagram', 'whatsapp', 'twitter', 'facebook', 'youtube', 'linkedin']
            dados_corr = []

            for p in plataformas:
                # Correlação Cognitiva
                col_think = f'think_time_{p}'
                if col_think in df2.columns:
                    r_think = df2[col_think].corr(df2['anxious_stressed'])
                    dados_corr.append({'Plataforma': p.capitalize(), 'Tipo': 'Cognitivo (Desejo)', 'Correlação': r_think})
                
                # Correlação Comportamental
                col_actual = f'actual_time_{p}'
                if col_actual in df2.columns:
                    r_actual = df2[col_actual].corr(df2['anxious_stressed'])
                    dados_corr.append({'Plataforma': p.capitalize(), 'Tipo': 'Real (Uso)', 'Correlação': r_actual})

            df_corr_bar = pd.DataFrame(dados_corr)
            
            fig_bar_corr = px.bar(
                df_corr_bar, x='Plataforma', y='Correlação', color='Tipo',
                barmode='group',
                title='Correlação: Padrões de Uso vs. Ansiedade',
                color_discrete_map={'Cognitivo (Desejo)': '#9B59B6', 'Real (Uso)': '#4A90E2'}
            )
            fig_bar_corr.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A', height=380, margin=dict(t=50, b=20, l=20, r=20), legend=dict(orientation="h", y=-0.2))
            context['graph_platforms_anxiety'] = fig_bar_corr.to_html(full_html=False, include_plotlyjs='cdn', config={'responsive': True})

            # ---------------------------------------------------------
            # GRÁFICO 2: Heatmap - Sintomas Físicos (PDF 3)
            # ---------------------------------------------------------
            sintomas = ['headaches_eyestrain', 'smartphone_discomfort', 'nervous_anxious']
            # Cria matriz vazia
            heatmap_data = []
            
            for s in sintomas:
                row = []
                for p in plataformas:
                    col_actual = f'actual_time_{p}'
                    if col_actual in df2.columns:
                        row.append(df2[col_actual].corr(df2[s]))
                    else:
                        row.append(0)
                heatmap_data.append(row)

            fig_heat = px.imshow(
                heatmap_data,
                x=[p.capitalize() for p in plataformas],
                y=['Dor de Cabeça', 'Desc. Smartphone', 'Nervosismo'],
                title='Impacto Físico por Plataforma',
                color_continuous_scale='RdBu_r', # Vermelho = Positivo (Pior sintoma), Azul = Negativo
                aspect="auto"
            )
            fig_heat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A', height=380, margin=dict(t=50, b=20, l=20, r=20))
            context['graph_heatmap_symptoms'] = fig_heat.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

            # ---------------------------------------------------------
            # GRÁFICO 3: Boxplot - Comparação Social (PDF 2)
            # ---------------------------------------------------------
            fig_social = px.box(
                df2, x='compare_with_others', y='mood_disorder',
                title='Comparação Social vs. Distúrbio de Humor',
                color='compare_with_others',
                labels={'compare_with_others': 'Nível de Comparação', 'mood_disorder': 'Frequência de Distúrbio'},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_social.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A', showlegend=False, height=380, margin=dict(t=50, b=20, l=20, r=20))
            context['graph_social_mood'] = fig_social.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

            # ---------------------------------------------------------
            # GRÁFICO 4: Scatter - Conflitos Sociais (Dataset 3 - PDF 6)
            # ---------------------------------------------------------
            fig_conflicts = px.scatter(
                df3, x='Avg_Daily_Usage_Hours', y='Conflicts_Over_Social_Media',
                trendline="ols", trendline_color_override="red",
                title='Uso Diário vs. Conflitos Sociais',
                opacity=0.6,
                labels={'Avg_Daily_Usage_Hours': 'Horas de Uso', 'Conflicts_Over_Social_Media': 'Nível de Conflito'}
            )
            fig_conflicts.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A', height=380, margin=dict(t=50, b=20, l=20, r=20))
            context['graph_conflicts'] = fig_conflicts.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

            # ---------------------------------------------------------
            # GRÁFICO 5: Boxplot - Sono e Uso Antes de Dormir (PDF 4)
            # ---------------------------------------------------------
            # Convertendo binário/escala para categoria legível se necessário
            fig_sleep_bed = px.box(
                df2, x='social_media_before_bed', y='sleep_quality_month',
                title='Uso Antes de Dormir vs. Qualidade do Sono',
                color='social_media_before_bed',
                color_discrete_map={0: '#4A90E2', 1: '#FF4B91'} # Azul (Baixo), Rosa (Alto)
            )
            fig_sleep_bed.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A', showlegend=False, height=380, margin=dict(t=50, b=20, l=20, r=20))
            context['graph_sleep_social'] = fig_sleep_bed.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

            # ---------------------------------------------------------
            # GRÁFICO 6: Scatter - Vício vs Horas de Sono (Dataset 3 - PDF 5)
            # ---------------------------------------------------------
            fig_addiction_sleep = px.scatter(
                df3, x='Addicted_Score', y='Sleep_Hours_Per_Night',
                trendline="ols", trendline_color_override="red",
                title='Score de Vício vs. Horas de Sono',
                labels={'Addicted_Score': 'Pontuação de Vício', 'Sleep_Hours_Per_Night': 'Horas de Sono'},
                opacity=0.6
            )
            fig_addiction_sleep.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A', height=380, margin=dict(t=50, b=20, l=20, r=20))
            context['graph_sleep_addiction'] = fig_addiction_sleep.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

        except FileNotFoundError:
            context['error'] = 'Datasets 2 ou 3 não encontrados na pasta data/.'
        except Exception as e:
            print(e)
            context['error'] = f'Erro no processamento do Eixo 3: {str(e)}'

    # =========================================================
    # LÓGICA DO EIXO 4: Dieta Digital (Dataset 4)
    # =========================================================
    elif selected_axis == '4':
        context['section_title'] = 'Dieta Digital e Bem-Estar (Eixo 4)'
        context['section_desc'] = 'Análise do volume de uso versus indicadores de qualidade de vida.'
        context['chart_section_title'] = 'Volume vs. Impacto (A Tese da "Qualidade")'

        csv_path = os.path.join(settings.BASE_DIR, 'data', 'dataset_4.csv')
        
        try:
            df4 = pd.read_csv(csv_path)

            # --- KPIS: A Revelação dos Dados ---
            # KPI 1: Volume Médio (O comportamento)
            avg_social = df4['social_media_hours'].mean()
            context['kpi_label_1'] = 'Média de Redes Sociais'
            context['kpi_time'] = f"{avg_social:.1f}h / dia"
            context['kpi_sub_1'] = 'Volume de uso diário'

            # KPI 2: A Correlação Fraca (O Insight)
            # Mostramos a correlação Social Media vs Saúde Mental para provar o ponto do PDF
            corr_mental = df4['social_media_hours'].corr(df4['mental_health_score'])
            context['kpi_label_2'] = 'Correlação: Bem-Estar'
            context['kpi_risk'] = f"r = {corr_mental:.2f}"
            context['kpi_sub_2'] = 'Associação fraca/insignificante'
            
            # --- CONFIGURAÇÃO PADRÃO PARA OS GRÁFICOS ---
            # Função auxiliar para não repetir código de layout
            def update_scatter_layout(fig, title):
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A',
                    height=380, margin=dict(l=20, r=20, t=40, b=20),
                    title=title
                )
                return fig

            # GRÁFICO 1: Horas vs. Humor (PDF 1)
            # Mostra a linha plana (sem correlação)
            fig_mood = px.scatter(
                df4, x='social_media_hours', y='mood_rating',
                trendline="ols", trendline_color_override="red",
                labels={'social_media_hours': 'Horas de Redes Sociais', 'mood_rating': 'Nota de Humor (1-10)'},
                opacity=0.6
            )
            update_scatter_layout(fig_mood, 'Impacto no Humor (Inexistente)')
            context['graph_pie'] = fig_mood.to_html(full_html=False, include_plotlyjs='cdn', config={'responsive': True})

            # GRÁFICO 2: Horas vs. Saúde Mental (PDF 2)
            fig_mental = px.scatter(
                df4, x='social_media_hours', y='mental_health_score',
                trendline="ols", trendline_color_override="red",
                labels={'social_media_hours': 'Horas de Redes Sociais', 'mental_health_score': 'Score Saúde Mental'},
                opacity=0.6
            )
            update_scatter_layout(fig_mental, 'Impacto na Saúde Mental Geral')
            context['graph_box'] = fig_mental.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

            # GRÁFICO 3: Horas vs. Duração do Sono (PDF 3)
            fig_sleep_dur = px.scatter(
                df4, x='social_media_hours', y='sleep_duration_hours',
                trendline="ols", trendline_color_override="red",
                labels={'social_media_hours': 'Horas de Redes Sociais', 'sleep_duration_hours': 'Horas de Sono'},
                opacity=0.6
            )
            update_scatter_layout(fig_sleep_dur, 'Impacto na Duração do Sono')
            context['graph_gender'] = fig_sleep_dur.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

            # GRÁFICO 4: Horas vs. Qualidade do Sono (PDF 4)
            fig_sleep_qual = px.scatter(
                df4, x='social_media_hours', y='sleep_quality',
                trendline="ols", trendline_color_override="red",
                labels={'social_media_hours': 'Horas de Redes Sociais', 'sleep_quality': 'Qualidade do Sono (1-10)'},
                opacity=0.6
            )
            update_scatter_layout(fig_sleep_qual, 'Impacto na Qualidade do Sono')
            context['graph_academic'] = fig_sleep_qual.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

        except FileNotFoundError:
            context['error'] = 'Dataset 4 não encontrado na pasta data/.'

    # =========================================================
    # LÓGICA DO EIXO 5: Predição e Ação (Datasets 1, 3 e 4)
    # =========================================================
    elif selected_axis == '5':
        context['section_title'] = 'Modelo Preditivo e Ação (Eixo 5)'
        context['section_desc'] = 'Identificação de grupos de risco e fatores de proteção (hábitos).'
        context['chart_section_title'] = 'Fatores de Intervenção'

        path_d1 = os.path.join(settings.BASE_DIR, 'data', 'dataset_1.csv')
        path_d3 = os.path.join(settings.BASE_DIR, 'data', 'dataset_3.csv')
        path_d4 = os.path.join(settings.BASE_DIR, 'data', 'dataset_4.csv')
        
        try:
            df1 = pd.read_csv(path_d1)
            df3 = pd.read_csv(path_d3)
            df4 = pd.read_csv(path_d4)

            # --- KPIS: Ação e Alvo ---
            
            # KPI 1: Melhor Fator de Mitigação
            habitos = ['physical_activity_hours_per_week', 'mindfulness_minutes_per_day', 'eats_healthy']
            melhor_habito = None
            menor_corr = 0 # Começa em 0 para buscar negativos
            
            for h in habitos:
                # Verifica se a coluna existe antes de calcular para evitar erros
                if h in df4.columns and 'weekly_depression_score' in df4.columns:
                    r = df4[h].corr(df4['weekly_depression_score'])
                    # Buscamos a correlação mais negativa (que reduz a depressão)
                    if r < menor_corr: 
                        menor_corr = r
                        melhor_habito = h
            
            # 🚨 CORREÇÃO DE SEGURANÇA AQUI 🚨
            context['kpi_label_1'] = 'Melhor Mitigador'
            
            if melhor_habito is None:
                # Fallback caso nenhuma correlação negativa seja encontrada
                context['kpi_time'] = "Em Análise"
                context['kpi_sub_1'] = "Nenhuma correlação negativa forte"
            else:
                # Lógica original (agora segura)
                if melhor_habito == 'eats_healthy':
                    nome_habito = "Alimentação"
                elif 'mindfulness' in melhor_habito:
                    nome_habito = "Mindfulness"
                else:
                    nome_habito = "Exercício"
                    
                context['kpi_time'] = nome_habito
                context['kpi_sub_1'] = f"Maior redução de sintomas (r={menor_corr:.2f})"

            # KPI 2: Grupo de Maior Risco (Baseado no Dataset 3 - PDF 5)
            # Qual nível acadêmico tem a maior mediana de vício?
            risco_acad = df3.groupby('Academic_Level')['Addicted_Score'].median().sort_values(ascending=False)
            top_group = risco_acad.index[0]
            score_group = risco_acad.iloc[0]

            context['kpi_label_2'] = 'Grupo de Risco'
            context['kpi_risk'] = top_group  # Ex: High School
            context['kpi_sub_2'] = f"Mediana de Vício: {score_group:.1f}"

            # ---------------------------------------------------------
            # GRÁFICO 1: Força dos Preditores (Barras - PDF 1)
            # ---------------------------------------------------------
            # Comparando correlações absolutas de hábitos vs sintomas
            preditores = ['social_media_hours', 'physical_activity_hours_per_week', 'mindfulness_minutes_per_day', 'eats_healthy']
            dados_pred = []
            
            labels_pred = {
                'social_media_hours': 'Uso Redes Sociais',
                'physical_activity_hours_per_week': 'Ativ. Física',
                'mindfulness_minutes_per_day': 'Mindfulness',
                'eats_healthy': 'Alimentação Saudável'
            }

            for p in preditores:
                r_anx = abs(df4[p].corr(df4['weekly_anxiety_score']))
                r_dep = abs(df4[p].corr(df4['weekly_depression_score']))
                dados_pred.append({'Fator': labels_pred[p], 'Sintoma': 'Ansiedade', 'Força (|r|)': r_anx})
                dados_pred.append({'Fator': labels_pred[p], 'Sintoma': 'Depressão', 'Força (|r|)': r_dep})
            
            fig_pred = px.bar(
                dados_pred, x='Fator', y='Força (|r|)', color='Sintoma',
                barmode='group',
                title='Força dos Preditores (Impacto Absoluto)',
                color_discrete_map={'Ansiedade': '#FF9F43', 'Depressão': '#5f27cd'}
            )
            fig_pred.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A', height=380, margin=dict(t=50, b=20, l=20, r=20), legend=dict(orientation="h", y=-0.2))
            context['graph_pie'] = fig_pred.to_html(full_html=False, include_plotlyjs='cdn', config={'responsive': True})

            # ---------------------------------------------------------
            # GRÁFICO 2: Hábitos e Mitigação (Barras - PDF 2)
            # ---------------------------------------------------------
            # Mostrando a direção real (positiva/negativa) para ver se ajuda ou atrapalha
            dados_mitig = []
            for p in ['physical_activity_hours_per_week', 'mindfulness_minutes_per_day', 'eats_healthy']:
                r_dep = df4[p].corr(df4['weekly_depression_score'])
                dados_mitig.append({'Hábito': labels_pred[p], 'Correlação': r_dep})
            
            fig_mitig = px.bar(
                dados_mitig, x='Hábito', y='Correlação',
                title='Potencial de Mitigação (Depressão)',
                text_auto='.3f',
                color='Correlação',
                color_continuous_scale='Tealgrn_r' # Verde para negativo (bom)
            )
            fig_mitig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A', height=380, margin=dict(t=50, b=20, l=20, r=20))
            context['graph_box'] = fig_mitig.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

            # ---------------------------------------------------------
            # GRÁFICO 3: Sono vs Mídia (Box Plot - PDF 3)
            # ---------------------------------------------------------
            # Usando Dataset 4 (que tem sleep_quality 1-10)
            fig_sleep = px.box(
                df4, x='sleep_quality', y='social_media_hours',
                title='Qualidade do Sono vs. Tempo de Tela',
                labels={'sleep_quality': 'Qualidade (1-10)', 'social_media_hours': 'Horas Redes Sociais'},
                color_discrete_sequence=['#4A90E2']
            )
            fig_sleep.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A', height=380, margin=dict(t=50, b=20, l=20, r=20))
            context['graph_gender'] = fig_sleep.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

            # ---------------------------------------------------------
            # GRÁFICO 4: Nível Acadêmico vs Vício (Box Plot - PDF 5)
            # ---------------------------------------------------------
            # Usando Dataset 3
            fig_acad_risk = px.box(
                df3, x='Academic_Level', y='Addicted_Score',
                title='Risco por Nível Acadêmico',
                color='Academic_Level',
                category_orders={'Academic_Level': ['High School', 'Undergraduate', 'Graduate']}, # Ordem lógica
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_acad_risk.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A', showlegend=False, height=380, margin=dict(t=50, b=20, l=20, r=20))
            context['graph_academic'] = fig_acad_risk.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})
            
            # ---------------------------------------------------------
            # GRÁFICO 5: Idade vs Vício (Scatter - PDF 4)
            # ---------------------------------------------------------
            # Usando Dataset 1
            # Como temos 5 gráficos, vamos colocá-lo numa variável extra
            fig_age = px.scatter(
                df1, x='Age', y='Internet_Addiction_Score',
                trendline="ols", trendline_color_override="red",
                title='Idade vs. Pontuação de Vício',
                opacity=0.5
            )
            fig_age.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#1C2E4A', height=380, margin=dict(t=50, b=20, l=20, r=20))
            context['graph_extra'] = fig_age.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True})

        except FileNotFoundError:
            context['error'] = 'Arquivos de dados necessários não encontrados.'

    return render(request, 'soma_app/dashboard.html', context)

def sobre_nos(request):
    return render(request, 'soma_app/sobre_nos.html')

def sobre_soma(request):
    return render(request, 'soma_app/sobre_soma.html')