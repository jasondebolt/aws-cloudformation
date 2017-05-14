"""Create an EC2 InstanceProfile resource using AWS CloudFormation.

Create an IAM Role, IAM Policy, and EC2 Instance Profile for EC2 Instances.
"""
from troposphere import Ref, Template
from troposphere.logs import LogGroup
import troposphere.iam as iam

EC2_ROLE_NAME = 'Ec2Role'
EC2_INSTANCE_PROFILE_NAME = 'Ec2RoleInstanceProfile'
LOG_POLICY_NAME = 'LogPolicy'
LOG_GROUP_NAME = 'CloudFormationLogs'
LOG_RETENTION_DAYS = 7


class EC2Resources(object):
    """Cloudformation resources that EC2 instances depend on."""
    def __init__(
            self, template, role_name=EC2_ROLE_NAME,
            profile_name=EC2_INSTANCE_PROFILE_NAME,
            log_policy_name=LOG_POLICY_NAME,
            log_group_name=LOG_GROUP_NAME,
            log_retention_days=LOG_RETENTION_DAYS):
        self.template = template
        self.role_name = role_name
        self.profile_name = profile_name
        self.log_policy_name = log_policy_name
        self.log_group_name = log_group_name
        self.log_retention_days = log_retention_days

    def attach(self):
        """Attached an IAM Role, IAM Policy, and EC2 Instance Profile to a
        CloudFormation template and returns the template."
        """
        self.template.add_resource(iam.Role(
            self.role_name,
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
            self.log_policy_name,
            PolicyName=self.log_policy_name,
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
            Roles=[Ref(self.role_name)]
        ))

        self.template.add_resource(iam.InstanceProfile(
            self.profile_name,
            Path="/",
            Roles=[Ref(self.role_name)]
        ))

        self.template.add_resource(LogGroup(
            self.log_group_name,
            RetentionInDays=self.log_retention_days
        ))

        return self.template


def main():
    """Generates a cloudformation template."""
    template = Template()
    template.add_version('2010-09-09')
    template.add_description('Create an IAM Role, IAM Policy, and EC2 '
                             'Instance Profile, and a CloudFormation log group '
                             'for EC2 Instances.')
    ec2_resources = EC2Resources(template)
    ec2_resources.attach()
    print template.to_json()


if __name__ == '__main__':
    main()
