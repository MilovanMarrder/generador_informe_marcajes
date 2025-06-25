from utils.data import etl_df
from reportgen.generador import generar_informe


df = etl_df('marcaje.xls')
print(df.columns)
generar_informe(df)



