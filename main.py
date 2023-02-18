from src.task import CapsolverGen, CapsolverChecker
from src.util.config import Config

import threading, os

class main():
    def main(self):
        if not os.path.exists("output/"): os.mkdir("output/")
        if not os.path.exists("output/checker/"): os.mkdir("output/checker/")
        if not os.path.exists("data/"): os.mkdir("data/")
        self.config = Config()

        match self.config.globalSettings.get("mode"):
            case "GENERATOR":
                self.startGenerator()
            case "CHECKER":
                self.startChecker()

    def startGenerator(self):
        def runThread(taskId):
            prefixStr = f"{taskId}"
            if taskId < 100:
                if taskId < 10:
                    prefixStr = f"00{taskId}"
                else:
                    prefixStr = f"0{taskId}"
                
            while True:
                task = CapsolverGen(prefixStr, config=self.config)
                task.start()

        for x in range(self.config.globalSettings.get("threads")):
            threading.Thread(target=runThread, args=(x + 1,)).start()

    def startChecker(self):
        match self.config.checkerSettings.get("mode"):
            case "KEY":
                toCheck = [x.strip() for x in open("output/keys.txt", "r", encoding="utf8").readlines()]
            case "ACC":
                toCheck = [x.strip() for x in open("output/created.txt", "r", encoding="utf8").readlines()]

        def runThread(taskId: int):
            prefixStr = f"{taskId}"
            if taskId < 100:
                if taskId < 10:
                    prefixStr = f"00{taskId}"
                else:
                    prefixStr = f"0{taskId}"
            while len(toCheck) > 0:
                data = toCheck.pop()
                CapsolverChecker(workerNum=prefixStr, data=data, config=self.config).start()

        for x in range(self.config.globalSettings.get("threads")):
            threading.Thread(target=runThread, args=(x + 1,)).start()
if __name__ == "__main__":
    main().main()