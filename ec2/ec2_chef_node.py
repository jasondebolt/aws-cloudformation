"""Generates an AWS CloudFormation template to bootstrap a Chef node."""
from troposphere import Base64, FindInMap, Join, Output, GetAtt, Tags
from troposphere import Ref, Template
from troposphere import cloudformation
import troposphere.ec2 as ec2
import ec2_parameters # pylint: disable=W0403
import ec2_resources # pylint: disable=W0403

EC2_INSTANCE_NAME = 'ChefNodeInstance'


class ChefNodeEC2Instance(object):
    """Generates the appropriate Cloudformation resources to produce
    an EC2 instance with an automatically bootstrapped Chef node.
    """
    def __init__(self, template):
        self.template = template

    def attach(self):
        """Attaches a bootstrapped Chef Node EC2 instance to an
        AWS CloudFormation template and returns the template.
        """
        parameters = ec2_parameters.EC2Parameters(self.template)
        parameters.attach()
        resources = ec2_resources.EC2Resources(self.template)
        resources.attach()

        security_group = self.template.add_resource(ec2.SecurityGroup(
            'SecurityGroup',
            GroupDescription='Allows SSH access from anywhere',
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort=22,
                    ToPort=22,
                    CidrIp=Ref(self.template.parameters['SSHLocation'])
                )
            ],
            Tags=Tags(
                Name='ChefNodeSecurityGroup'
            )
        ))

        self.template.add_resource(ec2.Instance(
            EC2_INSTANCE_NAME,
            ImageId=FindInMap(
                "AWSRegionArch2AMI", Ref("AWS::Region"),
                FindInMap("AWSInstanceType2Arch",
                          Ref(self.template.parameters['InstanceType']),
                          "Arch")),
            InstanceType=Ref(self.template.parameters['InstanceType']),
            KeyName=Ref(self.template.parameters['KeyName']),
            SecurityGroups=[Ref(security_group)],
            IamInstanceProfile=Ref(
                self.template.resources['InstanceProfileResource']),
            UserData=Base64(Join('', [
                '#!/bin/bash -xe\n',
                'yum update -y \n',
                'yum update -y aws-cfn-bootstrap\n',

                '# Install the files and packages from the metadata\n',
                '/opt/aws/bin/cfn-init -v ',
                '         --stack ', Ref('AWS::StackName'),
                '         --resource {0} '.format(EC2_INSTANCE_NAME),
                '         --configsets InstallAndRun ',
                '         --region ', Ref('AWS::Region'),
                '\n',
                '# Signal the status from cfn-init\n',
                '/opt/aws/bin/cfn-signal -e $? ',
                '         --stack ', Ref('AWS::StackName'),
                '         --resource {0} '.format(EC2_INSTANCE_NAME),
                '         --region ', Ref('AWS::Region'),
                'sudo usermod -a -G docker ec2-user',
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
                                     .format(EC2_INSTANCE_NAME)),
                                    'action=/opt/aws/bin/cfn-init -v ',
                                    '     --stack ', Ref('AWS::StackName'),
                                    '     --resource {0} '
                                    .format(EC2_INSTANCE_NAME),
                                    '     --configsets InstallAndRun ',
                                    '     --region ', Ref('AWS::Region'), '\n',
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
                                    'state_file= /var/awslogs/',
                                    'state/agent-state\n',
                                    '[/var/log/cloud-init.log]\n',
                                    'file = /var/log/cloud-init.log\n',
                                    Join('', ['log_group_name = ',
                                              Ref(self.template.resources[
                                                  'LogGroupResource']), '\n']),
                                    'log_stream_name = ',
                                    '{instance_id}/cloud-init.log\n',
                                    'datetime_format = \n',

                                    '[/var/log/cloud-init-output.log]\n',
                                    'file = /var/log/cloud-init-output.log\n',
                                    Join('', ['log_group_name = ',
                                              Ref(self.template.resources[
                                                  'LogGroupResource']), '\n']),
                                    'log_stream_name = ',
                                    '{instance_id}/cloud-init-output.log\n',
                                    'datetime_format = \n',

                                    '[/var/log/cfn-init.log]\n',
                                    'file = /var/log/cfn-init.log\n',
                                    Join('', ['log_group_name = ',
                                              Ref(self.template.resources[
                                                  'LogGroupResource']), '\n']),
                                    'log_stream_name = ',
                                    '{instance_id}/cfn-init.log\n',
                                    'datetime_format = \n',

                                    '[/var/log/cfn-hup.log]\n',
                                    'file = /var/log/cfn-hup.log\n',
                                    Join('', ['log_group_name = ',
                                              Ref(self.template.resources[
                                                  'LogGroupResource']), '\n']),
                                    'log_stream_name = ',
                                    '{instance_id}/cfn-hup.log\n',
                                    'datetime_format = \n',

                                    '[/var/log/cfn-wire.log]\n',
                                    'file = /var/log/cfn-wire.log\n',
                                    Join('', ['log_group_name = ',
                                              Ref(self.template.resources[
                                                  'LogGroupResource']), '\n']),
                                    'log_stream_name = ',
                                    '{instance_id}/cfn-wire.log\n',
                                    'datetime_format = \n',

                                    '[/var/log/httpd]\n',
                                    'file = /var/log/httpd/*\n',
                                    Join('', ['log_group_name = ',
                                              Ref(self.template.resources[
                                                  'LogGroupResource']), '\n']),
                                    'log_stream_name = ',
                                    '{instance_id}/httpd\n',
                                    'datetime_format = %d/%b/%Y:%H:%M:%S\n'
                                ])
                            },
                            '/etc/awslogs/awscli.conf': {
                                'content': Join('', [
                                    '[plugins]\n',
                                    'cwlogs = cwlogs\n',
                                    '[default]\n',
                                    'region = ', Ref('AWS::Region'), '\n',
                                ]),
                                'mode': '000444',
                                'owner': 'root',
                                'group': 'root'
                            }
                        },
                        commands={
                            '01_create_state_directory': {
                                'command' : 'mkdir -p /var/awslogs/state'
                            },
                            'test': {
                                'command': 'echo "$CFNTEST" > InstallLogs.txt',
                                'env': {
                                    'CFNTEST': 'I come from install_logs.'
                                },
                                'cwd': '~'
                            }
                        },
                        services={
                            'sysvinit': {
                                'awslogs': {
                                    'enabled': 'true',
                                    'ensureRunning': 'true',
                                    'files': ['/etc/awslogs/awslogs.conf']
                                }
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

        self.template.add_output(Output(
            'PublicIp',
            Description='Public IP of the newly created EC2 instance',
            Value=GetAtt(EC2_INSTANCE_NAME, 'PublicIp')
        ))
        return self.template


def main():
    template = Template()
    template.add_version('2010-09-09')
    template.add_description('Create a fully bootstrapped Chef node.')
    chef_node = ChefNodeEC2Instance(template)
    chef_node.attach()
    print template.to_json()

if __name__ == '__main__':
    main()
