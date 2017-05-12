
# See https://github.com/matthew-andrews/s3-static-website-cloudformation/blob/master/stack.json
# Redirects all requests from www.domain.com bucket to domain.com bucket.

aws cloudformation create-stack --stack-name jasondebolt-org \
    --template-url https://s3-us-west-2.amazonaws.com/jasondebolt-cloud-formation/route53/s3_bucket_a_record_nested.template \
    --parameters ParameterKey=DomainName,ParameterValue=jasondebolt.org \
    ParameterKey=IAMDeployUser,ParameterValue=jasondebolt \
    ParameterKey=S3BucketWebsiteEndpoint,ParameterValue=s3-website-us-west-2.amazonaws.com \
    ParameterKey=S3BucketHostedZoneID,ParameterValue=Z3BJ6K6RIION7M

aws cloudformation wait stack-create-complete --stack-name jasondebolt-org

echo "Stack created! Now uploading files to s3 bucket"

aws s3 cp index.html s3://jasondebolt.org
