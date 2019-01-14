bundle exec jekyll build
rm -r /var/www/andrewkhill.com/public_html/*
cp -r _site/* /var/www/andrewkhill.com/public_html/
