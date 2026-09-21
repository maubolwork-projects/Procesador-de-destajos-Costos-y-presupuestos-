# Procesador de Destajos

Aplicación desarrollada en Python para automatizar la extracción,
transformación y consolidación de información proveniente de formatos
Excel de destajos y presupuestos.

El programa identifica archivos Excel nuevos dentro de una carpeta de 
trabajo, extrae la información definida del formato, transforma los datos y
los incorpora a un archivo consolidado. Adicionalmente, mantiene un registro 
local de los archivos procesados mediante SQLite para evitar reprocesamientos.

El proyecto está diseñado actualmente para **un formato Excel específico y estable**.

---

# Objetivo

Automatizar el proceso manual de consolidación de información contenida en formatos
Excel utilizados para el registro de destajos y presupuestos.

El proceso permite:
- Detectar archivos de Excel dentro de una carpeta.
- Identificar archivos procesados
- Extraer información de encabezados y tablas.
- Estandarizar determinados tipos de datos.
- Generar automáticamente el importe de cada registro.
- Asignar IDs consecutivos.
- Consolidar los registros en un archivo de Excel.
- Mantener el historial de archivos procesados.
- Procesar archivos corregidos mediante una nueva versión del nombre.
- Ejecutar como aplicación mediante un archivo **.exe**

---

# Arquitectura

El proyecto está organizado en módulos según la responsabilidad de cada etapa:

``` text
pipeline_presupuestos.py
        |
        |__ file_manager.py
        |       |__ Descubrimiento y metadatos del archivo
        |
        |__ file_extractor.py
        |       |__ Extracción de encabezados y tablas
        |
        |__ table_constructor.py
        |        |__ Construcción, transformación y carga
        |
        |__ file_creator.py
        |       |__ Creación del archivo consolidado
        |
        |__ db_schema.py
              |__ Control de archivos procesados
```

---

# Flujo General

``` text
Archivos Excel de origen
          |
          ▼
   file_manager.py
          |
          ▼
Identificación del archivo
          |
          ▼
     ¿Ya existe?
      /      \
    Si        No
    |         |
    |         ▼
    | file_extractor.py
    |         |
    |         ▼
    | table_constructor.py
    |         |
    |         ▼
    | Caratula de pptos.xlsx
    |         |
    |         ▼
    | file_control.db
    |
    |_____ Omitir

```

---

# Módulos

`pipeline_presupuestos.py`

Es el **orquestador principal** del proceso.

Se encarga de coordinar las diferentes etapas y determinar qué archivos
deben procesarse.

También determina la carpeta de trabajo dependiendo de si el programa se 
ejecuta directamente desde Python o como `.exe`.

if getattr(sys, "frozen", False):

    ruta = Path(sys.executable).resolve().parent

else:

    ruta = Path(__file__).resolve().parent

Esto permite utilizar el mismo código tanto durante el desarrollo como en la 
aplicación empaquetada.

---

`file_manager.py`

Se encarga de descubrir los archivos Excel disponibles y generar los 
metadatos necesarios para su control.

Entre los datos registrados se encuentran:
- Nombre del archivo
- Ruta
- Hojas disponibles
- Identificador del archivo
- `hash_file`
- `hash_load`
- Fecha y hora de ejecución

### Identificación mediante hash

El proyecto usa dos IDs

`hash_file`

Identifica un archivo dentro del sistema de control.

Se construye utilizando información estable del archivo, su ruta, nombre
y hojas.

Su objetivo es determinar si el archivo ya fue procesado.

`hash_load`

Identifica una ejecución especifica e incorpora la fecha y hora de carga.

Su objetivo es diferenciar ejecuciones.

---

`file_extractor.py`

Se encarga de extraer la información del formato Excel.

Actualmente se extraen:

### Información del encabezado
- No. DE OBRA
- INICIO
- TERMINO
- FECHA
- RESIDENTE DE OBRA
- OBRA
- TRABAJOS A REALIZAR
- SUB-CONTRATISTA
- SUBCONTRATO Y/O DESTAJO

### Información de la tabla
- ID
- CLAVE DE PPTO
- CONCEPTO
- UNIDAD
- CANTIDAD
- P. UNITARIO
- P.U. AUTORIZADO

La posición de las celdas y estructura de la tabla corresponden al formato
especifico utilizado por el proceso.

---

`table_constructor.py`

Construye los registros finales que serán incorporados al archivo
consolidado.

Entre sus responsabilidades se encuentran:
- Integrar los datos del encabezado con la tabla.
- Asignar identificadores consecutivos.
- Convertir columnas numéricas.
- Calcular `IMPORTE`.
- Ordenar las columnas.
- Agregar los registros al archivo consolidado.

El importe se calcula mediante:
** IMPORTE = CANTIDAD x P. UNITARIO **

Las columnas numéricas principales son normalizadas mediante `pd.to_numeric()`
antes de realizar los cálculos.

---

`file_creator.py`

Se encarga de crear el archivo consolidado cuando todavía no existe. El archivo
generado es:

Caratula de pptos.xlsx

Contiene principalmente:
- Hoja `Instrucciones`
- Hoja `Registro`

La hoja de instrucciones explica al usuario el funcionamiento básico del 
proceso y el mecanismo utilizado para archivos corregidos.

---

`db_schema.py`

Administra la base de datos local utilizada para controlar los archivos 
procesados.

La base de datos utilizada es:

SQLite

y se genera como:

file_control.db

Su objetivo es mantener trazabilidad sobre los archivos que ya fueron 
procesados y evitar duplicaciones.

---

## Manejo de archivos corregidos

El sistema **no monitorea cambios en el contenido de los archivos ya procesados**.

Esta decisión es intencional para mantener el proceso sencillo y evitar realizar
comparaciones de contenido en cada ejecución.

Si un archivo ya procesado necesita una corrección, se debe modificar su nombre
agregando:

**CORREGIDO**

Por ejemplo:

Antes:
Destajo Obra A.xlsx

Después:
Destajo Obra A CORREGIDO.xlsx

Al cambiar el nombre, el archivo obtiene un nuevo `hash_file` y puede ser 
procesado como una nueva carga.

Este mecanismo permite mantener una trazabilidad sencilla de las versiones 
procesadas.

---

## Archivos generados

Durante la ejecución se generan dos archivos principales:

`Caratula de pptos.xlsx`

Archivo consolidado que contiene los registros extraídos de los formatos de 
origen.

`file_control.db`

Base de datos SQLite utilizada para controlar los archivos procesados.

Estos archivos son **productos de ejecución** y no deben incluirse en el 
repositorio de código.

---

## Ejecución desde Python

para ejecutar el programa durante el desarrollo:

py pipeline_presupuesto.py

El programa utilizará la carpeta donde se encuentra el proyecto como
carpeta de trabajo.

---

## Generación del ejecutable

El proyecto utiliza PyInstaller para generar una aplicación ejecutable.

Instalación:

py -m PyInstaller --version

Generación del ejecutable:

py -m PyInstaller --onefile --name "Procesador_Destajos" pipeline_presupuestos.py

El ejecutable se genera dentro de:

dist/Procesador_Destajos.exe

---

## Ejecución como aplicación

El usuario final no necesita ejecutar Python ni instalar las librerías del 
proyecto.

La estructura esperada de la carpeta de trabajo es:

``` text
Destajos/
|
|__ Procesador_Destajos.exe
|
|__ Destajo Obra A.xlsx
|__ Destajo Obra B.xlsx
|__ Destajo Obra C.xlsx
|
|__ Caratula de pptos.xlsx
|__ file_control.db

```

El usuario únicamente debe colocar los archivos Excel de origen en la carpeta
y ejecutar: `Procesador_destajos.exe`.

El programa identificará automáticamente los archivos que aún no hayan sido
procesados.

---

## Comportamiento del proceso
### Primera ejecución

```text
Excel nuevos
     ↓
Procesamiento
     ↓
Caratula de pptos.xlsx
     +
file_control.db
```

### Ejecuciones posteriores

```text

Excel ya registrados
        ↓
     Omitir

Excel nuevos
        ↓
    Procesar
```

### Archivo corregido

```text

Destajo A.xlsx
       ↓
Ya procesado

Destajo A CORREGIDO.xlsx
       ↓
Nuevo hash
       ↓
Procesar
```
---
## Pruebas realizadas

El funcionamiento del proceso fue validado mediante pruebas funcionales 
que cubren:

- Primera ejecución con archivos nuevos.
- Segunda ejecución sin archivos nuevos.
- Incorporación de un archivo nuevo.
- Procesamiento de archivos corregidos mediante cambio de nombre.
- Exclusión del archivo consolidado de la lista de archivos de entrada.
- Conversión de campos numéricos y cálculo de `IMPORTE`.

Las pruebas funcionales fueron completadas satisfactoriamente antes de 
generar el ejecutable.

---

## Tecnologías utilizadas

- Python 3.14.6
- Pandas
- OpenPyXL
- NumPy
- SQLite
- PyInstalller
- Excel (.xlsx)

---

## Alcance actual

El programa está diseñado específicamente para el formato de Excel utilizado 
actualmente en el proceso de destajos y presupuestos.

No se considera actualmente un sistema genérico de procesamiento de Excel.

La estructura de extracción depende de:

- Nombre de la hoja.
- Posiciones específicas de las celdas.
- Estructura de la tabla.
- columnas definidas por el formato.

Una modificación significativa del formato de origen puede requerir 
actualizar el módulo de extracción.

---

## Próximas mejoras

Posibles líneas de evolución del proyecto:

- Incorporar validaciones de calidad de datos.
- Mejorar los mensajes de ejecución.
- Registrar estadísticas de cada carga.
- Incorporar un reporte de archivos procesados.
- Mejorar el manejo de errores.
- Implementar una interfaz gráfica si el proceso lo requiere.
- Integrar posteriormente el resultado con la arquitectura general de datos de la organización.

---

## Estado del proyecto

### MVP funcional

El proceso de extracción, transformación, consolidación y control de archivos se encuentra implementado y probado.

El ejecutable `.exe` ha sido generado y validado en ejecución independiente del entorno de desarrollo.
