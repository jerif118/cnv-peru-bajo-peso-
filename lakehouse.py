"""Conexión y consultas compartidas por los notebooks de nacimientos."""

import os
from pathlib import Path

from databricks import sql
from dotenv import load_dotenv


class Lakehouse:
    def __init__(self):
        load_dotenv(Path(__file__).resolve().parent / ".env")
        self.catalogo = os.getenv("DATABRICKS_CATALOG")
        self.archivo_origen = os.getenv("DATABRICKS_RAW_CSV_PATH", "")
        servidor = os.getenv("DATABRICKS_SERVER_HOSTNAME")
        ruta_sql = os.getenv("DATABRICKS_HTTP_PATH")
        if not servidor or not ruta_sql or not self.catalogo:
            raise RuntimeError("Falta la conexión: completa .env según .env.example")

        self.conexion = sql.connect(
            server_hostname=servidor,
            http_path=ruta_sql,
            auth_type="databricks-oauth",
        )

    def preparar_sql(self, query):
        if "__ARCHIVO_ORIGEN__" in query and not self.archivo_origen:
            raise RuntimeError("Falta DATABRICKS_RAW_CSV_PATH en .env")
        return (query.replace("__CATALOGO__", self.catalogo)
                     .replace("__ARCHIVO_ORIGEN__", self.archivo_origen)
                     .replace("__NOMBRE_ARCHIVO__", Path(self.archivo_origen).name))

    def consultar(self, query, categorias=False):
        """categorias=True devuelve los textos como pandas category (menos memoria)."""
        with self.conexion.cursor() as cursor:
            cursor.execute(self.preparar_sql(query))
            return cursor.fetchall_arrow().to_pandas(strings_to_categorical=categorias)

    def ejecutar(self, query):
        with self.conexion.cursor() as cursor:
            cursor.execute(self.preparar_sql(query))

    def cerrar(self):
        self.conexion.close()
