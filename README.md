# Deployment

Scheme: Nginx <-> uwsgi <-> Django (python 3.6)

## Project code

Copy the project code in ```/var/www/```

## Python 

### CentOS (6/7) 
```
yum install gcc
```

Get source code from: http://python.org
Unarchive downloaded sources in a folder. 

'cd' into folder with unarchived code. 
Run:
```
./configure
make
make install
```

## virtualenv 

### Install 
```pip3 install virtualenv```

### Create environment 
```
cd /var/www/youtube
virtualenv -p python3.6 .venv
./.venv/bin/pip3 install -r requirements.txt
```

## Nginx

### Install

#### CentOS (6/7)
https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-centos-7

#### Ubuntu 16 
```
apt-get install nginx 
```

### Configuration

Create file /etc/nginx/conf.d/youtube.conf 
```
server {
    server_name 88.212.253.235 youtubetest.ru  www.youtubetest.ru;
    listen 80;

    location / {
        include    uwsgi_params;
        uwsgi_pass unix:/run/youtube.sock;
    }
}
```
### Start service

### CentOS 6
```
/etc/init.d/nginx start
```

### CentOS 7 / Ubuntu 16
```
systemctl start nginx
```

## UWSGI

### Install 
```pip3 install uwsgi```

### Configure 
```
mkdir -p /etc/uwsgi/vassals
```

Create file (if not exists) /etc/uwsgi/emperor.ini 
```
[uwsgi]
emperor = /etc/uwsgi/vassals
logto = /var/log/uwsgi/emperor.log
```

Create file /etc/uwsgi/vassals/youtube.init
```
[uwsgi]
# UWSGI config template for Dajngo 
project = youtube_platform
base = /var/www/youtube
log_filename = youtube.log
socket_path = /run/youtube.sock

chdir = %(base)
home = %(base)/.venv
module = %(project).wsgi:application

master = true
processes = 5

logto = /var/log/uwsgi/%(log_filename)
socket = %(socket_path)
chmod-socket = 666
vacuum = true
```

## Create service 

### CentOS 7 / Ubuntu 16

Create file (if not exists) /etc/systemd/system/uwsgi.service
```
[Unit]
Description=uWSGI Emperor service

[Service]
ExecStartPre=/usr/bin/bash -c 'mkdir -p /run/uwsgi && mkdir -p /var/log/uwsgi'
ExecStart=/usr/local/bin/uwsgi --ini /etc/uwsgi/emperor.ini
Restart=always
KillSignal=SIGQUIT
Type=notify
NotifyAccess=all
```

### CentOS 6 

Create file (if not exists) /etc/init.d/uwsgi 
```
 #!/bin/sh
        #
        # uwsgi        Startup script for uwsgi
        #
        # chkconfig: - 85 15
        # processname: uwsgi
        # description: uwsgi is an HTTP and reverse proxy server
        #
        ### BEGIN INIT INFO
        # Provides: uwsgi
        # Required-Start: $local_fs $remote_fs $network
        # Required-Stop: $local_fs $remote_fs $network
        # Default-Start: 2 3 4 5
        # Default-Stop: 0 1 6
        # Short-Description: start and stop uwsgi
        ### END INIT INFO

        # Source function library.
        . /etc/rc.d/init.d/functions

        DAEMON=/usr/local/bin/uwsgi
        DAEMON_OPTS="--ini /etc/uwsgi/emperor.ini"
        OWNER=uwsgi
        NAME=uwsgi
        RETVAL=0

        get_pid() {
            if [ -f /var/run/$daemon_name.pid ]; then
                echo `cat /var/run/$daemon_name.pid`
            fi
        }  

        case "$1" in
          start)
            mkdir -p '/var/log/uwsgi/'
            mkdir -p '/run/uwsgi/' 
            echo -n "Starting $NAME: "
                PID=$(get_pid)
                if [ -z "$PID" ]; then
                    [ -f /var/run/$NAME.pid ] && rm -f /var/run/$NAME.pid
                    touch /var/run/$NAME.pid                                        
                    chown $OWNER /var/run/$NAME.pid
                $DAEMON $DAEMON_OPTS & 
                fi
            ;;
          stop)
            echo -n "Stopping $NAME: "
                PID=$(get_pid)
                [ ! -z "$PID" ] && kill -s 3 $PID &> /dev/null
                if [ $? -gt 0 ]; then
                    echo "was not running"
                    exit 1
                else
                echo "$NAME."
                    rm -f /var/run/$NAME.pid &> /dev/null
                fi
            ;;
          reload)
                echo "Reloading $NAME"
                PID=$(get_pid)
                [ ! -z "$PID" ] && kill -s 1 $PID &> /dev/null
                if [ $? -gt 0 ]; then
                    echo "was not running"
                    exit 1
                else
                echo "$NAME."
                    rm -f /var/run/$NAME.pid &> /dev/null
                fi
            ;;
          force-reload)
                echo "Reloading $NAME"
                PID=$(get_pid)
                [ ! -z "$PID" ] && kill -s 15 $PID &> /dev/null
                if [ $? -gt 0 ]; then
                    echo "was not running"
                    exit 1
                else
                echo "$NAME."
                    rm -f /var/run/$NAME.pid &> /dev/null
                fi
                ;;
          restart)
                $0 stop
                sleep 2
                $0 start
            ;;
          status) 
            killall -10 $DAEMON
            ;;
              *) 
                N=/etc/init.d/$NAME
                echo "Usage: $N {start|stop|restart|reload|force-reload|status}" >&2
                exit 1
                ;;
            esac
exit 0
```

## Start service

### CentOS 7 / Ubuntu 16

```
systemctl start uwsgi
```

### CentOS 6
```
/etc/init.d/uwsgi start
```
