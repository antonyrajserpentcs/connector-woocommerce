.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Woocommerce Connector
=====================

Features
--------

**Helps to import and export the Woocommerce records such as below**
	* Product's Categeries
	* Products
	* Customers
	* Sale Orders

Configuration
-------------

**Get Access From Woocommerce**
    * Get the URL, Consumer key and Consuemer Secret key of esatblished store.

**Set Access in Odoo**
    * Configure Woocommerce access at Odoo Connector Backend.

**Run the Odoo server as below**
	* Set the following environment variables:
	  - ``ODOO_CONNECTOR_CHANNELS=root:4`` (or any other channels configuration)
	  - optional if ``xmlrpc_port`` is not set: ``ODOO_CONNECTOR_PORT=8069``

	* Start Odoo with ``--load=web,web_kanban,queue_job``
	  and ``--workers`` greater than 1.

	* Confirm the runner is starting correctly by checking the odoo log file:
	.. code-block:: none
	  ...INFO...connector.jobrunner.runner: starting
	  ...INFO...connector.jobrunner.runner: initializing database connections
	  ...INFO...connector.jobrunner.runner: connector runner ready for db <dbname>
	  ...INFO...connector.jobrunner.runner: database connections ready

	* Study the document for further.
	   :target: http://odoo-connector.com/guides/jobrunner.html#how-to-use-it
	   :alt: Odoo Connector

**Configuration of Apache(Only for Woocommerce Store configuration)**
	* Skip this step, if you are not configuring Woocommerce store.
	* sudo a2enmod rewrite
	* touch /etc/apache2/sites-available/woocommerce.conf
	* ln -s /etc/apache2/sites-available/woocommerce.conf /etc/apache2/sites-enabled/woocommerce.conf
	* nano /etc/apache2/sites-available/woocommerce.conf
	* Add the following lines:
		<VirtualHost *:80>
		ServerAdmin admin@yourdomain.com
		DocumentRoot "/var/www/html/"
		ServerName your-domain.com
		ServerAlias www.your-domain.com
		<Directory "/var/www/html/">
		Options FollowSymLinks
		AllowOverride All
		Order allow,deny
		allow from all
		</Directory>
		ErrorLog /var/log/apache2/error_log_file.log
		CustomLog /var/log/apache2/access_log_file.log common
		</VirtualHost>
	* systemctl restart apache2.service

**Test Connection and Import**
	* Check the connection.
	* Import or Export the Product's Categories, Products, Customers and Sale Orders.
	* Trace the jobs.
	* Verify checkpoints.


Contributors
------------

* Tech-Receptives Solutions <https://techreceptives.com/>
* Serpent Consulting Services Pvt. Ltd.<http://www.serpentcs.com/>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.

