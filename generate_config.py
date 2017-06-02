#!/bin/python

import sys
import urllib2, json, yaml

if len(sys.argv) < 2:
	print "Url arg required"
	exit(1)

url = sys.argv[1]
body = urllib2.urlopen(url).read()

report = json.loads(body)
out = [] 

def parse_metric(group_name, path_pattern, m, out):
	if "items" in m:
		return
	name = m["name"]
	clean_name = name.replace('-', '_').replace('.', '_') 
	kind = ""
	if "kind" in m:
		kind = m["kind"]
	values = {}
	if "value" in m:
		values["value"] = "$.value" 

	labels = {"kind": kind, "units": m["units"], "group": group_name}
	if kind == "HISTOGRAM":
                for k in ["25th %-ile", "50th %-ile", "75th %-ile", "90th %-ile", "95th %-ile", "99.9th %-ile", "count"]:
			safe_key = k.replace(" %-ile", "_percentile").replace(".", "")
			values[safe_key] = m[k]
		
	try:
		obj = {
			"name": clean_name,
			"type": "object",
			"path": path_pattern % name,
			"labels": labels, 
			"help": m["description"],
			"values": values 
		}
	except KeyError as e:
		print e
		print m

	out.append(obj)
	return

for m in report["metric_group"]["metrics"]:
	group_name = report["metric_group"]["name"]
	parse_metric(group_name, '$.metric_group.metrics[*]?(@.name == "%s")', m, out) 

for index, g in enumerate(report["metric_group"]["child_groups"]):
	group_name = g["name"]
	for subindex, m in enumerate(g["metrics"]):
		#this doesn't work due to bug in jsonpath library. It just matches first metrics item with expression and ignores the rest
                #so we need to find metrics item by index and match by name just in case
		#parse_metric(group_name, '$.metric_group.child_groups[%d].metrics[*]?(@.name == "%%s")' % index, m, out) 
		parse_metric(group_name, '$.metric_group.child_groups[%d].metrics[%d]?(@.name == "%%s")' % (index, subindex), m, out) 

print yaml.safe_dump(out, default_flow_style = False)
