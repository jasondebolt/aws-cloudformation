"""Generates an AWS CloudFormation template to bootstrap a Chef node."""
from troposphere import Base64, FindInMap, Join, Output, GetAtt, Tags
from troposphere import Ref, Template
from troposphere import cloudformation
import troposphere.ec2 as ec2
import ec2_parameters # pylint: disable=W0403
import ec2_instance_profile # pylint: disable=W0403

EC2_INSTANCE = 'Ec2Instance'

def attach_chef_node(template):
    """Attaches a bootstrapped Chef Node EC2 instance to an
    AWS CloudFormation template and returns the template.
    """
    template = ec2_parameters.attach_ec2_parameters(template)
    template = ec2_instance_profile.attach_ec2_instance_profile(template)

    security_group = template.add_resource(ec2.SecurityGroup(
        'SecurityGroup',
        GroupDescription='Allows SSH access from anywhere',
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=22,
                ToPort=22,
                CidrIp=Ref(template.parameters['SSHLocation'])
            )
        ],
        Tags=Tags(
            Name='ChefNodeSecurityGroup'
        )
    ))

    ec2_instance = template.add_resource(ec2.Instance(
        EC2_INSTANCE,
        ImageId=FindInMap(
            "AWSRegionArch2AMI", Ref("AWS::Region"),
            FindInMap("AWSInstanceType2Arch",
                      Ref(template.parameters['InstanceType']), "Arch")),
        InstanceType=Ref(template.parameters['InstanceType']),
        KeyName=Ref(template.parameters['KeyName']),
        SecurityGroups=[Ref(security_group)],
        IamInstanceProfile=Ref(template.resources['EC2RoleInstanceProfile']),
        UserData=Base64(Join('', [
            '#!/bin/bash\n', 'sudo apt-get update\n',
            'sudo apt-get -y install python-setuptools\n',
            'sudo apt-get -y install python-pip\n',
            ('sudo pip install https://s3.amazonaws.com'
             '/cloudformation-examples/'),
            'aws-cfn-bootstrap-latest.tar.gz\n',
            '\n',
            '/opt/aws/bin/cfn-init -v ',
            '         --stack ', Ref('AWS::StackName'),
            '         --resource {0} '.format(EC2_INSTANCE),
            '         --configsets InstallAndRun ',
            '         --region ', Ref('AWS::Region'),
            '\n'
        ])),
        Metadata=cloudformation.Metadata(
            cloudformation.Init(
                cloudformation.InitConfigSets(
                    InstallAndRun=['Install', 'InstallLogs', 'Configure']
                ),
                Install=cloudformation.InitConfig(
                    packages={
                        'yum': {
                            'stress': [],
                            'docker': []
                        }
                    },
                    files={
                        '/etc/cfn/cfn-hup.conf': {
                            'content': Join('', [
                                '[main]\n',
                                'stack=', Ref('AWS::StackId'), '\n',
                                'region=', Ref('AWS::Region'), '\n',
                                'interval=1', '\n'
                                ]),
                            'mode': '000400',
                            'owner': 'root',
                            'group': 'root'
                        },
                        '/etc/cfn/hooks.d/cfn-auto-reloader.conf': {
                            'content': Join('', [
                                '[cfn-auto-reloader-hook]\n',
                                'triggers=post.update\n',
                                ('path=Resources.{0}.Metadata.'
                                 'AWS::CloudFormation::Init\n'
                                 .format(EC2_INSTANCE)),
                                'action=/opt/aws/bin/cfn-init -v ',
                                '       --stack ', Ref('AWS::StackName'),
                                '       --resource {0} '.format(EC2_INSTANCE),
                                '       --configsets InstallAndRun ',
                                '       --region ', Ref('AWS::Region'), '\n',
                                'runas=root\n'
                            ]),
                        }
                    },
                    services={
                        'sysvinit': {
                            'docker': {
                                'enabled': 'true',
                                'ensureRunning': 'true'
                            },
                            'cfn-hup': {
                                'enabled': 'true',
                                'ensureRunning': 'true'
                            }
                        }
                    },
                    commands={
                        'test': {
                            'command': 'echo "$CFNTEST" > Install.txt',
                            'env': {
                                'CFNTEST': 'I come from Install.'
                            },
                            'cwd': '~'
                        }
                    }
                ),
                InstallLogs=cloudformation.InitConfig(
                    packages={
                        'yum': {
                            'awslogs': []
                        }
                    },
                    files={
                        '/etc/awslogs/awslogs.conf': {
                            'content': Join('', [
                                '[general]\n',
                                'state_file= /var/awslogs/state/agent-state\n',

                                '[/var/log/cloud-init.log]\n',
                                'file = /var/log/cloud-init.log\n',
                                'log_group_name = ', { 'Ref': 'CloudFormationLogs' }, '\n',
                                'log_stream_name = {instance_id}/cloud-init.log\n',
                                'datetime_format = \n',

                                '[/var/log/cloud-init-output.log]\n',
                                'file = /var/log/cloud-init-output.log\n',
                                'log_group_name = ', { 'Ref': 'CloudFormationLogs' }, '\n',
                                'log_stream_name = {instance_id}/cloud-init-output.log\n',
                                'datetime_format = \n',

                                '[/var/log/cfn-init.log]\n',
                                'file = /var/log/cfn-init.log\n',
                                'log_group_name = ', { 'Ref': 'CloudFormationLogs' }, '\n',
                                'log_stream_name = {instance_id}/cfn-init.log\n',
                                'datetime_format = \n',

                                '[/var/log/cfn-hup.log]\n',
                                'file = /var/log/cfn-hup.log\n',
                                'log_group_name = ', { 'Ref': 'CloudFormationLogs' }, '\n',
                                'log_stream_name = {instance_id}/cfn-hup.log\n',
                                'datetime_format = \n',

                                '[/var/log/cfn-wire.log]\n',
                                'file = /var/log/cfn-wire.log\n',
                                'log_group_name = ', { 'Ref': 'CloudFormationLogs' }, '\n',
                                'log_stream_name = {instance_id}/cfn-wire.log\n',
                                'datetime_format = \n',

                                '[/var/log/httpd]\n',
                                'file = /var/log/httpd/*\n',
                                'log_group_name = ', { 'Ref': 'CloudFormationLogs' }, '\n',
                                'log_stream_name = {instance_id}/httpd\n',
                                'datetime_format = %d/%b/%Y:%H:%M:%S\n'
                            ])
                        }

                    },
                    commands={
                        'test': {
                            'command': 'echo "$CFNTEST" > InstallLogs.txt',
                            'env': {
                                'CFNTEST': 'I come from install_logs.'
                            },
                            'cwd': '~'
                        }
                    }
                ),
                Configure=cloudformation.InitConfig(
                    commands={
                        'test': {
                            'command': 'echo "$CFNTEST" > Configure.txt',
                            'env': {
                                'CFNTEST': 'I come from Configure.'
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

    template.add_output(Output(
        'PublicIp',
        Description='Public IP of the newly created EC2 instance',
        Value=GetAtt(ec2_instance, 'PublicIp')
    ))
    return template


def main():
    template = Template()
    template.add_version('2010-09-09')
    template.add_description('Create a fully bootstrapped Chef node.')
    template = attach_chef_node(template)
    print template.to_json()

if __name__ == '__main__':
    main()
