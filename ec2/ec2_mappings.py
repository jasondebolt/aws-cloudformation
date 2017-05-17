"""Creates common mappings for EC2 instances resources within CloudFormation.
"""
from troposphere import Template

def attach_mappings(template):
    """Attaches common mappings to a template for EC2 related resources."""
    template.add_mapping(
        "Region2Principal",
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

    template.add_mapping(
        "Region2KeyPair",
        {u'ap-northeast-1': {u'key': 'tokyo'},
         u'ap-northeast-2': {u'key': 'seoul'},
         u'ap-south-1': {u'key': 'mumbai'},
         u'ap-southeast-1': {u'key': 'singapore'},
         u'ap-southeast-2': {u'key': 'sydney'},
         u'cn-north-1': {u'key': 'NO ACCESS TO CHINA FOR US USERS'},
         u'eu-central-1': {u'key': 'frankfurt'},
         u'eu-west-1': {u'key': 'ireland'},
         u'eu-west-2': {u'key': 'london'},
         u'sa-east-1': {u'key': 'sao-paulo'},
         u'ca-central-1': {u'key': 'central-canada'},
         u'us-east-1': {u'key': 'north-virginia'},
         u'us-east-2': {u'key': 'ohio'},
         u'us-west-1': {u'key': 'northern-california'},
         u'us-west-2': {u'key': 'oregon'}}
    )

    template.add_mapping(
        "Region2ARNPrefix",
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

    template.add_mapping(
        "AWSInstanceType2Arch",
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
    template.add_mapping(
        "AWSRegionArch2Centos7LinuxAMI",
        {u'ap-northeast-1': {u'HVM64': u'ami-571e3c30',
                             u'HVMG2': u'NOT_SUPPORTED',
                             u'PV64': u'NOT_SUPPORTED'},
         u'ap-northeast-2': {u'HVM64': u'ami-97cb19f9',
                             u'HVMG2': u'NOT_SUPPORTED',
                             u'PV64': u'NOT_SUPPORTED'},
         u'ap-south-1': {u'HVM64': u'ami-11f0837e',
                         u'HVMG2': u'NOT_SUPPORTED',
                         u'PV64': u'NOT_SUPPORTED'},
         u'ap-southeast-1': {u'HVM64': u'ami-30318f53',
                             u'HVMG2': u'NOT_SUPPORTED',
                             u'PV64': u'NOT_SUPPORTED'},
         u'ap-southeast-2': {u'HVM64': u'ami-24959b47',
                             u'HVMG2': u'NOT_SUPPORTED',
                             u'PV64': u'NOT_SUPPORTED'},
         u'cn-north-1': {u'HVM64': u'NOT_SUPPORTED',
                         u'HVMG2': u'NOT_SUPPORTED',
                         u'PV64': u'NOT_SUPPORTED'},
         u'eu-central-1': {u'HVM64': u'ami-7cbc6e13',
                           u'HVMG2': u'NOT_SUPPORTED',
                           u'PV64': u'NOT_SUPPORTED'},
         u'eu-west-1': {u'HVM64': u'ami-0d063c6b',
                        u'HVMG2': u'NOT_SUPPORTED',
                        u'PV64': u'NOT_SUPPORTED'},
         u'sa-east-1': {u'HVM64': u'ami-864f2dea',
                        u'HVMG2': u'NOT_SUPPORTED',
                        u'PV64': u'NOT_SUPPORTED'},
         u'us-east-1': {u'HVM64': u'ami-ae7bfdb8',
                        u'HVMG2': u'NOT_SUPPORTED',
                        u'PV64': u'NOT_SUPPORTED'},
         u'us-west-1': {u'HVM64': u'ami-7c280d1c',
                        u'HVMG2': u'NOT_SUPPORTED',
                        u'PV64': u'NOT_SUPPORTED'},
         u'us-west-2': {u'HVM64': u'ami-0c2aba6c',
                        u'HVMG2': u'NOT_SUPPORTED',
                        u'PV64': u'NOT_SUPPORTED'}}
    )

    template.add_mapping(
        "AWSRegionArch2AmazonLinuxAMI",
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

    return template


def main():
    template = Template()
    template.add_version('2010-09-09')
    template.add_description('Create common mappings for EC2 related'
                             'AWS CloudFormation resources')
    template = attach_mappings(template)
    print template.to_json()


if __name__ == '__main__':
    main()
