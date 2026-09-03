import time
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def ejecutar_prueba_volumen():
    print("--- INICIANDO PRUEBA DE VOLUMEN PNF-007 (Esquema Acadex) ---")
    
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cursor = conn.cursor()

    try:
        # 1. Insertamos datos base dejando que la identidad se genere sola
        print("Preparando datos base (usuario y categoría)...")
        cursor.execute("""
            INSERT INTO usuarios (correo_electronico, contrasena, es_admin) 
            VALUES ('volumen@acadex.com', 'hash_seguro_123', false)
            ON CONFLICT (correo_electronico) DO NOTHING;
        """)
        
        cursor.execute("""
            INSERT INTO categorias (nombre_categoria) 
            VALUES ('Academico')
            ON CONFLICT (nombre_categoria) DO NOTHING;
        """)
        conn.commit()

        # 2. Inserción masiva de 5,000 registros en 'tareas'
        print("Insertando 5,000 registros masivos en la tabla 'tareas'...")
        inicio_insercion = time.time()
        
        query_insert = """
            INSERT INTO tareas (
                nombre, descripcion, fecha_entrega, estado, 
                dificultad_estimada, tiempo_estimado, prioridad, 
                tiempo_acumulado, cronometro_activo, 
                id_usuario, id_grupo, id_categoria
            )
            SELECT 
                'Tarea Volumen ' || generate_series, 
                'Descripción masiva para la prueba de volumen número ' || generate_series, 
                NOW() + (generate_series || ' days')::interval,
                'pendiente', 
                3, 60, 2, 
                0, false, 
                1, NULL, 1
            FROM generate_series(1, 5000);
        """
        cursor.execute(query_insert)
        conn.commit()
        
        fin_insercion = time.time()
        print(f"-> ¡5,000 registros insertados con éxito en {fin_insercion - inicio_insercion:.4f} segundos!")

        # 3. Búsqueda Simple (por clave primaria ID)
        print("\nEjecutando Búsqueda Simple (por id_tarea)...")
        inicio_busqueda_simple = time.time()
        
        cursor.execute("SELECT * FROM tareas WHERE id_tarea = 2500;")
        cursor.fetchone()
        
        fin_busqueda_simple = time.time()
        tiempo_simple = fin_busqueda_simple - inicio_busqueda_simple
        print(f"-> Búsqueda simple completada en: {tiempo_simple:.6f} segundos.")

        # 4. Búsqueda Compleja (con filtros de texto ILIKE, prioridad y ordenamiento)
        print("\nEjecutando Búsqueda Compleja (filtros, texto y ordenamiento)...")
        inicio_busqueda_compleja = time.time()
        
        query_compleja = """
            SELECT * FROM tareas 
            WHERE nombre ILIKE '%Volumen 300%' 
            AND prioridad >= 2 
            ORDER BY fecha_entrega DESC, dificultad_estimada ASC;
        """
        cursor.execute(query_compleja)
        resultados_complejos = cursor.fetchall()
        
        fin_busqueda_compleja = time.time()
        tiempo_compleja = fin_busqueda_compleja - inicio_busqueda_compleja
        print(f"-> Búsqueda compleja completada en: {tiempo_compleja:.6f} segundos (Encontrados: {len(resultados_complejos)} registros).")

    except Exception as e:
        print(f"Error durante la ejecución de la prueba: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("-----------------------------------------------------------------")

if __name__ == "__main__":
    ejecutar_prueba_volumen()