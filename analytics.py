import pandas as pd


def summary_general(tabla: pd.DataFrame) -> pd.DataFrame:
    tabla['Tipo_dia'] = tabla['Fin_de_semana'].map({True: 'Fin de semana', False: 'Día de semana'})
    return tabla.groupby(['Mes','Tipo_dia']).agg(Cantidad_Dias=('Fecha','count'),
             Total_horas=('Jornada', lambda x: x.dt.total_seconds().sum()/3600)).reset_index()


def summary_employees(tabla: pd.DataFrame) -> pd.DataFrame:
    return tabla.groupby('Nombre').agg(Mediana_hrs_dia=('Jornada', lambda x: x.dt.total_seconds().median()/3600),
             Horas_totales=('Jornada', lambda x: x.dt.total_seconds().sum()/3600)).reset_index()

