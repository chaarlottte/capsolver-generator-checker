import json, charlogger, random

class Config():
    def __init__(self) -> None:
        self.configDict: dict = json.loads(open("data/config.json").read())

        self.globalSettings = self.configDict.get("global")
        self.styleSettings = self.globalSettings.get("style")
        self.genSettings = self.configDict.get("generator")
        self.checkerSettings = self.configDict.get("checker")

        self.proxies = [x.strip() for x in open("data/proxies.txt", "r", encoding="utf8").readlines()]
        pass

    def getProxy(self) -> str:
        proxyType = self.globalSettings.get("proxy_type")
        proxy = random.choice(self.proxies)

        if not "@" in proxy:
            host, port, username, password = proxy.split(":")
            proxy = f"{username}:{password}@{host}:{port}"

        return f"{proxyType}://{proxy}"

    def getLogger(self, workerNum: str) -> charlogger.Logger:
        defaultPrefix = self.styleSettings.get("default_prefix")
        defaultPrefix = defaultPrefix.replace("<WORKERNUM>", f"WORKER-{workerNum}")
        return charlogger.Logger(
            debug=self.styleSettings.get("debug_logging"),
            defaultPrefix=defaultPrefix,
            colorText=self.styleSettings.get("color_text")
        )
    