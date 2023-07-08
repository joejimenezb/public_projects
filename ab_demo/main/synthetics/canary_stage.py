import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (
    CfnMapping,
    aws_ssm as ssm,
)
from main.synthetics.canary_stack import CanaryStack

class CanaryStage(cdk.Stage):
     def __init__(self, scope: Construct, construct_id: str, stage: str, frb: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        
        CanaryStack(self, f"{stage}EcorpCanary", 
                    stage=stage,
                    frb=frb)