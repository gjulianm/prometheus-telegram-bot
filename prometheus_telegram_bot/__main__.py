# Module entry point
import sys
import argparse
import logging
import datetime
import time
import subprocess
import re
import json
import collections
import telegram
import codecs

from telegram.ext import Updater, CommandHandler

from .utils import configure_log
from .prometheus import PrometheusClient

command_queries = {}
prometheus = PrometheusClient(None)  # Initialized later


def tg_start(update, context):
    logging.info(
        f'Received /start from ID {update.effective_user.id}, {update.effective_user.username}')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hello! This is the Prometheus bot helper. Say /help to see the available commands")


def tg_help(update, context):
    message = "Available commands:\n\n" + "\n".join(command_queries.keys())

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message)


def tg_query(update, context):
    logging.info(
        f'Received {update.effective_message.text} from ID {update.effective_user.id}, {update.effective_user.username}')

    queries = command_queries[update.effective_message.text]
    message = ""

    for query in queries:
        results = prometheus.query(query['query'])
        query_results = collections.defaultdict(list)

        for result in results:
            labels = [result['metric'].get(l)
                      for l in query.get('group_by_labels', [])]
            labels_str = ", ".join(sorted(labels))

            query_results[labels_str].append(float(result['value'][1]))

        fmt = query.get('value_format', "{0}")

        if len(message) > 0:
            message += "\n"

        if 'description' in query:
            message += f'*{query["description"]}*\n'

        for labels_s, values in query_results.items():
            values_fmt = ", ".join(fmt.format(v) for v in values)

            if len(labels_s) > 0:
                message += f"{labels_s}: {values_fmt}\n"
            else:
                message += f"{values_fmt}\n"

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message, parse_mode=telegram.ParseMode.MARKDOWN)


def main(args=None):
    argp = argparse.ArgumentParser(
        description='Telegram bot for communicating with Prometheus')

    argp.add_argument('--verbose', '-v', action='store_true',
                      help='Verbose log output')

    argp.add_argument('--config', '-c', type=argparse.FileType('r'),
                      help="Configuration file (JSON format)", required=True)

    args = argp.parse_args()

    configure_log(args=args)

    logging.info(f"Loading config from {args.config}")

    # Ensure tildes and such are correctly interpreted
    with codecs.open(args.config.name, 'r', encoding='utf-8') as f:
        config = json.load(f)

    if 'tg_token' not in config:
        logging.error("Field 'tg_token' not found in config")
        sys.exit(1)

    if 'queries' not in config:
        logging.error("No queries configured!")
        sys.exit(1)

    tg_token = config['tg_token']

    global prometheus
    prometheus = PrometheusClient(config['prometheus'])

    updater = Updater(token=tg_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', tg_start))
    dispatcher.add_handler(CommandHandler('help', tg_help))

    for command, queries in config['queries'].items():
        logging.info(
            f'Adding handler for {command} with {len(queries)} queries')
        dispatcher.add_handler(CommandHandler(command, tg_query))

        command_queries[f'/{command}'] = queries

    logging.info('Starting polling for Telegram messages...')

    updater.start_polling()
