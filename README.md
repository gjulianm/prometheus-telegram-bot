# Prometheus Telegram bot

This is a simple Telegram bot that responds to commands with results from Prometheus queries. I built it for a home weather monitor system, so for example I could send the command */temperature* and have the bot respond with the results of a Prometheus query for the temperature sensors. Of course, you can make it work with whatever you want.

## Installation and usage

You can install this with `pip install git+https://github.com/gjulianm/prometheus-telegram-bot.git` and run it with the command `prometheus-telegram-bot`. It needs a configuration file, a sample of which is provided in [config.sample.json](./config.sample.json). The configuration file must contain the following keys:

* A *tg_token* key with the Telegram token for your bot. Read the [Telegram docs](https://core.telegram.org/bots#6-botfather) to see how to create a new bot.
* A *prometheus* key with the URL for the Prometheus instance to query.
* A *queries* key. This must be a dictionary, where the keys are the command names, and the value must be a list of query objects. Each query object must have a *query* key with the query string for Prometheus. Optionally, it can have a *description* that will be attached to the message, a *value_format* to format the value (uses Python `.format()` syntax, with `{0}` being the value to format), and *group_by_labels* that defines the labels that will be used as groups for the measurement.

For example, let's the sample configuration:

```json
{
    "tg_token": "my-telegram-token",
    "prometheus": "http://localhost:9090",
    "queries": {
        "scrapers": [
            {
                "description": "Enabled scrapers",
                "query": "up",
                "group_by_labels": ["instance", "job"],
                "value_format": "Up = {0}"
            }
        ]
    }
}
```

This configuration will make the bot accept a command, */scrapers*. When it receives that command, it will make the query *up* to the Prometheus server, which will return the latest values for all possible labels. The bot will group those results by instance and job, and format them with the string formatter given. The message the bot will send will be something like this:

> **Enabled scrapers**
>
> localhost:9090, prometheus: Up = 1.0
>
> localhost:9100, node: Up = 1.0

You can add as many commands as you like, and add as many queries as you want to a single command.

## Running as a service

You can use the prometheus-telegram-bot.service, set in *ExecStart* the correct path of the prometheus-telegram-bot executable (and change any CLI arguments you want, probably setting the configuration file in /etc/ or something like that) and then drop the file in */etc/systemd/system*. After running `systemctl daemon-reload`, you will be able to use prometheus-telegram-bot as a regular systemd service and enable it on boot if you want.
