"""Generates an AWS CloudFormation template to bootstrap a Chef node.

You must have an S3 bucket with the following files
    {S3_BUCKET_PATH}/{VALIDATOR_FILENAME}
    {S3_BUCKET_PATH}/{FIRST_RUN_FILENAME}
    {S3_BUCKET_PATH}/client.rb

Change the constants below with the names of your chef-client files.
"""
from troposphere import Base64, FindInMap, Join, Output, GetAtt, Tags, If
from troposphere import Ref, Template
from troposphere import cloudformation
import troposphere.ec2 as ec2
import ec2_parameters # pylint: disable=W0403
import ec2_resources # pylint: disable=W0403


EC2_INSTANCE_NAME = 'ChefNodeInstance'

# Where are your chef-client related files stored?
S3_CHEF_BOOTSTRAP_PATH = 'https://s3-us-west-2.amazonaws.com/jasondebolt-chef/'

# What are the names of your validator and first run files?
VALIDATOR_FILENAME = 'jasondebolt-validator.pem'
FIRST_RUN_FILENAME = 'first-run.json'

S3_FIRST_RUN = '{0}{1}'.format(S3_CHEF_BOOTSTRAP_PATH, FIRST_RUN_FILENAME)
S3_CLIENT_RB = '{0}client.rb'.format(S3_CHEF_BOOTSTRAP_PATH)
S3_VALIDATOR_PEM = '{0}{1}'.format(S3_CHEF_BOOTSTRAP_PATH, VALIDATOR_FILENAME)


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
                ),
                ec2.SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort=80,
                    ToPort=80,
                    CidrIp='0.0.0.0/0'
                ),
                ec2.SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort=8080,
                    ToPort=8080,
                    CidrIp='0.0.0.0/0'
                )
            ],
            Tags=Tags(
                Name='{0}SecurityGroup'.format(EC2_INSTANCE_NAME)
            )
        ))

        self.template.add_resource(ec2.Instance(
            EC2_INSTANCE_NAME,
            ImageId=If(
                'IsCentos7',
                FindInMap(
                    "AWSRegionArch2Centos7LinuxAMI", Ref("AWS::Region"),
                    FindInMap("AWSInstanceType2Arch",
                              Ref(self.template.parameters['InstanceType']),
                              "Arch")),
                FindInMap(
                    "AWSRegionArch2AmazonLinuxAMI", Ref("AWS::Region"),
                    FindInMap("AWSInstanceType2Arch",
                              Ref(self.template.parameters['InstanceType']),
                              "Arch"))
            ),
            InstanceType=Ref(self.template.parameters['InstanceType']),
            KeyName=FindInMap('Region2KeyPair', Ref('AWS::Region'), 'key'),
            SecurityGroups=[Ref(security_group)],
            IamInstanceProfile=Ref(
                self.template.resources['InstanceProfileResource']),
            UserData=Base64(Join('', [
                If('IsCentos7',
                   Join('\n', [
                       '#!/bin/bash ',
                       'sudo yum update -y ',
                       'sudo yum install -y vim ',
                       'sudo yum install -y epel-release ',
                       'sudo yum install -y awscli ',
                       '# Install CFN-BootStrap ',
                       ('/usr/bin/easy_install --script-dir /opt/aws/bin '
                        'https://s3.amazonaws.com/cloudformation-examples/'
                        'aws-cfn-bootstrap-latest.tar.gz '),
                       ('cp -v /usr/lib/python2*/site-packages/aws_cfn_'
                        'bootstrap*/init/redhat/cfn-hup /etc/init.d '),
                       'chmod +x /etc/init.d/cfn-hup ',
                       ]),
                   Join('\n', [
                       '#!/bin/bash -xe ',
                       'yum update -y ',
                       '# Update CFN-BootStrap ',
                       'yum update -y aws-cfn-bootstrap',
                       'sudo yum install -y awslogs ',
                       ])),
                Join('', [
                    '# Install the files and packages from the metadata\n'
                    '/opt/aws/bin/cfn-init -v ',
                    '         --stack ', Ref('AWS::StackName'),
                    '         --resource ', EC2_INSTANCE_NAME,
                    '         --configsets InstallAndRun',
                    '         --region ', Ref('AWS::Region'),
                    '         --role ',
                    Ref(self.template.resources['RoleResource']),
                    '\n',
                    '# Signal the status from cfn-init\n',
                    '/opt/aws/bin/cfn-signal -e $? '
                    '         --stack ', Ref('AWS::StackName'),
                    '         --resource ', EC2_INSTANCE_NAME,
                    '         --region ', Ref('AWS::Region'),
                    '         --role ',
                    Ref(self.template.resources['RoleResource']),
                    '\n'
                    ]),
                ]
                                )
                           ),
            Metadata=cloudformation.Metadata(
                cloudformation.Init(
                    cloudformation.InitConfigSets(
                        InstallAndRun=['Install', 'InstallLogs', 'InstallChef',
                                       'Configure']
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
                                'content': Join('\n', [
                                    '[main]',
                                    'stack={{stackid}}',
                                    'region={{region}}',
                                    'interval=1'
                                    ]),
                                'context': {
                                    'stackid': Ref('AWS::StackId'),
                                    'region': Ref('AWS::Region')
                                },
                                'mode': '000400',
                                'owner': 'root',
                                'group': 'root'
                            },
                            '/etc/cfn/hooks.d/cfn-auto-reloader.conf': {
                                'content': Join('\n', [
                                    '[cfn-auto-reloader-hook]',
                                    'triggers=post.update',
                                    ('path=Resources.{{instance_name}}'
                                     '.Metadata'
                                     '.AWS::CloudFormation::Init'),
                                    ('action=/opt/aws/bin/cfn-init -v '
                                     '     --stack {{stack_name}} '
                                     '     --resource {{instance_name}} '
                                     '     --configsets {{config_sets}} '
                                     '     --region {{region}} '),
                                    'runas={{run_as}}'
                                ]),
                                'context': {
                                    'instance_name': EC2_INSTANCE_NAME,
                                    'stack_name': Ref('AWS::StackName'),
                                    'region': Ref('AWS::Region'),
                                    'config_sets': 'InstallAndRun',
                                    'run_as': 'root'
                                }
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
                            '01_test': {
                                'command': 'echo "$CFNTEST" > Install.txt',
                                'env': {
                                    'CFNTEST': 'I come from Install.'
                                },
                                'cwd': '~'
                            }
                        }
                    ),
                    InstallLogs=cloudformation.InitConfig(
                        files={
                            '/etc/awslogs/awslogs.conf': {
                                'content': Join('\n', [
                                    '[general]',
                                    ('state_file= /var/awslogs/'
                                     'state/agent-state'),
                                    '',
                                    '[/var/log/cloud-init.log]',
                                    'file = /var/log/cloud-init.log',
                                    'log_group_name = {{log_group_name}}',
                                    ('log_stream_name = '
                                     '{instance_id}/cloud-init.log'),
                                    'datetime_format = {{datetime_format}}',
                                    '',
                                    '[/var/log/cloud-init-output.log]',
                                    'file = /var/log/cloud-init-output.log',
                                    'log_group_name = {{log_group_name}}',
                                    ('log_stream_name = '
                                     '{instance_id}/cloud-init-output.log'),
                                    'datetime_format = {{datetime_format}}',
                                    '',
                                    '[/var/log/cfn-init.log]',
                                    'file = /var/log/cfn-init.log',
                                    'log_group_name = {{log_group_name}}',
                                    ('log_stream_name = '
                                     '{instance_id}/cfn-init.log'),
                                    'datetime_format = {{datetime_format}}',
                                    '',
                                    '[/var/log/cfn-hup.log]',
                                    'file = /var/log/cfn-hup.log',
                                    'log_group_name = {{log_group_name}}',
                                    ('log_stream_name = '
                                     '{instance_id}/cfn-hup.log'),
                                    'datetime_format = {{datetime_format}}',
                                    '',
                                    '[/var/log/cfn-wire.log]',
                                    'file = /var/log/cfn-wire.log',
                                    'log_group_name = {{log_group_name}}',
                                    ('log_stream_name = '
                                     '{instance_id}/cfn-wire.log'),
                                    'datetime_format = {{datetime_format}}',
                                    '',
                                    '[/var/log/httpd]',
                                    'file = /var/log/httpd/*',
                                    'log_group_name = {{log_group_name}}',
                                    ('log_stream_name = '
                                     '{instance_id}/httpd'),
                                    'datetime_format = {{datetime_format}}'
                                ]),
                                'context': {
                                    'log_group_name': Ref(
                                        self.template.resources[
                                            'LogGroupResource']),
                                    'datetime_format': '%d/%b/%Y:%H:%M:%S'
                                }
                            },
                            '/etc/awslogs/awscli.conf': {
                                'content': Join('\n', [
                                    '[plugins]',
                                    'cwlogs = cwlogs',
                                    '[default]',
                                    'region = {{region}}'
                                ]),
                                'context': {
                                    'region': Ref('AWS::Region')
                                },
                                'mode': '000444',
                                'owner': 'root',
                                'group': 'root'
                            }
                        },
                        commands={
                            '01_create_state_directory': {
                                'command' : 'mkdir -p /var/awslogs/state'
                            },
                            '02_test': {
                                'command': 'echo "$CFNTEST" > InstallLogs.txt',
                                'env': {
                                    'CFNTEST': 'I come from install_logs.'
                                },
                                'cwd': '~'
                            },
                            '03_install_aws_logs_if_centos': {
                                'command': If('IsCentos7', Join('\n', [
                                    ('curl https://s3.amazonaws.com/aws-'
                                     'cloudwatch/downloads/latest/awslogs-'
                                     'agent-setup.py -O'),
                                    Join('', [
                                        'sudo python ./awslogs-agent-setup.py',
                                        '   --configfile /etc/awslogs/awslogs',
                                        '.conf   --non-interactive  --region ',
                                        Ref('AWS::Region')])
                                    ]), Join('', [
                                        'echo "not installing awslogs from ',
                                        'from source"'
                                        ]))
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
                    InstallChef=cloudformation.InitConfig(
                        commands={
                            '01_invoke_omnitruck_install': {
                                'command': (
                                    'curl -L '
                                    'https://omnitruck.chef.io/install.sh | '
                                    'bash'
                                ),
                            }
                        },
                        files={
                            '/etc/chef/client.rb': {
                                'source': S3_CLIENT_RB,
                                'mode': '000600',
                                'owner': 'root',
                                'group': 'root',
                                'authentication': 'S3AccessCreds'
                            },
                            '/etc/chef/jasondebolt-validator.pem': {
                                'source': S3_VALIDATOR_PEM,
                                'mode': '000600',
                                'owner': 'root',
                                'group': 'root',
                                'authentication': 'S3AccessCreds'
                            },
                            '/etc/chef/first-run.json': {
                                'source': S3_FIRST_RUN,
                                'mode': '000600',
                                'owner': 'root',
                                'group': 'root',
                                'authentication': 'S3AccessCreds'
                            }
                        }
                    ),
                    Configure=cloudformation.InitConfig(
                        commands={
                            '01_test': {
                                'command': 'echo "$CFNTEST" > Configure.txt',
                                'env': {
                                    'CFNTEST': 'I come from Configure.'
                                },
                                'cwd': '~'
                            },
                            '02_chef_bootstrap': {
                                'command': (
                                    'chef-client -j '
                                    '/etc/chef/first-run.json'
                                )
                            }
                        }
                    )
                ),
                cloudformation.Authentication({
                    'S3AccessCreds': cloudformation.AuthenticationBlock(
                        type='S3',
                        roleName=Ref(self.template.resources['RoleResource']))
                })
            ),
            Tags=Tags(
                Name=Ref('AWS::StackName'),
                env='ops'
            )
        ))

        self.template.add_output(Output(
            'PublicIp',
            Description='Public IP of the newly created EC2 instance',
            Value=GetAtt(EC2_INSTANCE_NAME, 'PublicIp')
        ))

        self.template.add_output(Output(
            'LinuxType',
            Description='The linux type of the EC2 instance.',
            Value=If('IsCentos7', 'centos_7', 'amazon_linux')
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
