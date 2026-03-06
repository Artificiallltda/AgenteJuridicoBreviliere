import os
import uuid
import pandas as pd
import matplotlib.pyplot as plt
from langchain_core.tools import tool
import io
import contextlib

@tool
def analyze_data_file(instruction: str, data_string: str) -> str:
    """
    Analisa dados como um Cientista de Dados e gera gráficos ou estatísticas.
    
    Use esta ferramenta quando o usuário enviar dados brutos ou perdir para 
    criar gráficos, calcular médias, comparar números, etc.
    
    IMPORTANTE: Como o ambiente de chat não permite o upload fácil de planilhas 
    direto pro agente, o 'data_string' deve ser uma representação em CSV ou 
    JSON dos dados que o usuário te passou, ou uma amostra dos dados se for 
    algo hipotético.
    
    A instrução deve conter um script Python seguro no formato de texto que
    será executado para processar a variável `df` (um DataFrame do Pandas gerado
    a partir do data_string).
    
    O script DEVE:
    1. Trabalhar com a variável preexistente chamada `df`.
    2. Usar o matplotlib para gerar um gráfico (se necessário) e salvá-lo 
       no caminho indicado pela variável global `output_path`.
    3. Imprimir dados úteis no console (usando print), pois a saída do console
       será devolvida para você usar na sua resposta final.
       
    Exemplo de instruction:
    df['Vendas'] = pd.to_numeric(df['Vendas'])
    resumo = df.describe()
    print("Resumo Estatístico:")
    print(resumo)
    plt.figure(figsize=(10,6))
    df.plot.bar(x='Mês', y='Vendas')
    plt.savefig(output_path)
    print(f"Gráfico salvo com sucesso.")
    """
    try:
        data_dir = os.path.join(os.getcwd(), "data", "outputs")
        os.makedirs(data_dir, exist_ok=True)
        
        filename = f"{uuid.uuid4().hex[:8]}_grafico_analise.png"
        filepath = os.path.join(data_dir, filename)
        
        # Converter string em DataFrame
        df = None
        try:
            df = pd.read_csv(io.StringIO(data_string))
        except Exception as e1:
            try:
                df = pd.read_json(io.StringIO(data_string))
            except Exception as e2:
                return f"Erro: O data_string fornecido não pôde ser lido como CSV nem JSON. (Erros: {e1}, {e2})"
            
        if df is None:
            return "Erro: DataFrame vazio."

        # Executar o código do usuário em um ambiente restrito
        # O script tem acesso ao DataFrame 'df', plt, pd e 'output_path'
        local_scope = {
            'df': df,
            'pd': pd,
            'plt': plt,
            'output_path': filepath
        }
        
        output_buffer = io.StringIO()
        with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
            try:
                exec(instruction, {}, local_scope)
            except Exception as script_error:
                print(f"Erro ao executar a instrução de análise: {str(script_error)}")
        
        console_output = output_buffer.getvalue()
        
        # Verificar se o script gerou uma imagem
        if os.path.exists(filepath):
            return (
                f"Análise concluída!\n\n"
                f"Saída do Console (Estatísticas):\n{console_output}\n\n"
                f"Um gráfico foi gerado.\n"
                f"Escreva sua resposta para o usuário com base nos dados acima e no FINAL cole EXATAMENTE esta tag: <SEND_FILE:{filename}>"
            )
        else:
            return (
                f"Análise concluída (Nenhum gráfico gerado).\n\n"
                f"Saída do Console:\n{console_output}\n\n"
                f"Escreva sua resposta para o usuário com base nesses dados."
            )
            
    except Exception as e:
        return f"Erro catastrófico na Análise de Dados: {str(e)}"
