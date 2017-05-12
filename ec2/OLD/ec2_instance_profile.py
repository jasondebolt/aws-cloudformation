from troposphere import Template, Ref, Join, FindInMap
from troposphere.logs import LogGroup
from troposphere.iam import Role, InstanceProfile
from awacs.aws import Action, Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole
import ec2_mappings

t = Template()
t.add_description("Creates resources for viewing CloudFormation logs of EC2 instances.")
t = ec2_mappings.attachMappings(t)

policy = Policy(
    Version="2012-10-17",
    Id="Logs Permissions",
    Statement=[
        Statement(
            Sid="1",
            Effect=Allow,
            Principal=Principal("Service", FindInMap("Region2Principal", Ref("AWS::Region"), "EC2Principal")),
            Action=[
                Action("logs", "CreateLogGroup"),
                Action("logs", "CreateLogStream"),
                Action("logs", "PutLogEvents"),
                Action("logs", "DescribeLogStreams"),
            ],
            Resource=[Join("", [FindInMap("Region2ARNPrefix", Ref("AWS::Region"), "ARNPrefix"), "logs:*:*:*"])],
        ),
    ],
)

logrole = t.add_resource(Role(
    "logrole",
    AssumeRolePolicyDocument=policy,
  )
)

cfninstanceprofile = t.add_resource(InstanceProfile(
    "InstanceProfile",
    Roles=[Ref(logrole)]
))

t.add_resource(LogGroup(
    "CloudFormationLogs",
    RetentionInDays=7,
))

print(t.to_json())
