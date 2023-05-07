# CloudAdmin

## Instalar nginx

```bash
sudo apt update
sudo apt install nginx
sudo systemctl status nginx.service
```

## Instalar uwsgi
```bash
sudo apt-get install uwsgi
```

## Instalar pip 

```bash
sudo apt install python3-pip
pip3 --version
```

### Adicionar packages
```bash
pip install uwsgi
pip install 
```

## Preparar diretório

```bash
cd /etc/nginx
mkdir server
```
### Criar scripts

```bash
cd /etc/nginx/server
echo "pkill -TERM uwsgi" > killUWSGI.sh
echo "# To reload use sudo systemctl reload nginx 
uwsgi --socket 127.0.0.1:8080 -w wsgi &" > initUWSGI.sh

chmod +x killUWSGI.sh
chmod +x initUWSGI.sh
```

## Iniciar e testar
```bash
sudo systemctl reload nginx.service
./killUWSGI.sh
./initUWSGI.sh
```



