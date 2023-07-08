import os
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ecr as ecr,
    aws_cloudtrail as cloudtrail,
    aws_logs as logs,
    aws_securityhub as securityhub,
    Aspects, Aws
)
from properties import props
import cdk_nag
class ComponentsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.props = props()
        trail = cloudtrail.Trail(self, "ECorp-CloudTrail",
            send_to_cloud_watch_logs=True,
            cloud_watch_logs_retention=logs.RetentionDays.ONE_MONTH,
            #is_organization_trail=True
        )

        sechub = securityhub.CfnHub(self, "EcorpSecHub")
        
        # Security Scan
        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())
        cdk_nag.NagSuppressions.add_stack_suppressions(self, [
            {"id":"AwsSolutions-IAM5", "reason": "ERROR: The IAM user, role, or group uses AWS managed policies. An AWS managed policy is a standalone policy that is created and admini stered by AWS. Currently, many AWS managed policies do not restrict resource scope. Repla ce AWS managed policies with system specific (customer) managed policies. This is a granu lar rule that returns individual findings that can be suppressed with appliesTo. The find ings are in the format Policy::<policy> for AWS managed policies. Example: appliesTo: ['P olicy::arn:<AWS::Partition>:iam::aws:policy/foo']"},
            {"id":"AwsSolutions-S1", "reason":" Bucket is mnage by CDK login configurations"},
            {"id":"AwsSolutions-S2", "reason":" Bucket is mnage by CDK login configurations"}
           ])
