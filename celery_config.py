import configparser

config = configparser.ConfigParser()
config.read("config.ini")

broker_url=config.get("celery", "broker") + "://" + config.get("celery", "host") + ":" +config.get("celery", "port"),
result_backend=config.get("celery", "broker") + "://" + config.get("celery", "host") + ":" +config.get("celery", "port")
worker_max_memory_per_child=6000000
task_acks_late = True
worker_prefetch_multiplier = 1