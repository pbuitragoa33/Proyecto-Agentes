# Lector y procesador de datos SNIES para análisis de programas académicos

# La idea es que analice los datos de SNIES para un programa académico dado y guardar los
# resultados. Y retorne un diccionario con las rutas a las gráficas y datos clave.


# Librerias necesarias

import pandas as pd
import matplotlib.pyplot as plt
import os


# Flujo principal 

def analizar_snies(nombre_programa_usuario: str, output_dir: str = 'reporte_snies') -> dict:

    print("Iniciando análisis SNIES para: ", nombre_programa_usuario, "...")


    # Directorio de salida

    if not os.path.exists(output_dir):

        os.makedirs(output_dir)


    # La entrada del usuuario se recibe como argumento de la función

    programa_limpio = nombre_programa_usuario.lower()
    programa_set = set(programa_limpio.split())
    requerido = programa_set 
    n = len(programa_set)

    # Carga de los datos SNIES del repo del profe

    maestro = pd.read_parquet('https://robertohincapie.com/data/snies/MAESTRO.parquet')
    oferta = pd.read_parquet('https://robertohincapie.com/data/snies/OFERTA.parquet')
    programas = pd.read_parquet('https://robertohincapie.com/data/snies/PROGRAMAS.parquet')
    ies = pd.read_parquet('https://robertohincapie.com/data/snies/IES.parquet')

    # Prueba de que hay datos

    print("Maestro: ", len(maestro), "oferta: ", len(oferta), 
          "Programas: ", len(programas), "Instituciones: ", len(ies))


    # Filtrado de programas equivalentes

    equivalentes = []

    for prg in programas['PROGRAMA_ACADEMICO'].unique():

        prg2 = str(prg).lower().split()
        indice_jaccard = len(programa_set.intersection(prg2)) / len(programa_set.union(prg2))

        # Umbral de Jaccard en 0.5 y que contenga todas las palabras clave

        if(indice_jaccard >= 0.5 and len(requerido.intersection(prg2)) == len(requerido)):

            equivalentes.append(prg)

    if not equivalentes:

        print("Advertencia: No se encontraron programas equivalentes exactos en SNIES.")


    programas2 = programas[programas['PROGRAMA_ACADEMICO'].isin(equivalentes)]
    snies2 = list(programas2['CODIGO_SNIES'].unique())
    maestro2 = maestro[maestro['CODIGO_SNIES'].isin(snies2)]

    institucion = {ies:name for ies,name in programas[['IES_PADRE','INSTITUCION']].values if str(ies) not in ['null','Nan']}
    maestro3 = maestro2.merge(programas, left_on = 'CODIGO_SNIES', right_on = 'CODIGO_SNIES', how = 'left')
    maestro4 = maestro3.merge(oferta, on = ['CODIGO_SNIES', 'PERIODO'], how = 'left')

    # Diccionario de resultados

    resultados = {
        'graficas': {},
        'tablas': {},
        'texto_programas': ''
    }

    # Guardar gráficas pues pueden servir para el reporte

    # Gráfica 1: Número de programas e instituciones

    NprogNies = maestro4.groupby(by = 'PERIODO').agg({'CODIGO_INSTITUCION_x':'nunique', 'CODIGO_SNIES':'nunique'})
    resultados['tablas']['n_prog_ies_tiempo'] = NprogNies.to_dict()

    # Gráfica 2: Costo vs Matriculados

    maestro4['PROXY_PER'] = maestro4['PROXY_PER'].astype(int)
    df = maestro4[(maestro4['PROXY_PER'] >= 20211) & (maestro4['PROXY_PER'] <= 20242)].copy()
    df.loc[:,'Nombre_ies'] = df['INSTITUCION']+ ' - ' + df['PROGRAMA_ACADEMICO']
    df = df[df['PROCESO'] == 'MATRICULADOS'].copy()
    df['CANTIDAD'] = df['CANTIDAD'].astype(int)
    df = df[['CODIGO_SNIES', 'MATRICULA', 'CANTIDAD', 'Nombre_ies', 'PERIODO',
         'DEPARTAMENTO_PROGRAMA', 'MUNICIPIO_PROGRAMA']]

    df = df.dropna()
    df = df[df['MATRICULA'] != 'null'].copy()

    df['MATRICULA'] = df['MATRICULA'].astype(float)

    ####print("Columnas en df:", df.columns)

    df2 = df.groupby(by = 'Nombre_ies').agg({'MATRICULA':'last', 'CANTIDAD':'mean'})

    # Grafica 2: Costo vs Matriculados

    plt.figure() 
    plt.scatter(df2['CANTIDAD'], df2['MATRICULA'])
    plt.xlabel('Promedio de estudiantes matriculados (2021-2023)')
    plt.ylabel('Valor último de matrícula pagado')
    plt.title('Costo vs. Promedio de Matriculados')

    path_g2 = os.path.join(output_dir, 'grafica_costo_matriculados.png')

    plt.savefig(path_g2)
    plt.close()

    resultados['graficas']['costo_vs_matriculados'] = path_g2
    resultados['tablas']['costo_vs_matriculados'] = df2.to_dict()

    # Grafica 3: Valor matrículas en el tiempo

    valor = pd.pivot_table(df, index = 'Nombre_ies',columns = 'PERIODO', values = 'MATRICULA', aggfunc = 'mean', fill_value = 0)
    
    plt.figure()
    valor.T.plot(legend = False) 
    plt.title('Evolución Valor de Matrícula')
    path_g3 = os.path.join(output_dir, 'grafica_evolucion_matricula.png')
    plt.savefig(path_g3)
    plt.close()
    resultados['graficas']['evolucion_matricula'] = path_g3

    # Grafica 4: Programas por Dpto y Mpio

    porDpto = df.groupby('DEPARTAMENTO_PROGRAMA').agg({'CODIGO_SNIES':'nunique'}).sort_values(by = 'CODIGO_SNIES', ascending = False)
    porMpio = df.groupby('MUNICIPIO_PROGRAMA').agg({'CODIGO_SNIES':'nunique'}).sort_values(by = 'CODIGO_SNIES', ascending = False)
    
    plt.figure()
    porDpto.head(10).plot.bar() 
    plt.title('Programas por Departamento (Top 10)')
    path_g4_dpto = os.path.join(output_dir, 'grafica_por_dpto.png')
    plt.savefig(path_g4_dpto)
    plt.close()
    resultados['graficas']['por_dpto'] = path_g4_dpto
    resultados['tablas']['por_dpto'] = porDpto.to_dict()

    # Grafica 5: Estudiantes en el tiempo

    num = pd.pivot_table(maestro4, index = 'PERIODO', columns = 'PROCESO', values = 'CANTIDAD', fill_value = 0, aggfunc = 'sum')
    
    fig, axes = plt.subplots(5, 1, sharex = True, figsize = (12, 14)) 

    for i,col in enumerate(num.columns): 

        axes[i].plot(num[col])
        axes[i].set_title(col)

        if(i < len(num.columns) -1):

            axes[i].label_outer()

        else:

            plt.xticks(rotation = 90)

        axes[i].grid()

    plt.tight_layout()
    path_g5 = os.path.join(output_dir, 'grafica_estudiantes_tiempo.png')
    plt.savefig(path_g5)
    plt.close()
    resultados['graficas']['estudiantes_tiempo'] = path_g5


    # Creación del prompt

    cad = ''
    i = 1

    for ies, prg, mpio in maestro4[['INSTITUCION', 'PROGRAMA_ACADEMICO', 'MUNICIPIO_PROGRAMA']].drop_duplicates().values:
        
        cad = cad + 'Programa ' + str(i) + ': Universidad: ' + ies+', Programa: ' + prg+', Ubicación o ciudad: ' + mpio+'. '
        i+=1

    resultados['texto_programas'] = cad

    print("Análisis SNIES completado")

    return resultados


#if __name__ == "__main__":

#    analizar_snies('Doctorado Matematicas')   # Si funciona Mari. Si no hay carreras equivalentes saca error