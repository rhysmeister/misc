# misc
Various little bits and pieces

dashboard.py
===============

Forked version of https://exchange.nagios.org/directory/Addons/Frontends-%28GUIs-and-CLIs%29/Web-Interfaces/DashBoard/details

Custom dashbaord for Nagios. os.getenv('REMOTE_USER') didn't work for me and I didn't want dashboard to be user centred anyway.
 
Follow the instructions as normal in https://exchange.nagios.org/components/com_mtree/attachment.php?link_id=61&cf_id=29

The replace the version of dashboard.py with this one. This version displays a list of available dashboard that will be the same for all users. I have removed the ability to add / edit custom dashboard from the Nagios interface. If no dashbaord is provided by the url we simply display a list of available dashbaord by reading the filename in the dashboard configuration directory.

Variables you probably need to change in dashboard.py

cfgdir - Set to where your dashboard configuration files are (.cfg extension, others are ignored)
datfile = Nagios status file. WHere the important status details are obtained.
dashboard_home_link