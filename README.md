# dbot

dbot is a simple IRC bot framework base which is written to be easily extended.

[dbot.py](./dbot.py) and Python 3.6 or later are all you need to write an IRC bot utilizing this project.  
[youtube.py](./youtube.py) is included as a useful example module.

## Example bot code
```python
import dbot.py
import youtube.py

def yt(**kwargs):
    user = kwargs.get('nick')
    target = kwargs.get('target')
    search_phrase = kwargs.get('args') 
    if search_phrase:
        bot.privmsg(target, youtube.get_url(search_phrase))

host = irc.example.org
port = 6667
nick = 'dbot'
channels = ['#channels', '#to', '#join']
fantasy = {'yt': yt}

server = dbot.Server(host, port, nick, channels)
bot = dbot.Bot(server, fantasy)
bot.run()
```

## TO-DO
- clean up/document code
