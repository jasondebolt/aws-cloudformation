from troposphere import Template, Ref
import troposphere.iam as iam

t = Template()
t.add_version("2010-09-09")
t.add_description("iam role example")

SampleRole = t.add_resource(iam.Role(
    "SampleRole",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "Service": ["ec2.amazonaws.com", "codedeploy.amazonaws.com"]
            },
            "Action": ["sts:AssumeRole"]
        }]
    },
    ManagedPolicyArns=[
        "arn:aws:iam::aws:policy/AmazonS3FullAccess",
        "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole",
    ],
    Path="/"
))

## PolicyRole
SampleDescribeInstancesPolicy = t.add_resource(iam.PolicyType(
    "SampleDescribeInstancesPolicy",
    PolicyName="SampleDescribeInstancesPolicy",
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
    Roles=[Ref("SampleRole")]
))
SampleRoleInstanceProfile = t.add_resource(iam.InstanceProfile(
    "SampleRoleInstanceProfile",
    Path="/",
    Roles=[Ref("SampleRole")]
))

print(t.to_json())
