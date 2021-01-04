from socket import create_connection, socket
from signal import signal, SIGINT
from ssl import SSLContext, PROTOCOL_TLSv1_2
from sys import stderr


class Message(str):
    def __init__(self, o):
        super().__init__()
        self.cmd = None
        self.target = None
        self.content = None
        self.nick = None
        if self.startswith('PING'):
            self.cmd = 'PING'
            self.pong = self.split(' ')[1]
        elif self.startswith(':') and self.count(':'):
            self.prefix, sub = self.lstrip(':').split(' ', maxsplit=1)
            if ':' in sub:
                sub, self.content = sub.split(':', maxsplit=1)
            self.cmd, middle = sub.split(' ', maxsplit=1)
            if self.cmd == 'PRIVMSG':
                self.nick = self.prefix.split('!')[0]
                if is_channel(middle):
                    self.target = middle.split(' ')[0]
                else:
                    self.target = self.prefix.split('!')[0]

    def print(self):
        print(f'>> {self}')

    def printerr(self):
        stderr.write(f'{self}\n')
        exit(1)


class Server:
    def __init__(self, host, port, nick, channels, tls=False, serverpass=None, nickpass=None, hostname=None,
                 servername=None, realname=None, qmesg='Bye!'):
        self.host = host
        self.port = port
        self.nick = nick
        self.channels = channels
        self.tls = tls
        self.serverpass = serverpass
        self.nickpass = nickpass
        self.hostname = hostname if hostname is not None else nick
        self.servername = servername if servername is not None else nick
        self.realname = realname if realname is not None else nick
        self.qmesg = qmesg


class Bot:
    def __init__(self, server, fantasy, prefix='.'):
        self.server = server
        self.conn = socket()
        self.fantasy = fantasy
        self.prefix = prefix
        signal(SIGINT, self.close)

    def close(self, sig, frame):
        self.send(f'QUIT {self.server.qmesg}')
        exit(0)

    def run(self):
        with create_connection((self.server.host, self.server.port)) as conn:
            if self.server.tls:
                with SSLContext(PROTOCOL_TLSv1_2).wrap_socket(conn, server_hostname=self.server.host) as self.conn:
                    self.register()
            else:
                self.conn = conn
                self.register()

    def register(self):
        registered = False
        self.send(f'NICK {self.server.nick}')
        self.send(f'USER {self.server.nick} {self.server.hostname} {self.server.servername} :{self.server.realname}')
        while not registered:
            for msg in self.recv():
                msg.print()
                if any(msg.cmd == s for s in ('376', 'MODE', '422')):
                    registered = True
        self.join()
        self.loop()

    def send(self, msg):
        print(f'<< {msg}')
        msg += '\r\n'
        self.conn.send(bytes(msg, 'utf-8'))

    def recv(self):
        buf = ''
        while True:
            b = self.conn.recv(2048)
            try:
                buf += b.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    buf += b.decode('windows-1252')
                except TypeError:
                    print('Discarding buffer with invalid byte')

            if buf.endswith('\r\n'):
                break
        buf = buf.rstrip('\r\n')
        for m in buf.split('\r\n'):
            msg = Message(m)
            if msg.cmd == 'PING':
                msg.print()
                self.send(f'PONG {msg.pong}')
            else:
                yield msg

    def join(self):
        for channel in self.server.channels:
            self.send(f'JOIN {channel}')

    def loop(self):
        while True:
            for msg in self.recv():
                msg.print()
                if msg.target is not None:
                    if ' ' in msg.content:
                        fcmd, args = msg.content.split(' ', maxsplit=1)
                    else:
                        fcmd = msg.content
                        args = None
                    if is_channel(msg.target) and not fcmd.startswith(self.prefix):
                        fcmd = ''
                    fcmd = fcmd.lstrip(self.prefix)
                    if fcmd in self.fantasy:
                        self.fantasy.get(fcmd)(**{'target': msg.target, 'args': args, 'nick': msg.nick})

    def privmsg(self, target, msg):
        self.send(f'PRIVMSG {target} :{msg}')


def is_channel(s: str):
    if any(s.startswith(c) for c in ('#', '&')):
        return True
    return False
