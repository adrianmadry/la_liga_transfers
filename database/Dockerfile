# Start with the official MySQL image
FROM mysql:latest

# Set environment variables for MySQL
ENV MYSQL_DATABASE=mydatabase
ENV MYSQL_USER=myuser
ENV MYSQL_PASSWORD=mypassword
ENV MYSQL_ROOT_PASSWORD=rootpassword

# Copy initialization files into the MySQL container's init directory
COPY init/init.sql /docker-entrypoint-initdb.d/
COPY init/merged_data_241004.csv /var/lib/mysql-files/

# Expose the default MySQL port
EXPOSE 3306
