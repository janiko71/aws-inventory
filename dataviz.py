import config
import json
import pprint

file_name_in  = config.filepath + "AWS_343017904322_20180823075335.json"
file_name_out = "net.json"

with open(file_name_in, "r") as f:
    inventory = f.read()

json_inventory = json.loads(inventory)
filtered_inventory = json.loads(inventory)

# Data cleaning
# Tricky : default VPC are removed if unusued.
vpc_list = []

for ec2_group in inventory["ec2"]:
    for ec2 in ec2_group["Instances"]:
        vpc_list.append(ec2["VpcId"])

inventory["ec2-vpcs"] = []
for vpc in config.global_inventory["ec2-vpcs"]:
    if (vpc['VpcId'] in vpc_list):
        inventory["ec2-vpcs"].append(vpc)


# Graph creating

network = {
    "nodes": [],
    "edges": [],
}
region_color = {}
for region in config.regions:
    region_name = region['RegionName']
    color = region['color']
    region_color[region_name] = color

for reservation in json_inventory['ec2']:
    rid = reservation['ReservationId']
    region_name = reservation['RegionName']
    for instance in reservation['Instances']:
        iid = instance['InstanceId']
        vpcid = instance['VpcId']
        network["nodes"].append({
            "id": iid,
            "label": "*ec2*\n_"+iid+"_",
            "caption": "" + rid + "\n" + region_name,
            "color": region_color[region_name],
            "font" : {
                "multi": "md",
            },
        })
        # VPC
        print(iid, vpcid)
        network["edges"].append({
            "from": iid,
            "to": vpcid,
            "font" : {
                "multi": "md",
            }
        })
        # Security Groups
        for sg in instance['SecurityGroups']:
            print(iid, sg['GroupId'])
            network["edges"].append({
                "from": iid,
                "to": sg['GroupId'],
                "font" : {
                    "multi": "md",
                }
            })
        # EBS
        for ebs in instance['BlockDeviceMappings']:
            print(iid, sg['GroupId'])
            network["edges"].append({
                "from": iid,
                "to": ebs['Ebs']['VolumeId'],
                "font" : {
                    "multi": "md",
                }
            })


for vpc in json_inventory['ec2-vpcs']:
    vpcid = vpc['VpcId']
    network["nodes"].append({
        "id": vpcid,
        "label": vpcid,
        "color": region_color[region_name],        
        "font" : {
            "multi": "md",
        },            
    })

for sg in json_inventory['ec2-security-groups']:
    gid = sg['GroupId']
    network["nodes"].append({
        "id": gid,
        "label": "*" + gid + "*" + "\n" + sg['GroupName'],
        "font" : {
            "multi": "md",
        },            
    })


for ebs in json_inventory['ec2-ebs']:
    vid = ebs['VolumeId']
    encrypt ="uncrypt."
    if ebs['Encrypted']:
        encrypt = "encrypt."
    network["nodes"].append({
        "id": vid,
        "label": "*" + vid + "*" + "\n" + str(ebs['Size']) + "Go/" + encrypt + "(" + ebs['State'] + ")",
        "font" : {
            "multi": "md",
        },            
    })

try:
    f = open(file_name_out, "w+")
except IOError as e:
    config.logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))

#f.write(str(network))
f.write(json.JSONEncoder().encode(network))

f.close()
    