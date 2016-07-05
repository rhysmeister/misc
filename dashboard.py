#!/usr/bin/python

##      DashBoard version 0.0.1
## Custom view on certain service/host groups in Nagios
## - author: Franjo Stipanovic
## - date: 30.4.2007.
## ChangeLog:
## - added subgroups 5.5.2007.
## FixMe:

from configobj import ConfigObj
import cgi, os, sys, datetime, urlparse, glob

class Dashboard:
        def __init__(self, dashboard=None):
                # retrieve username from browser headers
                # user = os.getenv('REMOTE_USER')
                # RC Edit REMOTE_USER doesn't work,
                # plus it would be good to have more
                # than one custom dashboard per user
                # Will end up forking tihis...

                cfgdir = "/usr/share/nagios/html/dh/"
                datfile = "/var/log/nagios/status.dat"
                cfgfile = None

                #cfg = ConfigObj(cfgfile) Need to do this below...
                sys.stderr = sys.stdout

                # list for host and service status
                hStatus = ['statusHOSTUP','statusHOSTDOWN','statusHOSTUNREACHABLE','statusHOSTPENDING','white']
                sStatus = ['statusOK','statusWARNING','statusCRITICAL','statusUNKNOWN','statusPENDING','white']

                print "Content-type: text/html\n\n"
                print "<html><head><title></title>"

                # rc don't want this
                # user doesnt have cfg? show him form for creating dashboard
                #if os.path.exists(cfgfile) == False:
                 #       print "<h1 align=center>Welcome to DashBoard Nagios module</h1>"
                  #      print "First, you have to create your dashboard configuration:"
                   #     self.show_new_edit_form()
                    #    return

                url = os.environ["REQUEST_URI"]
                parsed = urlparse.urlparse(url)
                if urlparse.parse_qs(parsed.query).has_key('dashboard'):
                        selectedDashboard =  urlparse.parse_qs(parsed.query)['dashboard'][0]
                        cfgfile = cfgdir + selectedDashboard + ".cfg"
                        cfg = ConfigObj(cfgfile)
                else:
                        print "<table border=0 cellspacing=3 cellpadding=3>"
                        for file in glob.glob(cfgdir + "*.cfg"):
                                dashboardName = os.path.splitext(os.path.basename(file))[0]
                                print "<tr><td><a href='/nagios/cgi-bin/dashboard.py?dashboard=" + dashboardName + "' target='_self'>" + dashboardName + "</a></td></tr>"
                        print "</table></body></html>"
                        return


                # basic html headers - included 60 sec refresh
                print "<meta http-equiv='refresh' content='60'>"
                print "<link rel=stylesheet type=text/css href=/nagios/stylesheets/common.css>"
                print "<link rel=stylesheet type=text/css href=/nagios/stylesheets/dashboard.css>"
                print "</head>"
                print "<body>"

                print "System time: " + datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p") + "<br>"
                print "Updated every 60 seconds" + "<br>"

                if os.path.exists(datfile) == False:
                        print "Error, please check datfile parameter"
                        return

                self.infile = open(datfile, "r")

                totalOK = 0
                totalNOK = 0
                print "<table border=0 cellpadding=3 cellspacing=2><tr>"
                # look for hosts and services status
                for i, val in enumerate(cfg):
                        if i % 2 == 0:
                                print "</tr><tr><td valign=top>"
                        else:
                                print "<td valign=top>"
                        print "<table class=tbl align=center border=0 cellpadding=3 cellspacing=2>\
                                <tr><td class=status colspan=4>%s</td></tr><tr>" % val
                        totalOK = totalNOK = 0
                        for idx, v in enumerate(cfg[val]['members']):
                                # reset file cursor
                                self.infile.seek(0)
                                style = target = ''
                                if v.find(':') == -1:
                                        status = self.find_host_status(v.strip())
                                        if status != '4':
                                                target = "<a href='extinfo.cgi?type=1&host=%s'>%s</a>" \
                                                        % (v.strip(), v.strip())
                                        else:
                                                target = v.strip()
                                        style = hStatus[int(status)]
                                        if status != '0':
                                                totalNOK += 1
                                        else:
                                                totalOK += 1
                                else:
                                        status = self.find_service_status(v.split(':')[0].strip(),
                                                        v.split(':')[1].strip())
                                        if status != '5':
                                                target = "<a href='extinfo.cgi?type=2&host=%s&service=%s'>%s</a>" \
                                                        % (v.split(':')[0].strip(), v.split(':')[1].strip(),
                                                        v.split(':')[1].strip())
                                        else:
                                                target = v.strip()
                                        style = sStatus[int(status)]
                                        if status != '0':
                                                totalNOK += 1
                                        else:
                                                totalOK += 1
                                if idx % 4 == 0:
                                        print "</tr><tr><td class=%s>%s</td>" % (style, target)
                                else:
                                        print "<td class=%s>%s</td>" % (style, target)
                        # do we have subgroups?
                        if len(cfg[val].keys()) > 1:
                                for idxj, j in enumerate(cfg[val].keys()[1:]):
                                        # reset number of failed members
                                        num_failed = 0
                                        # special flag is unknown member found
                                        # probably mistyped in configuration
                                        # mark whole subgroup as white if one unknown found
                                        num_unknown = 0
                                        # to which service group this belongs?
                                        group = cfg[val][j]['group'].strip()
                                        # loop thru members in subgroup
                                        for idx, k in enumerate(cfg[val][j]['members']):
                                                self.infile.seek(0)
                                                style = target = ''
                                                # is it host?
                                                if k.find(':') == -1:
                                                        status = self.find_host_status(k.strip())
                                                        if status != '0':
                                                                if status == '4':
                                                                        num_unknown += 1
                                                                num_failed += 1
                                                else:
                                                        status = self.find_service_status(k.split(':')[0].strip(),
                                                                        k.split(':')[1].strip())
                                                        if status != '0':
                                                                if status == '5':
                                                                        num_unknown += 1
                                                                num_failed += 1
                                        if num_failed > 0:
                                                totalNOK += 1
                                                # did they all failed?
                                                if len(cfg[val][j]['members']) == num_failed:
                                                        style = sStatus[2] # critical status
                                                else:
                                                        style = sStatus[1] # warning status
                                                # was there any unknown member?
                                                if num_unknown > 0:
                                                        style = sStatus[5] # give white color
                                        else:
                                                totalOK += 1
                                                style = sStatus[0]
                                        if idxj % 4 == 0:
                                                print "</tr><tr><td class=%s><a href='status.cgi?hostgroup\
                                                                =%s&style=detail'>%s</a></td>" % (style, group, j)
                                        else:
                                                print "<td class=%s><a href='status.cgi?hostgroup\
                                                                =%s&style=detail'>%s</a></td>" % (style, group, j)
                        print "<tr><td colspan=4 class=white>Total OK:" + str(totalOK) + "&nbsp;&nbsp;" \
                                "Total NOK:" + str(totalNOK) + "</td></tr>"
                        print "</table><br><br></td>"
                print "</table>"
                print "</body></html>"

        """
                look for has_been_checked param
                it shows if service/host has pending status
        """
        def look_pending(self):
                while 1:
                        line = self.infile.readline().strip()
                        if line == "}":
                                break
                        param = line.split("=")[0]
                        if param == "has_been_checked":
                                checked = line[17:]
                                return checked

        """
                look for current_state param and return it
                used in service and host checks
        """
        def look_status(self):
                while 1:
                        line = self.infile.readline().strip()
                        if line == "}":
                                break
                        param = line.split("=")[0]
                        if param == "current_state":
                                current_state = line[14:]
                                return current_state
        """
                host - host_name
                service - service_description
                together they represent unique combination in nagios
        """
        def find_service_status(self, host, service):
                while 1:
                        line = self.infile.readline()
                        if line == "":
                                break
                        if line[:7] == "service":  # start of object
                                # points to host_name
                                line = self.infile.readline().strip()
                                if (line[10:] == host): # our host?
                                        # points to service_description
                                        line = self.infile.readline().strip()
                                        if (line[20:] == service): # our service?
                                                checked = self.look_pending()
                                                if checked == '0': # has pending status
                                                        return '4'
                                                state = self.look_status()
                                                return state
                return '5' # host not found

        """
                host - host_name
        """
        def find_host_status(self, host):
                while 1:
                        line = self.infile.readline()
                        if line == "":
                                break
                        if line[:4] == "host":
                                # points to host_name
                                line = self.infile.readline().strip()
                                if (line[10:] == host): # our host?
                                        checked = self.look_pending()
                                        if checked == '0': # has pending status
                                                return '3'
                                        state = self.look_status()
                                        return state
                return '4' # host not found

        """
                display form for creating dashboard when user doesn't have cfg file
        """
        def show_new_edit_form(self):
                print "<form action='dashboard_save_cfg.py' method='post'>"
                print "<textarea rows='25' cols='75' name='cfg'>"
                print "#\n# Example configuration (this is comment)\n#\n"
                print "[Google Servers]"
                print "members=google_ftp, google_http, google_smtp"
                print "</textarea>"
                print "<br><input type='submit' value='Submit'>"
                print "</form>"

dashboard = Dashboard()
