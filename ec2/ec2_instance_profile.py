"""Create an EC2 InstanceProfile resource using AWS CloudFormation.

Create an IAM Role, IAM Policy, and EC2 Instance Profile for EC2 Instances.
"""
from troposphere import Ref, Template
import troposphere.iam as iam


def attach_instance_profile(template):
    """Attached an IAM Role, IAM Policy, and EC2 Instance Profile to a
    CloudFormation template and returns the template."
    """
    template.add_resource(iam.Role(
        "EC2Role",
        AssumeRolePolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {
                    "Service": ["ec2.amazonaws.com", "opsworks.amazonaws.com"]
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
    template.add_resource(iam.PolicyType(
        "LogPolicy",
        PolicyName="LogPolicy",
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

    template.add_resource(iam.InstanceProfile(
        "EC2RoleInstanceProfile",
        Path="/",
        Roles=[Ref("EC2Role")]
    ))
    return template


def main():
    template = Template()
    template.add_version('2010-09-09')
    template.add_description('Create an IAM Role, IAM Policy, and EC2 '
                             'Instance Profile for EC2 Instances.')
    template = attach_instance_profile(template)
    print template.to_json()


if __name__ == '__main__':
    main()
