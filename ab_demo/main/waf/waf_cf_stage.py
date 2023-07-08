import aws_cdk as cdk
from constructs import Construct
from main.waf.waf_cloudfront import WafCloudFrontStack

class WAF_Satege(cdk.Stage):
     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        WafCloudFrontStack(
            self, "WafCloudFrontStack"
        )