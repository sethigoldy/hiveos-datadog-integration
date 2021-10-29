from slackbot import app
from uptime import start_uptime

if __name__ == "__main__":
    # start uptime robot with the main app
    start_uptime()
    app.run()
