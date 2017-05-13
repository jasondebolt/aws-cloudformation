"""Create an EC2 InstanceProfile resource using AWS CloudFormation.

Create an IAM Role, IAM Policy, and EC2 Instance Profile for EC2 Instances.
"""
from troposphere import Ref, Template
from troposphere.logs import LogGroup
import troposphere.iam as iam


LOG_POLICY_NAME = 'LogPolicy'
LOG_GROUP_NAME = 'CloudFormationLogs'
LOG_RETENTION_DAYS = 7


class Ec2Resources(object):
    """Cloudformation resources that EC2 instances depend on."""
    def __init__(self, template):
        self.template = template

    def attach_ec2_instance_profile(self):
        """Attached an IAM Role, IAM Policy, and EC2 Instance Profile to a
        CloudFormation template and returns the template."
        """
        self.template.add_resource(iam.Role(
            "EC2Role",
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
            LOG_POLICY_NAME,
            PolicyName=LOG_POLICY_NAME,
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
            Roles=[Ref("EC2Role")]
        ))

        self.template.add_resource(iam.InstanceProfile(
            "EC2RoleInstanceProfile",
            Path="/",
            Roles=[Ref("EC2Role")]
        ))

        self.template.add_resource(LogGroup(
            LOG_GROUP_NAME,
            RetentionInDays=LOG_RETENTION_DAYS
        ))

        return self.template


def main():
    """Generates a cloudformation template."""
    template = Template()
    template.add_version('2010-09-09')
    template.add_description('Create an IAM Role, IAM Policy, and EC2 '
                             'Instance Profile, and a CloudFormation log group '
                             'for EC2 Instances.')
    ec2_resources = Ec2Resources(template)
    template = ec2_resources.attach_ec2_instance_profile()
    print template.to_json()


if __name__ == '__main__':
    main()
