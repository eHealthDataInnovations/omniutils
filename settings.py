import logging
import os
from pathlib import Path

# Configurar logging para exibir mensagens no console
# logging.basicConfig(
#     level=logging.DEBUG,  # Definir nível de log
#     format='%(levelname)s: %(message)s',  # Formato das mensagens de log
#     force=True
# )

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent


def get_requests_cache_expire_after_days() -> int:
    return int(os.getenv("REQUESTS_CACHE_EXPIRE_AFTER_DAYS", 30))


def get_log_rotary_file_backup_count() -> int:
    return int(os.getenv("LOG_ROTARY_FILE_BACKUP_COUNT", 10))


def get_disk_cache_expire() -> int:
    duracao = 3600 * 24 * 30  # 30 dias
    return int(os.getenv("DISK_CACHE_EXPIRE", duracao))
