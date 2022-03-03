import aws_cdk as cdk

from aws_cdk.aws_codebuild import BuildEnvironmentVariable
from aws_cdk.aws_codebuild import BuildSpec
from aws_cdk.aws_codebuild import BuildEnvironment
from aws_cdk.aws_codebuild import EventAction
from aws_cdk.aws_codebuild import FilterGroup
from aws_cdk.aws_codebuild import LinuxBuildImage
from aws_cdk.aws_codebuild import Project
from aws_cdk.aws_codebuild import ReportGroup
from aws_cdk.aws_codebuild import Source


class ContinuousIntegrationStack(cdk.Stack):

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        github = Source.git_hub(
            owner='keenangraham',
            repo='cdk-pipeline',
            webhook=True,
        )

        unit_test_report_group = ReportGroup(
            self, 'PytestUnitTestReportGroup'
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
                        'install': {
                            'runtime-versions': {
                                'python': '3.9',
                            },
                            'commands': [
                                'echo $CODEBUILD_RESOLVED_SOURCE_VERSION',
                                'echo $CODEBUILD_SOURCE_REPO_URL',
                                'echo $CODEBUILD_WEBHOOK_EVENT',
                                'echo $CODEBUILD_WEBHOOK_TRIGGER',
                                'echo $(git log -1 --pretty="%s (%h) - %an")',
                                'pip3 install -r requirements-dev.txt',
                            ]
                        },
                        'build': {
                            'commands': [
                                'ls',
                                'echo CI',
                                'echo $TEST',
                                'python -m pytest --junitxml=pytest_report.xml',
                            ]
                        }
                    },
                    'reports': {
                        unit_test_report_group.report_group_arn: {
                            'files': 'pytest_report.xml',
                            'file_format': 'JUNITXML',
                        }
                    },
                }
            ),
            environment_variables={
                'TEST': BuildEnvironmentVariable(
                    value='SOMETHING!'
                )
            },
            badge=True,
        )
