import aws_cdk as cdk
from constructs import Construct
from DockerBuild.Base import Base
from DockerBuild.Pipeline import Pipeline
from DockerBuild.DockerDeploy_Stack import DockerDeploy
from properties import props
class DockerCD_Stage(cdk.Stage):
     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.props = props()
        base = Base(self, f"{self.props['namespace']}-base", self.props)

        # pipeline stack
        pipeline = Pipeline(self, f"{self.props['namespace']}-pipeline", base.outputs)
        pipeline.add_dependency(base)
        # image deploy
        DockerDeploy(self, "ECSDockerBuild", base.outputs)