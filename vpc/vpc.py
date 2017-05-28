from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output, If, And, Not, Or, Equals, Condition
from troposphere import Parameter, Ref, Tags, Template, Export
from troposphere.cloudformation import Init
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.ec2 import PortRange
from troposphere.ec2 import Route
from troposphere.ec2 import EIP
from troposphere.ec2 import RouteTable
from troposphere.ec2 import Subnet
from troposphere.ec2 import SubnetRouteTableAssociation
from troposphere.ec2 import NatGateway
from troposphere.ec2 import VPC
from troposphere.ec2 import InternetGateway
from troposphere.ec2 import VPCGatewayAttachment


t = Template()

t.add_version("2010-09-09")

t.add_description("""\
Creates 1 VPC, 2 public subnets, 2 private subnets, 1 network ACL, 2 NAT gateways, 1 Internet Gateway, 4 route tables (2 public (1 is created by default), 2 private), 2 elastic IPs (one for each NAT gateway), and 1 default VPC security group. Each private subnet gets its own NAT gateway, which costs about 5 cents each per hour. The public subnet is attached to an internet gateway.""")
CIDRRange = t.add_parameter(Parameter(
    "CIDRRange",
    Default="10.40.0.0",
    Type="String",
    Description="VPCCIDR Range (will be a /16 block)",
    AllowedValues=["10.0.0.0", "10.40.0.0", "10.80.0.0"],
))

t.add_mapping("VPCRanges",
{u'10.0.0.0': {u'PrivateSubnetAZ1': u'10.0.2.0/24',
               u'PrivateSubnetAZ2': u'10.0.3.0/24',
               u'PublicSubnetAZ1': u'10.0.0.0/24',
               u'PublicSubnetAZ2': u'10.0.1.0/24'},
 u'10.40.0.0': {u'PrivateSubnetAZ1': u'10.40.2.0/24',
                u'PrivateSubnetAZ2': u'10.40.3.0/24',
                u'PublicSubnetAZ1': u'10.40.0.0/24',
                u'PublicSubnetAZ2': u'10.40.1.0/24'},
 u'10.80.0.0': {u'PrivateSubnetAZ1': u'10.80.2.0/24',
                u'PrivateSubnetAZ2': u'10.80.3.0/24',
                u'PublicSubnetAZ1': u'10.80.0.0/24',
                u'PublicSubnetAZ2': u'10.80.1.0/24'}}
)

NATAZ2Route = t.add_resource(Route(
    "NATAZ2Route",
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref("RouteTablePrivateAZ2"),
    NatGatewayId=Ref("NATAZ2"),
))

NATAZ1Route = t.add_resource(Route(
    "NATAZ1Route",
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref("RouteTablePrivateAZ1"),
    NatGatewayId=Ref("NATAZ1"),
))

EIPNATAZ2 = t.add_resource(EIP(
    "EIPNATAZ2",
    Domain="vpc",
))

RouteTablePublic = t.add_resource(RouteTable(
    "RouteTablePublic",
    VpcId=Ref("VPCBase"),
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), "-PublicRT"]),
    ),
))

PublicNetAZ2 = t.add_resource(Subnet(
    "PublicNetAZ2",
    VpcId=Ref("VPCBase"),
    AvailabilityZone=Select("1", GetAZs(Ref("AWS::Region"))),
    CidrBlock=FindInMap("VPCRanges", Ref(CIDRRange), "PublicSubnetAZ2"),
    MapPublicIpOnLaunch="True",
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), "-PublicAZ2"]),
    ),
))

RouteAssociationPrivateAZ2Default = t.add_resource(SubnetRouteTableAssociation(
    "RouteAssociationPrivateAZ2Default",
    SubnetId=Ref("PrivateNetAZ2"),
    RouteTableId=Ref("RouteTablePrivateAZ2"),
))

NATAZ1 = t.add_resource(NatGateway(
    "NATAZ1",
    SubnetId=Ref("PublicNetAZ1"),
    AllocationId=GetAtt("EIPNATAZ1", "AllocationId"),
    DependsOn="IGWBaseAttachment",
))

EIPNATAZ1 = t.add_resource(EIP(
    "EIPNATAZ1",
    Domain="vpc",
))

RouteAssociationPublicAZ1Default = t.add_resource(SubnetRouteTableAssociation(
    "RouteAssociationPublicAZ1Default",
    SubnetId=Ref("PublicNetAZ1"),
    RouteTableId=Ref(RouteTablePublic),
))

RouteAssociationPrivateAZ1Default = t.add_resource(SubnetRouteTableAssociation(
    "RouteAssociationPrivateAZ1Default",
    SubnetId=Ref("PrivateNetAZ1"),
    RouteTableId=Ref("RouteTablePrivateAZ1"),
))

VPCBase = t.add_resource(VPC(
    "VPCBase",
    EnableDnsSupport="True",
    CidrBlock=Join("", [Ref(CIDRRange), "/16"]),
    EnableDnsHostnames="True",
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), "-VPC"]),
    ),
))

PublicNetAZ1 = t.add_resource(Subnet(
    "PublicNetAZ1",
    VpcId=Ref(VPCBase),
    AvailabilityZone=Select("0", GetAZs(Ref("AWS::Region"))),
    CidrBlock=FindInMap("VPCRanges", Ref(CIDRRange), "PublicSubnetAZ1"),
    MapPublicIpOnLaunch="True",
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), "-PublicAZ1"]),
    ),
))

NATAZ2 = t.add_resource(NatGateway(
    "NATAZ2",
    SubnetId=Ref(PublicNetAZ2),
    AllocationId=GetAtt(EIPNATAZ2, "AllocationId"),
    DependsOn="IGWBaseAttachment",
))

RoutePublicDefault = t.add_resource(Route(
    "RoutePublicDefault",
    GatewayId=Ref("IGWBase"),
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref(RouteTablePublic),
    DependsOn=["IGWBaseAttachment"],
))

RouteAssociationPublicAZ2Default = t.add_resource(SubnetRouteTableAssociation(
    "RouteAssociationPublicAZ2Default",
    SubnetId=Ref(PublicNetAZ2),
    RouteTableId=Ref(RouteTablePublic),
))

PrivateNetAZ1 = t.add_resource(Subnet(
    "PrivateNetAZ1",
    VpcId=Ref(VPCBase),
    AvailabilityZone=Select("0", GetAZs(Ref("AWS::Region"))),
    CidrBlock=FindInMap("VPCRanges", Ref(CIDRRange), "PrivateSubnetAZ1"),
    MapPublicIpOnLaunch="False",
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), "-PrivateAZ1"]),
        Network="private",
    ),
))

PrivateNetAZ2 = t.add_resource(Subnet(
    "PrivateNetAZ2",
    VpcId=Ref(VPCBase),
    AvailabilityZone=Select("1", GetAZs(Ref("AWS::Region"))),
    CidrBlock=FindInMap("VPCRanges", Ref(CIDRRange), "PrivateSubnetAZ2"),
    MapPublicIpOnLaunch="False",
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), "-PrivateAZ2"]),
        Network="private",
    ),
))

IGWBase = t.add_resource(InternetGateway(
    "IGWBase",
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), "-IGW"]),
    ),
))

RouteTablePrivateAZ1 = t.add_resource(RouteTable(
    "RouteTablePrivateAZ1",
    VpcId=Ref(VPCBase),
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), "-PrivateAZ1RT"]),
    ),
))

IGWBaseAttachment = t.add_resource(VPCGatewayAttachment(
    "IGWBaseAttachment",
    VpcId=Ref(VPCBase),
    InternetGatewayId=Ref(IGWBase),
))

RouteTablePrivateAZ2 = t.add_resource(RouteTable(
    "RouteTablePrivateAZ2",
    VpcId=Ref(VPCBase),
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), "-PrivateAZ2RT"]),
    ),
))

VPCID = t.add_output(Output(
    "VPCID",
    Value=Ref(VPCBase),
    Export=Export(Join("", [Ref("AWS::StackName"), "-VPCID"]))
))

SubnetPublicAZ1 = t.add_output(Output(
    "SubnetPublicAZ1",
    Value=Ref(PublicNetAZ1),
    Export=Export(Join("", [Ref("AWS::StackName"), "-SubnetPublicAZ1"]))
))

SubnetPrivateAZ1 = t.add_output(Output(
    "SubnetPrivateAZ1",
    Value=Ref(PrivateNetAZ1),
    Export=Export(Join("", [Ref("AWS::StackName"), "-SubnetPrivateAZ1"]))
))

ElasticIP1 = t.add_output(Output(
    "ElasticIP1",
    Value=Ref(EIPNATAZ1),
    Export=Export(Join("", [Ref("AWS::StackName"), "-ElasticIP1"]))
))

ElasticIP2 = t.add_output(Output(
    "ElasticIP2",
    Value=Ref(EIPNATAZ2),
    Export=Export(Join("", [Ref("AWS::StackName"), "-ElasticIP2"]))
))

SubnetPublicAZ2 = t.add_output(Output(
    "SubnetPublicAZ2",
    Value=Ref(PublicNetAZ2),
    Export=Export(Join("", [Ref("AWS::StackName"), "-SubnetPublicAZ2"]))
))

DefaultSG = t.add_output(Output(
    "DefaultSG",
    Value=GetAtt(VPCBase, "DefaultSecurityGroup"),
    Export=Export(Join("", [Ref("AWS::StackName"), "-DefaultSG"]))
))

SubnetPrivateAZ2 = t.add_output(Output(
    "SubnetPrivateAZ2",
    Value=Ref(PrivateNetAZ2),
    Export=Export(Join("", [Ref("AWS::StackName"), "-SubnetPrivateAZ2"]))
))

print(t.to_json())
