# To reload use sudo systemctl reload nginx 
uwsgi --socket 127.0.0.1:8080 -w wsgi &
