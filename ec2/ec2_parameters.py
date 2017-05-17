"""Creates common parameters for EC2 instances resources within CloudFormation.
"""
from troposphere import Parameter, Template, Condition, Equals, Ref, FindInMap
import ec2_mappings # pylint: disable=W0403


class EC2Parameters(object):
    """Cloudformation parameters that EC2 instances depend on."""
    def __init__(self, template):
        self.template = template

    def attach(self):
        """Attaches parameters to EC2 instances launched with
        AWS CloudFormation.
        """
        self.template.add_parameter(Parameter(
            'SSHLocation',
            ConstraintDescription=(
                'must be a valid IP CIDR range of the form x.x.x.x/x.'),
            Description=(
                'The IP address range that can be used to SSH to '
                'the EC2 instances'),
            Default='0.0.0.0/0',
            MinLength='9',
            AllowedPattern=(
                '(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})/(\\d{1,2})'),
            MaxLength='18',
            Type='String',
        ))

        self.template.add_parameter(Parameter(
            'InstanceType',
            Default='t2.micro',
            ConstraintDescription='must be a valid EC2 instance type.',
            Type='String',
            Description='EC2 Instance Size',
            AllowedValues=[
                't1.micro', 't2.nano', 't2.micro', 't2.small', 't2.medium',
                't2.large', 'm1.small', 'm1.medium', 'm1.large', 'm1.xlarge',
                'm2.xlarge', 'm2.2xlarge', 'm2.4xlarge', 'm3.medium',
                'm3.large', 'm3.xlarge', 'm3.2xlarge', 'm4.large', 'm4.xlarge',
                'm4.2xlarge', 'm4.4xlarge', 'm4.10xlarge', 'c1.medium',
                'c1.xlarge', 'c3.large', 'c3.xlarge', 'c3.2xlarge',
                'c3.4xlarge', 'c3.8xlarge', 'c4.large', 'c4.xlarge',
                'c4.2xlarge', 'c4.4xlarge', 'c4.8xlarge', 'g2.2xlarge',
                'g2.8xlarge', 'r3.large', 'r3.xlarge', 'r3.2xlarge',
                'r3.4xlarge', 'r3.8xlarge', 'i2.xlarge', 'i2.2xlarge',
                'i2.4xlarge', 'i2.8xlarge', 'd2.xlarge', 'd2.2xlarge',
                'd2.4xlarge', 'd2.8xlarge', 'hi1.4xlarge', 'hs1.8xlarge',
                'cr1.8xlarge', 'cc2.8xlarge', 'cg1.4xlarge'],
        ))

        self.template.add_parameter(Parameter(
            'LinuxType',
            Default='centos_7',
            ConstraintDescription='must be either centos_7 or amazon_linux',
            Type='String',
            Description='Linux Type',
            AllowedValues=['centos_7', 'amazon_linux']
        ))

        self.template.add_parameter(Parameter(
            'RoleName',
            Description=(
                'The name you would like to give the role associated with '
                'this EC2 instance.'),
            Default='InstanceRole',
            MinLength='1',
            AllowedPattern=('^[a-zA-Z0-9]*$'),
            MaxLength='15',
            Type='String',
        ))

        self.template.add_parameter(Parameter(
            'InstanceProfileName',
            Description=(
                'The instance profile name you would like to give the role '
                'associated with this EC2 instance.'),
            Default='InstanceProfile',
            MinLength='1',
            AllowedPattern=('^[a-zA-Z0-9]*$'),
            MaxLength='15',
            Type='String',
        ))

        self.template.add_parameter(Parameter(
            'LogPolicyName',
            Description=(
                'The log policy name you would like to give the role '
                'associated with this EC2 instance.'),
            Default='LogPolicy',
            MinLength='1',
            AllowedPattern=('^[a-zA-Z0-9]*$'),
            MaxLength='15',
            Type='String',
        ))

        self.template.add_parameter(Parameter(
            'LogGroupName',
            Description=(
                'The log group name you would like to give the role '
                'associated with this EC2 instance.'),
            Default='LogGroup',
            MinLength='1',
            AllowedPattern=('^[a-zA-Z0-9]*$'),
            MaxLength='15',
            Type='String',
        ))

        self.template.add_parameter(Parameter(
            'LogRetentionDays',
            Description=(
                'The number of days you would like to retain the logs '
                'associated with this instance in cloudwatch.'),
            Default='7',
            AllowedValues=[
                '1', '3', '5', '7', '14', '30', '60', '90', '120', '150',
                '180', '365', '400', '545', '731', '1827', '3653'],
            Type='Number',
        ))

        self.template.add_condition(
            'IsCentos7',
            Equals(Ref('LinuxType'), 'centos_7')
        )

        return ec2_mappings.attach_mappings(self.template)


def main():
    template = Template()
    template.add_version('2010-09-09')
    template.add_description('Create common parameters for EC2 related'
                             'AWS CloudFormation resources')
    ec2_parameters = EC2Parameters(template)
    ec2_parameters.attach()
    print template.to_json()


if __name__ == '__main__':
    main()
