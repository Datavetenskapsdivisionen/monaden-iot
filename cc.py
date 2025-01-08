import pychromecast

def main():
    chromecast = pychromecast.get_listed_chromecasts(friendly_names=["Living Room TV"])[0][0]
    chromecast.wait()
    print(chromecast.name)

if __name__ == "__main__":
    main() 
