from crontab import CronTab

# Access the current user's crontab
cron = CronTab(user=True)

# Define the command and create a new job
job = cron.new(command='date >> /home/julio/file.txt')

# Set the schedule (e.g., every minute)
# job.minute.every(1)

# Example: Run every day at 2:30 PM (14:30)
# job.minute.on(30)
# job.hour.on(14)

# OR set it all at once using cron syntax
job.setall('25 0 * * *')

# Write the job to the system crontab
cron.write()

