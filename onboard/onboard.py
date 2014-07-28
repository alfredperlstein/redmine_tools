#!/usr/bin/env python

##### README ####
# Script to make onboarding tickets in redmine
# from: http://redmine.norse-data.com/projects/norse-appliance/wiki/On_boarding
#
# Author: Alfred Perlstein

# who watches all the onboarding tickets (redmine login names)
watcher_list = []  # ["ap"]

# Redmine project that new hire tickets go under.
project_name = "ops"

# base URL to access redmine API
base_url = 'http://redmine.yourcompany.com'

# this program supports a config file syntax to pass the http password
# in as you should never pass a password via command line.
# put inside a file (auth.txt) this:
#
# --redmine-http-auth-pass
# alfred
# --redmine-http-auth-user
# 6234f7.this.is.your.auth.key.32
#
# Then pass that file to the program like so:
# python onboard.py @auth.txt
#
##### END #####

import argparse
import datetime
import redmine_rest

def do_config():
    import argparse
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("--hire-full-name", 
			help="new hire's full name")
    parser.add_argument("--hire-extern-email",
			help="new hire's external email")
    parser.add_argument("-v", "--verbose", action="store_true",
			help="increase output verbosity")
    parser.add_argument("--redmine-api-url", default=base_url,
			help="url to redmine base url")
    parser.add_argument("--redmine-project", default=project_name,
			help="project in which tickets are made")
    parser.add_argument("--redmine-tracker", default="Support",
			help="project in which tickets are made")
    parser.add_argument("--redmine-http-auth-user",
			help="username for http auth to redmine")
    parser.add_argument("--redmine-http-auth-pass",
			help="password for http auth to redmine")
    parser.add_argument("--redmine-hiring-manager",
			help="whom to assign the main ticket")
    parser.add_argument("--redmine-watchers",
			help="who else to watch the tickets")
    parser.add_argument("--all-tickets-to-manager", action="store_true",
	    default=False,
			help="send ALL tickets to manager")
    parser.add_argument("--config-file",
			help="specify config file")
    parser.add_argument("--assign-all-to-user",
			help="override ticket assignment to a single redmine" +
			    "user")
    return parser.parse_args()

    
args = do_config()

base_url = args.redmine_api_url
project_name = args.redmine_project

rm = redmine_rest.ticket_poster(
	redmine_data={
	    "base_url": base_url,
	    "project_name": project_name,
	    "auth": (args.redmine_http_auth_user,
			args.redmine_http_auth_pass)
	    },
	new_user_data = {
	    "new_user_name" : args.hire_full_name,
	    "new_user_extern_email" : args.hire_extern_email
	    }
	)


hiring_manager = args.redmine_hiring_manager
user_id = rm.get_user_id_by_name(hiring_manager)
support_id = rm.get_tracker_id_by_name(args.redmine_tracker)
proj_id = rm.get_project_id_by_name(args.redmine_project)

new_user_name = args.hire_full_name
new_user_extern_email = args.hire_extern_email

# When testing, it's useful not to annoy everyone so we
# can set the hiring manager to someone and send ALL tickets
# to them.
if args.all_tickets_to_manager:
    alfred_account = hiring_manager
    tom_account = hiring_manager
    hil_account = hiring_manager
else:
    alfred_account = "ap"
    tom_account = "tgs"
    hil_account = "hb"


# Alfred watches all.
watcher_ids = []
for watcher in watcher_list:
    watcher_ids.append(get_user_id_by_name(watcher))

# 5 days from now..
onboarding_sla_days = 5
due_date_str = (datetime.datetime.now() +
	    datetime.timedelta(days=onboarding_sla_days)).strftime("%Y-%m-%d")

issue_template = {
        "project_id" : proj_id,
        "assigned_to_id" : user_id,
        "tracker_id": support_id,
        "subject": "Onboarding %s" % new_user_name,
        "description": "This is the main ticket to onboard %s" % new_user_name,
        #parent_issue_id - ID of the parent issue
	"watcher_user_ids": watcher_ids,
	"due_date": due_date_str
}

payload = {
    "issue" : issue_template
}

print "Posting main issue:"
main_issue_id = rm.post_ticket(user=new_user_name,
	subject="Onboarding %s" % new_user_name,
	payload=payload,
	body="This is the main ticket to onboard %s" % new_user_name)

print "Posting sub issues..."

# set up the parent issue.
issue_template["parent_issue_id"] = main_issue_id

# Alfred Tickets
issue_template["assigned_to_id"] = rm.get_user_id_by_name(alfred_account)
rm.post_ticket(user=new_user_name, subject="get ssh pub key",
    payload=payload)
rm.post_ticket(user=new_user_name, subject="build1 login",
    payload=payload)
rm.post_ticket(user=new_user_name, subject="build1 add to 'dev' unix group",
    payload=payload)
rm.post_ticket(user=new_user_name, subject="build2 login",
    payload=payload)
rm.post_ticket(user=new_user_name, subject="redmine login",
    payload=payload)
rm.post_ticket(user=new_user_name,
    subject="add redmine user to 'appliance' group", payload=payload)
rm.post_ticket(user=new_user_name,
    subject="add username/email to committers.lst",
    body="Add username and email to build:/freenas-build/freenas.git/hooks/committers.lst",
    payload=payload)

# Hil tickets
issue_template["assigned_to_id"] = rm.get_user_id_by_name(hil_account)
rm.post_ticket(user=new_user_name,
    subject="buy hardware",
    body="""1 macbook pro 16GB memory
    keyboard
    LCD
    thunderbolt dock
    apple trackpad""", payload=payload)
rm.post_ticket(user=new_user_name,
    subject="get office front door keys", payload=payload)
rm.post_ticket(user=new_user_name,
    subject="get building keys", payload=payload)
rm.post_ticket(user=new_user_name,
    subject="create zimbra account",
    body="outside email is: %s" % new_user_extern_email, payload=payload)

# Tom tickets
issue_template["assigned_to_id"] = rm.get_user_id_by_name(tom_account)
rm.post_ticket(user=new_user_name,
    subject="create vpn keys",
    body="", payload=payload)
rm.post_ticket(user=new_user_name,
    subject="LDAP account setup",
    body="", payload=payload)
rm.post_ticket(user=new_user_name,
    subject="NFS home directory setup",
    body="", payload=payload)

print "Done posting sub issues..."
print "Main issue: %d - %s/issues/%d" % (main_issue_id, base_url, main_issue_id)
print "Done."
