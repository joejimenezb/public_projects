import aws_cdk as cdk
from constructs import Construct
from main.frontend.website_stack import ECorpWebsiteStack
class WebsiteStage(cdk.Stage):
     def __init__(self, scope: Construct, construct_id: str, arn_waf, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        websitestack = ECorpWebsiteStack( self, "ECWebsiteStack", 
                           wafacl= arn_waf)

