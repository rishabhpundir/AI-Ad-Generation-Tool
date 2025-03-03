sudo ssh -i appnightly.pem ubuntu@IP_ADDRESS

sudo scp -i appnightly.pem nightlysql ubuntu@IP_ADDRESS:/home/ubuntu/

psql -d nightly -f /var/lib/PostgreSQL/nightlysql



# Setup gunicorn
sudo nano /etc/systemd/system/gunicorn.service

####
[Unit]
Description=gunicorn daemon for Django nightly API
After=network.target

[Service]
User=jenkins
Group=www-data
WorkingDirectory=/home/ubuntu/Nighly-Whats-Up
ExecStart=/home/ubuntu/venv/bin/gunicorn --workers 3 --bind unix:/PATH/TO/PROJECTNAME/projectname.sock nightly.wsgi:application

[Install]
WantedBy=multi-user.target
####

sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
#


# Setup Nginx 
sudo nano /etc/nginx/sites-available/nightly

####
server {
    listen 80;
    server_name IP_ADDRESS;

    location / {
        proxy_pass http://unix:/PATH/TO/PROJECTNAME/projectname.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /staticfiles/ {
        alias /home/ubuntu/Nighly-Whats-Up/staticfiles/;
        alias /home/ubuntu/Nighly-Whats-Up/staticfiles/
    }
}
####

sudo ln -s /etc/nginx/sites-available/nightly /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginxcat 
sudo ufw allow 'Nginx Full'
sudo systemctl restart gunicorn
sudo systemctl restart nginx
#



# Commands for file/folder permissions
sudo usermod -aG www-data ubuntu
# sudo chmod -R 770 /home/ubuntu/your-django-project/media
sudo chmod -R 770 /home/ubuntu/Nighly-Whats-Up/staticfiles
sudo chmod -R 750 /home/ubuntu/Nighly-Whats-Up
sudo chown -R ubuntu:www-data /home/ubuntu/Nighly-Whats-Up

######################### special commands ##########################
sudo chown ubuntu:www-data /home/ubuntu/Nighly-Whats-Up/nightly.sock
sudo chmod 660 /home/ubuntu/Nighly-Whats-Up/nightly.sock
sudo chown -R ubuntu:www-data /home/ubuntu/Nighly-Whats-Up
sudo chmod -R 750 /home/ubuntu/Nighly-Whats-Up
#####################################################################

sudo chown ubuntu:www-data /home/ubuntu/nightly.sock
sudo chmod 660 /home/ubuntu/nightly.sock
sudo chown -R ubuntu:www-data /home/ubuntu/
sudo chmod -R 750 /home/ubuntu/


sudo chown jenkins:jenkins /home/ubuntu/
sudo chmod 660 /home/ubuntu/nightly.sock
sudo chown -R jenkins:jenkins /home/ubuntu/
sudo chmod -R 750 /home/ubuntu/

# Settings for shared permissions ubuntu/jenkins
sudo usermod -aG www-data jenkins
sudo groupadd shared-group
sudo usermod -aG shared-group ubuntu
sudo usermod -aG shared-group jenkins
sudo chown -R ubuntu:www-data /home/ubuntu
sudo chown -R ubuntu:shared-group /home/ubuntu
sudo chmod -R 2775 /home/ubuntu
sudo find /home/ubuntu -type d -exec chmod g+s {} \;
ls -ld /home/ubuntu
ls -l /home/ubuntu
groups jenkins
groups ubuntu

sudo chown -R jenkins:shared-group /home/ubuntu/venv
#


## S3 media policy
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::nightlystorage/media/*"
        }
    ]
}

sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl restart nginx
