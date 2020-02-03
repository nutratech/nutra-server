from crontab import CronTab

from ..settings import SERVER_HOST


def caffeinate():
    return
    # Keeps server awake
    cron = CronTab()
    job = cron.new(command=f"/usr/bin/curl {SERVER_HOST}")
    # At minute 0 and 30 past every hour from 6 through 20.
    job.setall("00,30 06-20 * * *")
    job.run()
