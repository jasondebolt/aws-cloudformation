import ec2_header
from troposphere import Ref, Template
from troposphere.ec2 import SecurityGroup


t = Template()
t.add_version("2010-09-09")
t.add_description("Create an EC2 instance which automatically bootstraps a Chef node using Chef unattended installs.")
t = ec2_header.setEc2Header(t)

InstanceSecurityGroup = t.add_resource(SecurityGroup(
    "InstanceSecurityGroup",
    SecurityGroupIngress=[{ "ToPort": "22", "IpProtocol": "tcp", "CidrIp": Ref(t.parameters['SSHLocation']), "FromPort": "22" }],
    GroupDescription="Enable SSH access via port 22",
))

print(t.to_json())
