import aws_cdk as cdk

from aws_cdk.aws_codebuild import BuildEnvironmentVariable
from aws_cdk.aws_codebuild import BuildSpec
from aws_cdk.aws_codebuild import BuildEnvironment
from aws_cdk.aws_codebuild import EventAction
from aws_cdk.aws_codebuild import FilterGroup
from aws_cdk.aws_codebuild import LinuxBuildImage
from aws_cdk.aws_codebuild import Source
from aws_cdk.aws_codebuild import Project


class ContinuousIntegrationStack(cdk.Stack):

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        github = Source.git_hub(
            owner='keenangraham',
            repo='cdk-pipeline',
            webhook=True,
        )

        continuous_integration_project = Project(
            self,
            'ContinuousIntegrationProject',
            source=github,
            environment=BuildEnvironment(
                build_image=LinuxBuildImage.STANDARD_5_0,
                privileged=True,
            ),
            build_spec=BuildSpec.from_object(
                {
                    'version': '0.2',
                    'phases': {
                        'build': {
                            'commands': [
                                'echo CI',
                                'echo $TEST',
                            ]
                        }
                    }
                }
            ),
            environment_variables={
                'TEST': BuildEnvironmentVariable(
                    value='SOMETHING!'
                )
            },
            badge=True,
        )
