from constructs import Construct
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_s3_deployment as s3_deployment,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    #aws_certificatemanager as certmgr,
    #aws_route53 as route53,
    Aws,
    Aspects, RemovalPolicy
)
import cdk_nag

class ECorpWebsiteStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, wafacl: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        waf_id = f'arn:aws:wafv2:us-east-1:{Aws.ACCOUNT_ID}:global/webacl/waf-cloudfront/{wafacl}'
        
        s3_log = s3.Bucket(
                    self, "EcorpWebsiteLogs", # name og the access logs bucket 
                    access_control=s3.BucketAccessControl.LOG_DELIVERY_WRITE,
                    removal_policy=RemovalPolicy.DESTROY,  # deletes bucket when stack is removed
                    encryption=s3.BucketEncryption.KMS_MANAGED,
                    block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                    public_read_access=False,    # Buckety encryption
                    enforce_ssl=True
                )

        # S3 bucket for static website hosting
        website_bucket = s3.Bucket(
            self, id="ecorp-website",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            public_read_access=False,
            removal_policy=RemovalPolicy.DESTROY,
            server_access_logs_bucket=s3_log,
            server_access_logs_prefix="S3_StaticWebsite"
        )
        # arn = f"{Aws.ACCOUNT_ID}__WAFarn"
        #  WAF
        #Fn.import_value("EcorpWAF-WafCloudFrontStack:WafAclArn")

        #  S3 bucket --> CloudFront
        bucket_origin_access_identity = cloudfront.OriginAccessIdentity(self, "OriginAccessIdentity")
        website_bucket.grant_read(bucket_origin_access_identity)

        # CloudFront distribution

        # my_hosted_zone = route53.HostedZone(
        #     self, "HostedZone",
        #     zone_name="example.com"
        # )
        # certificate = certmgr.Certificate(
        #     self, "Certificate",
        #     domain_name="www.example.com",
        #     validation=certmgr.CertificateValidation.from_dns(my_hosted_zone)
        # )
        cloudfront_distribution = cloudfront.Distribution(
            self, 
            "EcorpDistribution",
            default_root_object="index.html",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(website_bucket, origin_access_identity=bucket_origin_access_identity),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
                
            ),
            web_acl_id=waf_id,
            log_bucket=s3_log,
            log_file_prefix="cf_StatickLogs",
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2018,
            # certificate=certificate,
            # domain_names=["www.example.com"]    
        )

        # S3 bucket deployment
        website_bucket_deployment = s3_deployment.BucketDeployment(
            self, "DeployECorpWebsite",
            sources=[s3_deployment.Source.asset("main/frontend/dist/")],
            destination_bucket=website_bucket,
            distribution=cloudfront_distribution,
        )

        # Depend on S3 bucket for bucket deployment
        website_bucket_deployment.node.add_dependency(website_bucket)
        #security check 
        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())
        cdk_nag.NagSuppressions.add_stack_suppressions(self, [
        {"id":"AwsSolutions-S1", "reason":"Login bucket do not require Access logs "},
        {"id":"AwsSolutions-S10", "reason":"Cloud front is going to handle the encription using SSL"},
        {"id":"AwsSolutions-IAM5", "reason":"ERROR: The IAM user, role, or group uses AWS managed policies. An AWS managed policy is a standalone policy that is created and admini stered by AWS. Currently, many AWS managed policies do not restrict resource scope. Repla ce AWS managed policies with system specific (customer) managed policies. This is a granu lar rule that returns individual findings that can be suppressed with appliesTo. The find ings are in the format Policy::<policy> for AWS managed policies. Example: appliesTo: ['P olicy::arn:<AWS::Partition>:iam::aws:policy/foo']"},
        {"id":"AwsSolutions-IAM4", "reason":"ERROR: The IAM user, role, or group uses AWS managed policies. An AWS managed policy is a standalone policy that is created and admini stered by AWS. Currently, many AWS managed policies do not restrict resource scope. Repla ce AWS managed policies with system specific (customer) managed policies. This is a granu lar rule that returns individual findings that can be suppressed with appliesTo. The find ings are in the format Policy::<policy> for AWS managed policies. Example: appliesTo: ['P olicy::arn:<AWS::Partition>:iam::aws:policy/foo']"},
        {"id":"AwsSolutions-CFR1", "reason":"This is cause by the Geo restrictions been part of the WAF/cloudfront_stack.py "},
        {"id":"AwsSolutions-CFR4", "reason":"Please uncoment lines 51-60, 74, 75 To use a certificate and comply with CFR4 when the certificate are in place"},
        ])

        
