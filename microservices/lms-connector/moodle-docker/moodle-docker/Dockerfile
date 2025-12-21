FROM php:8.2-apache

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    unzip git curl cron \
    libzip-dev libjpeg-dev libpng-dev libfreetype6-dev \
    libicu-dev libxml2-dev && \
    docker-php-ext-configure gd --with-freetype --with-jpeg && \
    docker-php-ext-install mysqli zip gd intl soap exif opcache && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN git clone git://git.moodle.org/moodle.git /tmp/moodle && \
    cd /tmp/moodle && \
    git branch --track MOODLE_500_STABLE origin/MOODLE_500_STABLE && \
    git checkout MOODLE_500_STABLE && \
    cp -rf ./* /var/www/html/ && \
    rm -rf /tmp/moodle

RUN echo "max_input_vars=5000" > /usr/local/etc/php/conf.d/moodle.ini && \
    echo "opcache.enable=1" >> /usr/local/etc/php/conf.d/moodle.ini

RUN mkdir -p /var/www/moodledata && \
    chown -R www-data:www-data /var/www && \
    chmod -R 755 /var/www

RUN echo "* * * * * www-data php /var/www/html/admin/cli/cron.php > /dev/null 2>&1"     > /etc/cron.d/moodle-cron && chmod 0644 /etc/cron.d/moodle-cron

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /var/www/html
EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
