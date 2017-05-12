from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output, If, And, Not, Or, Equals, Condition
from troposphere import Parameter, Ref, Tags, Template
from troposphere.cloudformation import Init
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.ec2 import PortRange
from troposphere.iam import Role
from troposphere.ec2 import SecurityGroup
from troposphere.logs import LogGroup
from troposphere.iam import InstanceProfile
from troposphere.ec2 import Instance, NetworkInterfaceProperty, PrivateIpAddressSpecification


t = Template()

t.add_version("2010-09-09")

t.add_description("""\
AWS CloudFormation template to do bootstrap Chef nodes.""")
SSHLocation = t.add_parameter(Parameter(
    "SSHLocation",
    ConstraintDescription="must be a valid IP CIDR range of the form x.x.x.x/x.",
    Description=" The IP address range that can be used to SSH to the EC2 instances",
    Default="0.0.0.0/0",
    MinLength="9",
    AllowedPattern="(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})/(\\d{1,2})",
    MaxLength="18",
    Type="String",
))

KeyName = t.add_parameter(Parameter(
    "KeyName",
    ConstraintDescription="must be the name of an existing EC2 KeyPair.",
    Type="AWS::EC2::KeyPair::KeyName",
    Description="Name of an existing EC2 KeyPair to enable SSH access to the instance",
))

InstanceType = t.add_parameter(Parameter(
    "InstanceType",
    Default="t2.micro",
    ConstraintDescription="must be a valid EC2 instance type.",
    Type="String",
    Description="EC2 Instance Size",
    AllowedValues=["t1.micro", "t2.nano", "t2.micro", "t2.small", "t2.medium", "t2.large", "m1.small", "m1.medium", "m1.large", "m1.xlarge", "m2.xlarge", "m2.2xlarge", "m2.4xlarge", "m3.medium", "m3.large", "m3.xlarge", "m3.2xlarge", "m4.large", "m4.xlarge", "m4.2xlarge", "m4.4xlarge", "m4.10xlarge", "c1.medium", "c1.xlarge", "c3.large", "c3.xlarge", "c3.2xlarge", "c3.4xlarge", "c3.8xlarge", "c4.large", "c4.xlarge", "c4.2xlarge", "c4.4xlarge", "c4.8xlarge", "g2.2xlarge", "g2.8xlarge", "r3.large", "r3.xlarge", "r3.2xlarge", "r3.4xlarge", "r3.8xlarge", "i2.xlarge", "i2.2xlarge", "i2.4xlarge", "i2.8xlarge", "d2.xlarge", "d2.2xlarge", "d2.4xlarge", "d2.8xlarge", "hi1.4xlarge", "hs1.8xlarge", "cr1.8xlarge", "cc2.8xlarge", "cg1.4xlarge"],
))

t.add_mapping("Region2Principal",
{u'ap-northeast-1': {u'EC2Principal': u'ec2.amazonaws.com',
                     u'OpsWorksPrincipal': u'opsworks.amazonaws.com'},
 u'ap-northeast-2': {u'EC2Principal': u'ec2.amazonaws.com',
                     u'OpsWorksPrincipal': u'opsworks.amazonaws.com'},
 u'ap-south-1': {u'EC2Principal': u'ec2.amazonaws.com',
                 u'OpsWorksPrincipal': u'opsworks.amazonaws.com'},
 u'ap-southeast-1': {u'EC2Principal': u'ec2.amazonaws.com',
                     u'OpsWorksPrincipal': u'opsworks.amazonaws.com'},
 u'ap-southeast-2': {u'EC2Principal': u'ec2.amazonaws.com',
                     u'OpsWorksPrincipal': u'opsworks.amazonaws.com'},
 u'cn-north-1': {u'EC2Principal': u'ec2.amazonaws.com.cn',
                 u'OpsWorksPrincipal': u'opsworks.amazonaws.com.cn'},
 u'eu-central-1': {u'EC2Principal': u'ec2.amazonaws.com',
                   u'OpsWorksPrincipal': u'opsworks.amazonaws.com'},
 u'eu-west-1': {u'EC2Principal': u'ec2.amazonaws.com',
                u'OpsWorksPrincipal': u'opsworks.amazonaws.com'},
 u'sa-east-1': {u'EC2Principal': u'ec2.amazonaws.com',
                u'OpsWorksPrincipal': u'opsworks.amazonaws.com'},
 u'us-east-1': {u'EC2Principal': u'ec2.amazonaws.com',
                u'OpsWorksPrincipal': u'opsworks.amazonaws.com'},
 u'us-west-1': {u'EC2Principal': u'ec2.amazonaws.com',
                u'OpsWorksPrincipal': u'opsworks.amazonaws.com'},
 u'us-west-2': {u'EC2Principal': u'ec2.amazonaws.com',
                u'OpsWorksPrincipal': u'opsworks.amazonaws.com'}}
)

t.add_mapping("Region2ARNPrefix",
{u'ap-northeast-1': {u'ARNPrefix': u'arn:aws:'},
 u'ap-northeast-2': {u'ARNPrefix': u'arn:aws:'},
 u'ap-south-1': {u'ARNPrefix': u'arn:aws:'},
 u'ap-southeast-1': {u'ARNPrefix': u'arn:aws:'},
 u'ap-southeast-2': {u'ARNPrefix': u'arn:aws:'},
 u'cn-north-1': {u'ARNPrefix': u'arn:aws-cn:'},
 u'eu-central-1': {u'ARNPrefix': u'arn:aws:'},
 u'eu-west-1': {u'ARNPrefix': u'arn:aws:'},
 u'sa-east-1': {u'ARNPrefix': u'arn:aws:'},
 u'us-east-1': {u'ARNPrefix': u'arn:aws:'},
 u'us-west-1': {u'ARNPrefix': u'arn:aws:'},
 u'us-west-2': {u'ARNPrefix': u'arn:aws:'}}
)

t.add_mapping("AWSInstanceType2Arch",
{u'c1.medium': {u'Arch': u'PV64'},
 u'c1.xlarge': {u'Arch': u'PV64'},
 u'c3.2xlarge': {u'Arch': u'HVM64'},
 u'c3.4xlarge': {u'Arch': u'HVM64'},
 u'c3.8xlarge': {u'Arch': u'HVM64'},
 u'c3.large': {u'Arch': u'HVM64'},
 u'c3.xlarge': {u'Arch': u'HVM64'},
 u'c4.2xlarge': {u'Arch': u'HVM64'},
 u'c4.4xlarge': {u'Arch': u'HVM64'},
 u'c4.8xlarge': {u'Arch': u'HVM64'},
 u'c4.large': {u'Arch': u'HVM64'},
 u'c4.xlarge': {u'Arch': u'HVM64'},
 u'cc2.8xlarge': {u'Arch': u'HVM64'},
 u'cr1.8xlarge': {u'Arch': u'HVM64'},
 u'd2.2xlarge': {u'Arch': u'HVM64'},
 u'd2.4xlarge': {u'Arch': u'HVM64'},
 u'd2.8xlarge': {u'Arch': u'HVM64'},
 u'd2.xlarge': {u'Arch': u'HVM64'},
 u'g2.2xlarge': {u'Arch': u'HVMG2'},
 u'g2.8xlarge': {u'Arch': u'HVMG2'},
 u'hi1.4xlarge': {u'Arch': u'HVM64'},
 u'hs1.8xlarge': {u'Arch': u'HVM64'},
 u'i2.2xlarge': {u'Arch': u'HVM64'},
 u'i2.4xlarge': {u'Arch': u'HVM64'},
 u'i2.8xlarge': {u'Arch': u'HVM64'},
 u'i2.xlarge': {u'Arch': u'HVM64'},
 u'm1.large': {u'Arch': u'PV64'},
 u'm1.medium': {u'Arch': u'PV64'},
 u'm1.small': {u'Arch': u'PV64'},
 u'm1.xlarge': {u'Arch': u'PV64'},
 u'm2.2xlarge': {u'Arch': u'PV64'},
 u'm2.4xlarge': {u'Arch': u'PV64'},
 u'm2.xlarge': {u'Arch': u'PV64'},
 u'm3.2xlarge': {u'Arch': u'HVM64'},
 u'm3.large': {u'Arch': u'HVM64'},
 u'm3.medium': {u'Arch': u'HVM64'},
 u'm3.xlarge': {u'Arch': u'HVM64'},
 u'm4.10xlarge': {u'Arch': u'HVM64'},
 u'm4.2xlarge': {u'Arch': u'HVM64'},
 u'm4.4xlarge': {u'Arch': u'HVM64'},
 u'm4.large': {u'Arch': u'HVM64'},
 u'm4.xlarge': {u'Arch': u'HVM64'},
 u'r3.2xlarge': {u'Arch': u'HVM64'},
 u'r3.4xlarge': {u'Arch': u'HVM64'},
 u'r3.8xlarge': {u'Arch': u'HVM64'},
 u'r3.large': {u'Arch': u'HVM64'},
 u'r3.xlarge': {u'Arch': u'HVM64'},
 u't1.micro': {u'Arch': u'PV64'},
 u't2.large': {u'Arch': u'HVM64'},
 u't2.medium': {u'Arch': u'HVM64'},
 u't2.micro': {u'Arch': u'HVM64'},
 u't2.nano': {u'Arch': u'HVM64'},
 u't2.small': {u'Arch': u'HVM64'}}
)

t.add_mapping("AWSRegionArch2AMI",
{u'ap-northeast-1': {u'HVM64': u'ami-374db956',
                     u'HVMG2': u'ami-e0ee1981',
                     u'PV64': u'ami-3e42b65f'},
 u'ap-northeast-2': {u'HVM64': u'ami-2b408b45',
                     u'HVMG2': u'NOT_SUPPORTED',
                     u'PV64': u'NOT_SUPPORTED'},
 u'ap-south-1': {u'HVM64': u'ami-ffbdd790',
                 u'HVMG2': u'ami-f5b2d89a',
                 u'PV64': u'NOT_SUPPORTED'},
 u'ap-southeast-1': {u'HVM64': u'ami-a59b49c6',
                     u'HVMG2': u'ami-0cb5676f',
                     u'PV64': u'ami-df9e4cbc'},
 u'ap-southeast-2': {u'HVM64': u'ami-dc361ebf',
                     u'HVMG2': u'ami-a71c34c4',
                     u'PV64': u'ami-63351d00'},
 u'cn-north-1': {u'HVM64': u'ami-8e6aa0e3',
                 u'HVMG2': u'NOT_SUPPORTED',
                 u'PV64': u'ami-77559f1a'},
 u'eu-central-1': {u'HVM64': u'ami-ea26ce85',
                   u'HVMG2': u'ami-7f04ec10',
                   u'PV64': u'ami-6527cf0a'},
 u'eu-west-1': {u'HVM64': u'ami-f9dd458a',
                u'HVMG2': u'ami-b9bd25ca',
                u'PV64': u'ami-4cdd453f'},
 u'sa-east-1': {u'HVM64': u'ami-6dd04501',
                u'HVMG2': u'NOT_SUPPORTED',
                u'PV64': u'ami-1ad34676'},
 u'us-east-1': {u'HVM64': u'ami-6869aa05',
                u'HVMG2': u'ami-2e5e9c43',
                u'PV64': u'ami-2a69aa47'},
 u'us-west-1': {u'HVM64': u'ami-31490d51',
                u'HVMG2': u'ami-fd76329d',
                u'PV64': u'ami-a2490dc2'},
 u'us-west-2': {u'HVM64': u'ami-7172b611',
                u'HVMG2': u'ami-83b770e3',
                u'PV64': u'ami-7f77b31f'}}
)

LogRole = t.add_resource(Role(
    "LogRole",
    Path="/",
    Policies=[{ "PolicyName": "LogRolePolicy", "PolicyDocument": { "Version": "2012-10-17", "Statement": [{ "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents", "logs:DescribeLogStreams"], "Resource": [Join("", [FindInMap("Region2ARNPrefix", Ref("AWS::Region"), "ARNPrefix"), "logs:*:*:*"])], "Effect": "Allow" }] } }],
    AssumeRolePolicyDocument={ "Version": "2012-10-17", "Statement": [{ "Action": ["sts:AssumeRole"], "Effect": "Allow", "Principal": { "Service": [FindInMap("Region2Principal", Ref("AWS::Region"), "EC2Principal")] } }] },
))

InstanceSecurityGroup = t.add_resource(SecurityGroup(
    "InstanceSecurityGroup",
    SecurityGroupIngress=[{ "ToPort": "22", "IpProtocol": "tcp", "CidrIp": Ref(SSHLocation), "FromPort": "22" }],
    GroupDescription="Enable SSH access via port 22",
))

CloudFormationLogs = t.add_resource(LogGroup(
    "CloudFormationLogs",
    RetentionInDays=7,
))

LogRoleInstanceProfile = t.add_resource(InstanceProfile(
    "LogRoleInstanceProfile",
    Path="/",
    Roles=[Ref(LogRole)],
))

ChefNodeInstance = t.add_resource(Instance(
    "ChefNodeInstance",
    Metadata=Init(
        { "InstallLogs": { "files": { "/etc/awslogs/awscli.conf": { "content": Join("", ["[plugins]\n", "cwlogs = cwlogs\n", "[default]\n", "region = ", Ref("AWS::Region"), "\n"]), "owner": "root", "group": "root", "mode": "000444" }, "/etc/awslogs/awslogs.conf": { "content": Join("", ["[general]\n", "state_file= /var/awslogs/state/agent-state\n", "[/var/log/cloud-init.log]\n", "file = /var/log/cloud-init.log\n", "log_group_name = ", Ref(CloudFormationLogs), "\n", "log_stream_name = {instance_id}/cloud-init.log\n", "datetime_format = \n", "[/var/log/cloud-init-output.log]\n", "file = /var/log/cloud-init-output.log\n", "log_group_name = ", Ref(CloudFormationLogs), "\n", "log_stream_name = {instance_id}/cloud-init-output.log\n", "datetime_format = \n", "[/var/log/cfn-init.log]\n", "file = /var/log/cfn-init.log\n", "log_group_name = ", Ref(CloudFormationLogs), "\n", "log_stream_name = {instance_id}/cfn-init.log\n", "datetime_format = \n", "[/var/log/cfn-hup.log]\n", "file = /var/log/cfn-hup.log\n", "log_group_name = ", Ref(CloudFormationLogs), "\n", "log_stream_name = {instance_id}/cfn-hup.log\n", "datetime_format = \n", "[/var/log/cfn-wire.log]\n", "file = /var/log/cfn-wire.log\n", "log_group_name = ", Ref(CloudFormationLogs), "\n", "log_stream_name = {instance_id}/cfn-wire.log\n", "datetime_format = \n", "[/var/log/httpd]\n", "file = /var/log/httpd/*\n", "log_group_name = ", Ref(CloudFormationLogs), "\n", "log_stream_name = {instance_id}/httpd\n", "datetime_format = %d/%b/%Y:%H:%M:%S\n"]), "owner": "root", "group": "root", "mode": "000444" } }, "services": { "sysvinit": { "awslogs": { "files": ["/etc/awslogs/awslogs.conf"], "ensureRunning": "true", "enabled": "true" } } }, "commands": { "01_create_state_directory": { "command": "mkdir -p /var/awslogs/state" } }, "packages": { "yum": { "awslogs": [] } } }, "Configure": { "commands": { "test": { "test": "test ! -e ~/test.txt", "ignoreErrors": "false", "command": "echo \"$ENV_TEST\" > test.txt", "cwd": "~", "env": { "ENV_TEST": "I come from the environment!" } } } }, "Install": { "files": { "/etc/cfn/cfn-hup.conf": { "content": Join("", ["[main]\n", "stack=", Ref("AWS::StackId"), "\n", "region=", Ref("AWS::Region"), "\n", "interval=1", "\n"]), "owner": "root", "group": "root", "mode": "000400" }, "/etc/cfn/hooks.d/cfn-auto-reloader.conf": { "content": Join("", ["[cfn-auto-reloader-hook]\n", "triggers=post.update\n", "path=Resources.ChefNodeInstance.Metadata.AWS::CloudFormation::Init\n", "action=/opt/aws/bin/cfn-init -v ", "         --stack ", Ref("AWS::StackName"), "         --resource ChefNodeInstance ", "         --configsets InstallAndRun ", "         --region ", Ref("AWS::Region"), "\n", "runas=root\n"]) } }, "sources": { "/home/ec2-user": "https://github.com/Codewars/codewars-runner-cli/archive/master.zip" }, "packages": { "yum": { "stress": [], "docker": [] } }, "services": { "sysvinit": { "docker": { "ensureRunning": "true", "enabled": "true" }, "cfn-hup": { "files": ["/etc/cfn/cfn-hup.conf", "/etc/cfn/hooks.d/cfn-auto-reloader.conf"], "ensureRunning": "true", "enabled": "true" } } } }, "configSets": { "InstallAndRun": ["Install", "InstallLogs", "Configure"] } },
    ),
    UserData=Base64(Join("", ["#!/bin/bash -xe\n", "yum update -y \n", "yum update -y aws-cfn-bootstrap\n", "# Install the files and packages from the metadata\n", "/opt/aws/bin/cfn-init -v ", "         --stack ", Ref("AWS::StackName"), "         --resource ChefNodeInstance ", "         --configsets InstallAndRun ", "         --region ", Ref("AWS::Region"), "\n", "# Signal the status from cfn-init\n", "/opt/aws/bin/cfn-signal -e $? ", "         --stack ", Ref("AWS::StackName"), "         --resource ChefNodeInstance ", "         --region ", Ref("AWS::Region"), "\n", "sudo usermod -a -G docker ec2-user", "\n"])),
    ImageId=FindInMap("AWSRegionArch2AMI", Ref("AWS::Region"), FindInMap("AWSInstanceType2Arch", Ref(InstanceType), "Arch")),
    BlockDeviceMappings=[{ "DeviceName": "/dev/xvda", "Ebs": { "VolumeSize": 10 } }],
    KeyName=Ref(KeyName),
    SecurityGroups=[Ref(InstanceSecurityGroup)],
    IamInstanceProfile=Ref(LogRoleInstanceProfile),
    InstanceType=Ref(InstanceType),
))

WebsiteURL = t.add_output(Output(
    "WebsiteURL",
    Description="Public DNS Name",
    Value=Join("", [GetAtt(ChefNodeInstance, "PublicDnsName")]),
))

print(t.to_json())
