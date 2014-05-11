#!/usr/bin/env python

import requests
import json
import urllib

headers = {'content-type': 'application/json'}

class ticket_poster:
    def __init__(self, redmine_data, new_user_data):
	self.redmine_data = redmine_data

	self.base_url = redmine_data["base_url"]
	self.project_name = redmine_data["project_name"]
	self.auth = redmine_data["auth"]

	self.new_user_data = new_user_data
	self.new_user_name = new_user_data["new_user_name"]
	self.new_user_extern_email = new_user_data["new_user_extern_email"]

    def redmine_get(self, url, **kwargs):
	return (requests.get(url, auth=self.auth, headers=headers, **kwargs))

    def get_project_id_by_name(self, project_name):
	url = self.base_url + '/projects/%s.json' % urllib.quote(project_name)
	r = self.redmine_get(url)
	try:
	    return int(r.json()["project"]["id"])
	except Exception as e:
	    print "Exception: url: %s http res: %s" % (url, r.text)
	    raise e

    def get_user_id_by_name(self, user_name):
	url = self.base_url + '/users.json'
	r = self.redmine_get(url, params= { "name": user_name })
	try:
	    for user in r.json()["users"]:
		if user["login"] == user_name:
		    return user["id"]
	    raise KeyError("no such user %s" % user_name)
	except Exception as e:
	    print "Exception: %s -> %s" % (url, r.text)
        raise e

    def get_tracker_id_by_name(self, tracker_name):
	r = self.redmine_get(self.base_url + '/trackers.json')
	for tracker in r.json()["trackers"]:
	    if tracker["name"] == tracker_name:
		return tracker["id"]
	raise KeyError("no such tracker %s" % tracker_name)

    def get_priority_id_by_name(self, priority_name):
	r = self.redmine_get(
		self.base_url + '/enumerations/issue_priorities.json')
	for issue in r.json()["issue_priorities"]:
	    if issue["name"] == priority_name:
		return issue["id"]
	raise KeyError("no such priority name '%s'" % priority_name)

    def ticket_url(self, ticket_id):
	return "%s/issues/%d" % (self.base_url, ticket_id)

    def post_ticket(self, user, subject, payload, body=""):
	payload["issue"]["subject"] = "onboard [%s] - %s" % (user, subject)
	payload["issue"]["description"] = body
	try:
	    r = requests.post(self.base_url + '/issues.json',
		auth=self.auth, headers=headers, data=json.dumps(payload))
	    the_id = r.json()["issue"]["id"]
	    print "Ticket %d created: %s" % (the_id, self.ticket_url(the_id))
	except Exception as e:
	    try:
		print "result code: %d -> %s" % (r.status_code, r.text)
	    except:
		raise e
	    raise e
	return the_id
