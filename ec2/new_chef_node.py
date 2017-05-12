from troposphere import Base64, FindInMap, Join, Output, GetAtt, Tags
from troposphere import Parameter, Ref, Template
from troposphere import cloudformation
import troposphere.ec2 as ec2
import ec2_header


t = Template()
t.add_version("2010-09-09")
t.add_description("Create an EC2 instance which automatically bootstraps a Chef node using Chef unattended installs.")
t = ec2_header.setEc2Header(t)

security_group = t.add_resource(ec2.SecurityGroup(
    'SecurityGroup',
    GroupDescription='Allows SSH access from anywhere',
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol='tcp',
            FromPort=22,
            ToPort=22,
            CidrIp=Ref(t.parameters['SSHLocation'])
        )
    ],
    Tags=Tags(
        Name='ChefNodeSecurityGroup'
    )
))

ec2_instance = t.add_resource(ec2.Instance(
    'Ec2Instance',
    ImageId=FindInMap("AWSRegionArch2AMI", Ref("AWS::Region"), FindInMap("AWSInstanceType2Arch", Ref(t.parameters['InstanceType']), "Arch")),
    InstanceType=Ref(t.parameters['InstanceType']),
    KeyName=Ref(t.parameters['KeyName']),
    SecurityGroups=[Ref(security_group)],
    IamInstanceProfile='LogRoleInstanceProfile',
    UserData=Base64(Join('', [
        '#!/bin/bash\n',
        'sudo apt-get update\n',
        'sudo apt-get -y install python-setuptools\n',
        'sudo apt-get -y install python-pip\n',
        'sudo pip install https://s3.amazonaws.com/cloudformation-examples/',
        'aws-cfn-bootstrap-latest.tar.gz\n',
        'cfn-init -s \'', Ref('AWS::StackName'),
        '\' -r Ec2Instance -c ascending'
    ])),
    Metadata=cloudformation.Metadata(
        cloudformation.Init(
            cloudformation.InitConfigSets(
                ascending=['config1', 'config2'],
                descending=['config2', 'config1']
            ),
            config1=cloudformation.InitConfig(
                commands={
                    'test': {
                        'command': 'echo "$CFNTEST" > text.txt',
                        'env': {
                            'CFNTEST': 'I come from config1.'
                        },
                        'cwd': '~'
                    }
                }
            ),
            config2=cloudformation.InitConfig(
                commands={
                    'test': {
                        'command': 'echo "$CFNTEST" > text.txt',
                        'env': {
                            'CFNTEST': 'I come from config2.'
                        },
                        'cwd': '~'
                    }
                }
            )
        )
    ),
    Tags=Tags(
        Name='ops.cfninit',
        env='ops'
    )
))

t.add_output(Output(
    'PublicIp',
    Description='Public IP of the newly created EC2 instance',
    Value=GetAtt(ec2_instance, 'PublicIp')
))


print(t.to_json())
