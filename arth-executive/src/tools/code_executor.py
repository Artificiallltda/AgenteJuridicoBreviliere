from langchain_core.tools import tool
import subprocess
import os
import uuid
from typing import Dict, Any

@tool
def execute_python_code(code: str) -> str:
    """
    Executa c\'F3digo Python em um subprocesso e retorna o resultado (stdout/stderr).
    Extremamente \'FAtil para o Arth realizar c\'E1lculos complexos, processar dados,
    gerar gr\'E1ficos ou scripts utilit\'E1rios.
    Voc\'EA (a IA) deve fornecer o c\'F3digo Python completo e v\'E1lido.
    Lembre-se de usar print() no c\'F3digo para que as informa\'E7\'F5es sejam retornadas no stdout.
    """
    try:
        # Cria um diret\'F3rio tempor\'E1rio para o script
        temp_dir = os.path.join(os.getcwd(), "data", "temp_scripts")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Gera um nome de arquivo \'FAnico
        filename = f"script_{uuid.uuid4().hex[:8]}.py"
        filepath = os.path.join(temp_dir, filename)
        
        # Escreve o c\'F3digo no arquivo
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
            
        # Executa o script
        result = subprocess.run(
            ["python", filepath],
            capture_output=True,
            text=True,
            timeout=30 # Limite de 30 segundos
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\nErros/Avisos:\n{result.stderr}"
            
        return output if output else "Script executado com sucesso (sem sa\'EDda no terminal)."
        
    except subprocess.TimeoutExpired:
        return "Erro: A execu\'E7\'E3o do c\'F3digo excedeu o tempo limite de 30 segundos."
    except Exception as e:
        return f"Erro ao executar o c\'F3digo: {str(e)}"
