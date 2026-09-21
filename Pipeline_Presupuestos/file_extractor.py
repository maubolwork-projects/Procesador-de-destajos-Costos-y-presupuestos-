#file_extractor.py

#====================================
# 1. Librerías y Variables
#====================================

import openpyxl
import pandas as pd

interest_cells = {
    "No. DE OBRA" : "C12",
    "INICIO" : "J12",
    "TERMINO" : "J13",
    "FECHA" : "J14",
    "RESIDENTE DE OBRA" : "C13",
    "OBRA" : "C8",
    "TRABAJOS A REALIZAR" : "C9",
    "SUB-CONTRATISTA" : "E10",
    "SUBCONTRATO Y/O DESTAJO" : "E14"
}

TABLE_HEADERS = ["ID", "CLAVE DE PPTO", "CONCEPTO", "UNIDAD", "CANTIDAD", "P. UNITARIO", "P.U. AUTORIZADO"]
TABLE_START = 18
TABLE_ROWS = 19
COLUMNS_DROP = [3, 4, 5, 10]

#====================================
# 2. Funciones Privadas (Uso Interno)
#====================================

def _extract_header_data(path):
    #Esta función extrae los datos mas relevantes de la caratula del formato presupuesto destajistas
    #Devuelve un diccionario que relaciona la etiqueta del dato con el mismo
    header_data = {}
    wb = openpyxl.load_workbook(path)
    sheet = wb.active
    for column, cell in interest_cells.items():
        header_data[column] = sheet[cell].value

    wb.close()
    return header_data

def _get_source_excel(path, sheet_name):
    #Esta función toma una ruta de un archivo excel y devuelve un dataframe 
    df = pd.read_excel(path, sheet_name=sheet_name, header=None, dtype_backend='numpy_nullable')

    return df

def _extract_table_data(df):
    #Esta función extrae información de la parte tabular del formato de registro, contempla 19 filas fijas
    #elimina las columnas en blanco creadas por las celdas combinadas
    # 1. Extraemos las 19 filas 
    posicion_inicial = df.index.get_loc(TABLE_START)
    resultado = df.iloc[posicion_inicial : posicion_inicial + TABLE_ROWS].copy()

    # 2. Eliminamos las columnas en las posiciones 3, 4 y 5
    resultado = resultado.drop(resultado.columns[COLUMNS_DROP], axis=1)
    resultado = resultado.reset_index(drop=True)
    resultado = resultado.dropna(how='all')
    resultado.columns=TABLE_HEADERS

    return resultado

#====================================
# 3. Función Pública (Interfaz)
#====================================

def extracted_data(path):
    #Esta es la función principal ejecuta las funciones que extraen información del header y de la tabla
    df = _get_source_excel(path, "NOMBRE DE LA OBRA") #Definir nombre de la pestaña de interes y fijarla

    header_data = _extract_header_data(path)
    table_data = _extract_table_data(df)
    return header_data, table_data

__all__ = ["extracted_data"]