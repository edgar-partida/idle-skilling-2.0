import os
import logging


def configurar_logger(nombre_log: str = "IdleSkillingBot", archivo_log: str = "resources/app.log") -> logging.Logger:
    """Configura y retorna un logger persistente que escribe en consola y en un archivo de texto."""

    # Asegurar que el directorio resources exista
    dir_name = os.path.dirname(archivo_log)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)

    logger = logging.getLogger(nombre_log)
    logger.setLevel(logging.DEBUG)

    # Evitar duplicidad de handlers si ya fue configurado antes
    if not logger.handlers:
        # Formato detallado con fecha, hora, nivel y mensaje
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) -> %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 1. Handler para archivo (persistencia)
        file_handler = logging.FileHandler(archivo_log, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 2. Handler para consola (opcional, para depuración rápida)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
