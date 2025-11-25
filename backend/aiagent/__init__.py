# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

# 初始化 PyMySQL
# PyMySQL 需要在使用前进行初始化，以替代 mysqlclient
import pymysql
pymysql.install_as_MySQLdb()

__all__ = ('celery_app',)
