from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output, If, And, Not, Or, Equals, Condition
from troposphere import Parameter, Ref, Tags, Template
from troposphere.iam import Role, InstanceProfile
from troposphere.ec2 import SecurityGroup
from troposphere.logs import LogGroup
from awacs.aws import Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole
import header
import ec2_mappings


t = Template()
t.add_version("2010-09-09")
t.add_description("Creates resources for viewing CloudFormation logs of EC2 instances.")
t = ec2_mappings.attachMappings(t)


t.add_resource(Role(
    "LogRole",
    RoleName="LogRole",
    Policies=[
        Policy(
            PolicyName="LogRolePolicy",
            PolicyDocument={
                "Version": "2012-10-17",
                "Statement": [
                    {"Action": [
                       "logs:CreateLogGroup",
                       "logs:CreateLogStream",
                       "logs:PutLogEvents",
                       "logs:DescribeLogStreams"
                     ],
                     "Resource": [Join("", [FindInMap("Region2ARNPrefix", Ref("AWS::Region"), "ARNPrefix"), "logs:*:*:*"])],
                     "Effect": "Allow"
                     }
                ]
            }
        )
    ],
    AssumeRolePolicyDocument=Policy(
        Statement=[
            Statement(
                Effect=Allow,
                Action=[AssumeRole],
                Principle=Principle("Service", ["ec2.amazonaws.com"])
            )
        ]
    )

))

t.add_resource(LogGroup(
    "CloudFormationLogs",
    RetentionInDays=7,
))

t.add_resource(InstanceProfile(
    "LogRoleInstanceProfile",
    Roles=["LogRole"],
    InstanceProfileName="LogRoleInstanceProfile",
))

print(t.to_json())
