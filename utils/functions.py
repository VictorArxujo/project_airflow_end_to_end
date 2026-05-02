from datetime import datetime, timedelta
import pandas as pd

def retorna_hora_atual_formatada():
    data_brasil=datetime.utcnow() - timedelta(hours=3)
    data_formatada = data_brasil.strftime("%Y-%m-%dT%H:%M:%SZ")
    return data_formatada

def retorna_data_hora_atual(horario_str):
    return datetime.strptime(horario_str, "%H:%M").time()


def transform_to_tags(df, sub_code):
    json_list = []
    # Selecionamos as colunas de dados (ignorando 'nome' e 'id' que compõem o prefixo)
    cols_dados = [col for col in df.columns if col not in ['nome', 'id']]
    
    for _, row in df.iterrows():
        nome_inversor = str(row['id_intelup'])
        for col in cols_dados:
            # Monta o tagCode: SMTR + ID + SUBCODE + NOME_DA_COLUNA
            tag_code = f"SMTR_{nome_inversor}_{sub_code}_{col}"
            valor = row[col]
            
            # Adiciona ao dicionário, tratando valores nulos se existirem
            json_list.append({
                'tagCode': tag_code,
                'value': valor if pd.notna(valor) else None
            })
    return json_list
