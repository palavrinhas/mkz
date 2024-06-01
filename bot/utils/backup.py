from datetime import datetime
import pytz

def emissao_data():
    brt_timezone = pytz.timezone('America/Sao_Paulo')
    current_time_br = datetime.now(brt_timezone)
    formatted_datetime = current_time_br.strftime('%d/%m/%Y às %H:%M:%S')
    return formatted_datetime