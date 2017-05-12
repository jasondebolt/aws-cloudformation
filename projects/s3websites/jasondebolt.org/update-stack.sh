
# See https://github.com/matthew-andrews/s3-static-website-cloudformation/blob/master/stack.json
# Redirects all requests from www.domain.com bucket to domain.com bucket.



#aws cloudformation update-stack --stack-name jasondebolt-org \
#    --template-url https://s3-us-west-2.amazonaws.com/jasondebolt-cloud-formation/s3/s3_static_website.template \
#    --parameters ParameterKey=DomainName,ParameterValue=jasondebolt.org ParameterKey=IAMDeployUser,ParameterValue=jasondebolt
#
#aws cloudformation wait stack-update-complete --stack-name jasondebolt-org
#
#echo "Stack updated! Now uploading files to s3 bucket"

aws s3 cp index.html s3://jasondebolt.org
