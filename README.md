# Capsolver Generator/Checker
A tool to create infinite accounts for [capsolver](https://capsolver.com) and add balance to them.

Also a checker because why not.

## How to use
Put your proxies in `data/proxies.txt`. Format them as either `user:pass@host:port` or `host:port:user:pass`.

Put at least one Discord token in `data/tokens.txt`. I would recommend more, but it doesn't really matter.

In `data/config.json`, everything should be pretty self-explanatory. If you want to use your referral code, you can change the default one to yours. Also make sure that, if you are using socks4/socks5 proxies, you change the `proxy_type` variable to your proxy's type.

You can also change the mode in `data/config.json`. Each setting with multiple options will have its options displayed in the file.

## Credits
[kek](https://github.com/kekeds) for originally creating a capsolver gen and showing it off, which inspired me to create this one.
I also stole line 143 of generator.py from his capsolver gen, which you can find [here](https://github.com/kekeds).

Also, thanks to [Dionis1902](https://github.com/Dionis1902) for his [AccountGeneratorHelper](https://github.com/Dionis1902/AccountGeneratorHelper) which helped me implement the tempmail service.