#!/usr/bin/python3

import json
import summary
import schedule
import time


config = json.load(open("config.json", "r"))

def main():
    schedule.every().day.at("23:00").do(summary.run)
    summary.run()
    while True:
        schedule.run_pending()
        try:
            time.sleep(600)
        except KeyboardInterrupt:
            exit(130)


if __name__ == "__main__":
    main()
