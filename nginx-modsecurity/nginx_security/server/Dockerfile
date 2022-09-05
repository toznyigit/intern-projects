FROM quay.io/centos/centos:stream8 

COPY ./cagri.crt /etc/pki/ca-trust/source/anchors/cagri.crt
RUN update-ca-trust

RUN dnf update -y
RUN yum groupinstall -y "Development Tools"
RUN yum install -y procps httpd httpd-devel pcre pcre-devel libxml2 libxml2-devel curl curl-devel\
                   openssl openssl-devel gcc wget nano python38-devel python38-pip git mlocate
RUN updatedb

# FLASK APP REQUIREMENTS
RUN pip3 install --upgrade pip --trusted-host files.pythonhosted.org --cert /etc/pki/ca-trust/source/anchors/cagri.crt
RUN pip3 install --upgrade wheel --trusted-host files.pythonhosted.org --cert /etc/pki/ca-trust/source/anchors/cagri.crt
RUN pip3 install --upgrade setuptools --trusted-host files.pythonhosted.org --cert /etc/pki/ca-trust/source/anchors/cagri.crt

RUN pip3 install flask --trusted-host files.pythonhosted.org --cert /etc/pki/ca-trust/source/anchors/cagri.crt
RUN pip3 install psycopg2-binary --trusted-host files.pythonhosted.org --cert /etc/pki/ca-trust/source/anchors/cagri.crt
RUN pip3 install python-dotenv --trusted-host files.pythonhosted.org --cert /etc/pki/ca-trust/source/anchors/cagri.crt
RUN pip3 install uwsgi --trusted-host files.pythonhosted.org --cert /etc/pki/ca-trust/source/anchors/cagri.crt
RUN pip3 install ansible --trusted-host files.pythonhosted.org --cert /etc/pki/ca-trust/source/anchors/cagri.crt

# MODSECURITY INSTALL
WORKDIR /opt
RUN git clone https://github.com/SpiderLabs/ModSecurity
WORKDIR /opt/ModSecurity
RUN git submodule init
RUN git submodule update
RUN ./build.sh
RUN ./configure
RUN make
RUN make install

# MODSECURITY_NGINX CONNECTOR INSTALL
WORKDIR /opt
RUN git clone --depth 1 https://github.com/SpiderLabs/ModSecurity-nginx.git

# NGINX INSTALL
WORKDIR /opt
RUN wget http://nginx.org/download/nginx-1.18.0.tar.gz
RUN tar -xvzmf nginx-1.18.0.tar.gz
WORKDIR /opt/nginx-1.18.0
RUN groupadd -r nginx
RUN useradd -r -g nginx -s /sbin/nologin -M nginx
RUN ./configure --add-dynamic-module=../ModSecurity-nginx  --user=nginx --group=nginx\
    --with-cc-opt='-g -O2 -fdebug-prefix-map=/build/nginx-GkiujU/nginx-1.18.0=. -fstack-protector-strong -Wformat -Werror=format-security -fPIC -Wdate-time -D_FORTIFY_SOURCE=2' --with-ld-opt='-Wl,-Bsymbolic-functions -Wl,-z,relro -Wl,-z,now -fPIC'\
    --prefix=/usr/share/nginx --conf-path=/etc/nginx/nginx.conf --http-log-path=/var/log/nginx/access.log\
    --error-log-path=/var/log/nginx/error.log --lock-path=/var/lock/nginx.lock --pid-path=/run/nginx.pid\
    --modules-path=/usr/lib/nginx/modules --http-client-body-temp-path=/var/lib/nginx/body\
    --http-fastcgi-temp-path=/var/lib/nginx/fastcgi --http-proxy-temp-path=/var/lib/nginx/proxy\
    --http-scgi-temp-path=/var/lib/nginx/scgi --http-uwsgi-temp-path=/var/lib/nginx/uwsgi --with-debug --with-pcre-jit\
    --with-http_ssl_module --with-http_stub_status_module --with-http_realip_module --with-http_auth_request_module\
    --with-http_v2_module --with-http_dav_module --with-http_slice_module --with-threads --with-http_addition_module\
    --with-http_gunzip_module --with-http_gzip_static_module --with-http_sub_module --with-stream=dynamic --with-stream_ssl_module\
    --with-mail=dynamic --with-mail_ssl_module
RUN make
RUN make install
RUN make modules
RUN mkdir -p /var/lib/nginx/body

# MODSECURITY_NGINX CONNECTOR CONFIG
RUN mkdir -p /etc/nginx/modules
RUN cp objs/ngx_http_modsecurity_module.so /etc/nginx/modules
RUN rm -rf /usr/share/modsecurity-crs
RUN git clone https://github.com/coreruleset/coreruleset /usr/local/modsecurity-crs
RUN mv /usr/local/modsecurity-crs/crs-setup.conf.example /usr/local/modsecurity-crs/crs-setup.conf
RUN mv /usr/local/modsecurity-crs/rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf.example /usr/local/modsecurity-crs/rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf

# MODSECURITY CONFIG
RUN mkdir -p /etc/nginx/modsec
RUN cp /opt/ModSecurity/unicode.mapping /etc/nginx/modsec
RUN cp /opt/ModSecurity/modsecurity.conf-recommended /etc/nginx/modsec/modsecurity.conf
RUN mkdir -p /etc/modsecurity
RUN cp /opt/ModSecurity/modsecurity.conf-recommended /etc/modsecurity/modsecurity.conf
RUN sed -i "s/SecRuleEngine DetectionOnly/SecRuleEngine On/" /etc/nginx/modsec/modsecurity.conf
COPY ./main.conf /etc/nginx/modsec/main.conf

# UWSGI & NGINX CONFIG
COPY ./nginx.conf /etc/nginx/nginx.conf
RUN mkdir -p /etc/nginx/sites-enabled
COPY ./bare /etc/nginx/sites-enabled/

# FLASK APP RUN
COPY ./bare_server /app
WORKDIR /app
RUN mkdir key
COPY ./key/bare_server.crt /app/key/
COPY ./key/bare_ssl.key /app/key/
CMD /usr/share/nginx/sbin/nginx && uwsgi --ini wsgi.ini
