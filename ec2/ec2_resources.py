"""Create an EC2 InstanceProfile resource using AWS CloudFormation.

Create an IAM Role, IAM Policy, and EC2 Instance Profile for EC2 Instances.
"""
from troposphere import Ref, Template
from troposphere.logs import LogGroup
import troposphere.iam as iam
import ec2_parameters # pylint: disable=W0403


class EC2Resources(object):
    """Cloudformation resources that EC2 instances depend on."""
    def __init__(self, template):
        self.template = template

    def attach(self):
        """Attached an IAM Role, IAM Policy, and EC2 Instance Profile to a
        CloudFormation template and returns the template."
        """
        self.template.add_resource(iam.Role(
            'RoleResource',
            AssumeRolePolicyDocument={
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "Service": ["ec2.amazonaws.com",
                                    "opsworks.amazonaws.com"]
                    },
                    "Action": ["sts:AssumeRole"]
                }]
            },
            ManagedPolicyArns=[
                "arn:aws:iam::aws:policy/AmazonS3FullAccess",
            ],
            Path="/"
        ))

        # Inline policy for the given role defined in the Roles attribute.
        self.template.add_resource(iam.PolicyType(
            'LogPolicyResource',
            PolicyName=Ref(self.template.parameters['LogPolicyName']),
            PolicyDocument={
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Resource": [
                        "*"
                    ],
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                        "logs:DescribeLogStreams"
                    ]
                }]
            },
            Roles=[Ref(self.template.resources['RoleResource'])]
        ))

        self.template.add_resource(iam.InstanceProfile(
            'InstanceProfileResource',
            Path="/",
            Roles=[Ref(self.template.resources['RoleResource'])]
        ))

        self.template.add_resource(LogGroup(
            'LogGroupResource',
            LogGroupName=Ref(self.template.parameters['LogGroupName']),
            RetentionInDays=Ref(self.template.parameters['LogRetentionDays'])
        ))

        return self.template


def main():
    """Generates a cloudformation template."""
    template = Template()
    template.add_version('2010-09-09')
    template.add_description('Create an IAM Role, IAM Policy, and EC2 '
                             'Instance Profile, and a CloudFormation log group '
                             'for EC2 Instances.')
    parameters = ec2_parameters.EC2Parameters(template)
    parameters.attach()
    ec2_resources = EC2Resources(template)
    ec2_resources.attach()
    print template.to_json()


if __name__ == '__main__':
    main()
