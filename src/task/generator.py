import requests, charlogger, json, time, random, threading, typing, string
from account_generator_helper import Person, GmailNator, TempMailPlus, InboxKitten
from bs4 import BeautifulSoup
from ..util.config import Config
from ..util.utils import utils

class CapsolverGen():
    def __init__(self, 
                workerNum: str = "001", 
                config: Config = Config()
            ) -> None:
        self.config = config
        self.session = requests.Session()
        self.proxy = self.config.getProxy()
        self.session.proxies = { "http": self.proxy, "https": self.proxy }
        self.session.headers.update({ "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36" })
        self.logger = self.config.getLogger(workerNum)
        self.refCode = self.config.genSettings.get("referral_code")
        self.discordToken = random.choice([x.strip() for x in open("data/tokens.txt", "r", encoding="utf8").readlines()])
        self.emailService = self.config.genSettings.get("tempmail")
        pass

    def start(self) -> None:
        try:
            self.setRequestData()
            self.sendEmailVerification()
        except Exception as e:
            self.logger.error(title="ERROR", data=e)
            return
        
    def cont(self) -> None:
        if self.config.genSettings.get("add_balance"):
            self.login()
            self.connectDiscord()
        
    def connectDiscord(self) -> None:
        headers = { "authorization": self.discordToken }
        body = {
            "permissions": "0",
            "authorize": True
        }
        resp = requests.post("https://discord.com/api/v9/oauth2/authorize?client_id=1062177869834502194&response_type=code&redirect_uri=https%3A%2F%2Fdashboard.capsolver.com%2Foauth2%2Fdiscord.html&scope=identify%20email%20guilds.join", allow_redirects=True, headers=headers, json=body, proxies=self.session.proxies)
        # print(resp.status_code, resp.text)
        code = resp.json().get("location").split("?code=")[1]
        resp = self.session.post("https://backend.captchaai.io/api/v1/oauth2/verify/discord", json={ "code": code })
        if resp.status_code == 201:
            self.token = resp.json().get("token")
            self.logger.paid(title="BALANCE", data=f"Added $0.10 of balance to account! Token: {self.token}")
            with open("output/keys.txt", "a") as f:
                f.write(f"{self.token}\n")
                f.close()
        else:
            print(resp.text)
            self.logger.warn(title="BALANCE", data=f"Couldn't sign up for free trial!")

    def login(self) -> None:
        body = {
            "email": self.email,
            "password": self.password,
            "inviteCode": self.refCode,
            "recaptchaToken": ""
        }
        resp = self.session.post("https://backend.captchaai.io/api/v1/passport/login", json=body)
        if resp.status_code == 201:
            self.logger.valid(title="LOGIN", data=f"Successfully logged into account {self.email}")
            self.session.headers.update({ "authorization": f"Bearer {resp.json().get('accessToken')}" })
        else:
            self.logger.valid(title="LOGIN", data=f"Couldn't log in! {resp.text}")

    def sendEmailVerification(self) -> None:
        body = { "email": self.email }
        resp = self.session.post("https://backend.captchaai.io/api/v1/passport/account/email/send", json=body)
        if resp.status_code == 201:
            self.logger.info(title="SENT", data=f"Sent email verification code to {self.email}")

            letters = [hash(_letter) for _letter in self.mail.get_inbox()]
                
            while not self.verifiedEmail:
                try:
                    for _letter in self.mail.get_inbox():
                        if hash(_letter) not in letters:
                            letters.append(hash(_letter))
                            self.mail._letter_handler(_letter)
                    time.sleep(5)
                except Exception as e:
                    self.logger.error(title="EMAIL", data=f"Error while checking email!")
                    pass

            # self.emailThread = threading.Thread(target=pollEmail, args=(self,))
            # self.emailThread.start()
        else:
            self.logger.error(title="FAIL", data=f"Unknown error on email verification. Status code: {resp.status_code}")
            print(resp.text)

    def signup(self) -> None:
        # threading.Thread(target=self.emailThread._stop).start()
        body = {
            "email": self.email,
            "code": self.verifyCode,
            "username": self.email,
            "password": self.password,
            "inviteCode": self.refCode,
            "recaptchaToken": ""
        }
        resp = self.session.post("https://backend.captchaai.io/api/v1/passport/account/email/reg", json=body)
        if resp.status_code == 201:
            self.logger.valid(title="CREATED", data=f"Created account! {self.email}:{self.password}")
            with open("output/created.txt", "a") as f:
                f.write(f"{self.email}:{self.password}\n")
                f.close()
            self.cont()
        else:
            if "code error" in resp.text:
                self.logger.warn(title="BAD CODE", data=f"Verification code is invalid, retrying...")
                self.sendEmailVerification()
            else:
                self.logger.error(title="FAIL", data=f"Unknown error on signup. Status code: {resp.status_code}")

    def setRequestData(self) -> dict:
        self.person = Person()
        self.firstName = self.person.name.split(" ")[0]
        self.lastName = self.person.name.split(" ")[0]
        self.username = self.person.name.replace(" ", "").lower()[:10] + str(random.randint(10, 99))
        self.password = utils.get_password()

        match self.emailService:
            case "GMAILNATOR":
                self.mail = GmailNator()
            case "TEMPMAIL_PLUS":
                 self.mail = TempMailPlus()
            case "INBOXKITTEN":
                self.mail = InboxKitten()

        @self.mail.letter_handler(from_email="no-reply@superai.pro")
        def emailVerifHandler(letter):
            self.logger.debug(title="EMAIL", data=f"Got email: {letter.subject}")
            emailContent = letter.letter
            # self.verifyCode = emailContent.split("""background-color: #4abc6a;">                                    """)[1].split("""                                  </a>""")[0]
            print(emailContent)

            match self.emailService:
                case "GMAILNATOR":
                    self.verifyCode = emailContent.split("<center style=\"color: #ffffff; font-family: sans-serif; font-size: 15px;\">")[1].split("</center>")[0].replace(" ", "").replace("\r", "").replace("\n", "")
                case "TEMPMAIL_PLUS":
                    # self.mail = TempMailPlus()
                    self.verifyCode = emailContent
                case "INBOXKITTEN":
                    soup = BeautifulSoup(emailContent, 'html.parser')
                    code_element = soup.find('p', text='Someone has created a CapSolver account with this email address. If this was you, To verify your account, please use the following code — it will expire in 30 minutes:')
                    self.verifyCode = code_element.find_next('a').text.replace(" ", "").replace("\n", "").replace("\r", "")
            
            self.verifiedEmail = True
            self.logger.info(title="EMAIL", data=f"Got verification code: {self.verifyCode}")
            self.signup()

        self.verifiedEmail = False

        self.email = self.mail.get_email()