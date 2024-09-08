#!/usr/bin/python3
import json

config = json.load(open("config.json", "r"))



def main():
    if config['mode'] == "live":
        import live        
        live.start()
    elif config['mode'] == "summary":
        import summary        
        summary.start()

if __name__ == "__main__":
    main()
