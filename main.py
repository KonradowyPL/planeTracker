#!/usr/bin/python3
import json

config = json.load(open("config.json", "r"))



def main():
    if config['mode'] == "live":
        import live        
        live.run()


if __name__ == "__main__":
    main()
