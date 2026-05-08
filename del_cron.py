from crontab import CronTab

cron = CronTab(user=True)

# Buscar y eliminar por comentario
# cron.remove_all(comment='mi_proceso_especial')

# O buscar y eliminar por el comando exacto
cron.remove_all(command='./git/datatool/run_env.sh 0fb86a93-a4e8-45e8-8059-d1f4af306c04 >> /home/julio/cron.log 2>&1')

cron.write()

