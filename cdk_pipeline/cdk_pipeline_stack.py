import aws_cdk as cdk

from aws_cdk.pipelines import ArtifactMap
from aws_cdk.pipelines import CodePipeline
from aws_cdk.pipelines import CodePipelineSource
from aws_cdk.pipelines import ShellStep

from aws_cdk.aws_codepipeline import StagePlacement

from aws_cdk.aws_codepipeline_actions import ManualApprovalAction
from aws_cdk.aws_codepipeline_actions import CodeBuildAction
from aws_cdk.aws_codepipeline_actions import LambdaInvokeAction

from aws_cdk.aws_codebuild import PipelineProject
from aws_cdk.aws_codebuild import BuildSpec
from aws_cdk.aws_codebuild import BuildEnvironment
from aws_cdk.aws_codebuild import LinuxBuildImage

from aws_cdk.aws_lambda import Code
from aws_cdk.aws_lambda import Function
from aws_cdk.aws_lambda import Runtime

from cdk_pipeline.continuous_integration_stack import ContinuousIntegrationStack

from cdk_pipeline.naming import prepend_branch_name
from cdk_pipeline.naming import prepend_project_name


class ContinuousIntegrationStage(cdk.Stage):

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id,  **kwargs)
        ContinuousIntegrationStack(
            self,
            prepend_project_name(
                'CIStack'
            )
        )


class CdkPipelineStack(cdk.Stack):

    def __init__(self, scope, construct_id, chatbot=None, branch=None, **kwargs):
        super().__init__(scope, construct_id,  **kwargs)
        github = CodePipelineSource.connection(
            'keenangraham/cdk-pipeline',
            'main',
            connection_arn=(
                'arn:aws:codestar-connections:'
                'us-east-1:618537831167:'
                'connection/28ec4d05-97dd-4730-b41c-b3b698b2a485'
            )
        )
        synth = ShellStep(
            'Synth',
            input=github,
            env={
                'BRANCH': branch
            },
            commands=[
                'npm install -g aws-cdk',
                'python -m pip install -r requirements.txt',
                'cdk synth -c branch=$BRANCH',
            ]
        )
        code_pipeline = CodePipeline(
            self,
            prepend_branch_name(
                branch,
                'CodePipeline',
            ),
            synth=synth
        )
        ci_stage = ContinuousIntegrationStage(
            self,
            'ContinuousIntegrationStage'
        )
        code_pipeline.add_stage(
            ci_stage
        )
        custom_step = ShellStep(
            'EchoStep',
            commands=[
                'echo hello',
                'ls',
            ]
        )
        wave = code_pipeline.add_wave(
            'TestWave',
            pre=[
                custom_step
            ]
        )

        # Can't modify high-level CodePipeline after build.
        code_pipeline.build_pipeline()

        #Low-level pipeline.
        pipeline = code_pipeline.pipeline

        custom_action = ManualApprovalAction(
            action_name="ShouldRun",
        )

        inserted_stage = pipeline.add_stage(
            stage_name='InsertedStage',
            placement=StagePlacement(
                right_before=pipeline.stage(
                    'TestWave'
                )
            ),
            actions=[
                custom_action,
            ],
        )

        unit_test_project = PipelineProject(
            self,
            'UnitTests',
            environment=BuildEnvironment(
                build_image=LinuxBuildImage.STANDARD_5_0,
                privileged=True,
            ),
            build_spec=BuildSpec.from_object(
                {
                    'version': '0.2',
                    'phases': {
                        'install': {
                            'commands': [
                                'echo hello from install',
                            ],
                        },
                        'build': {
                            'commands': [
                                'echo CODEBUILD!',
                                'ls',
                                'git clone https://github.com/IGVF-DACC/igvfd.git',
                                'cd igvfd',
                                'ls',
                                'docker-compose version',
                                'cat docker-compose.test.yml',
                                'docker-compose -f docker-compose.test.yml up --exit-code-from pyramid',
                            ]
                        }
                    }
                }
            )
        )

        random_lambda = Function(
            self, 'RandomLambda',
            runtime=Runtime.NODEJS_14_X,
            handler='index.handler',
            code=Code.from_inline(
                (
                    "exports.handler = function (event, context) {"
                        "console.log('HELLO');"
                        "console.log(event);"
                        "var AWS = require('aws-sdk');"
                        "var codepipeline = new AWS.CodePipeline();"
                        "var jobId = event['CodePipeline.job'].id;"
                        "codepipeline.putJobSuccessResult({ jobId });"
                        "context.succeed('DONE!');"
                    "}"
                )
            )
        )

        lambda_action = LambdaInvokeAction(
            action_name='RunRandomLambda',
            lambda_=random_lambda,
        )

        artifact_map = ArtifactMap()

        github_artifact = artifact_map.to_code_pipeline(
            github.primary_output
        )

        test_action = CodeBuildAction(
            action_name='RunUnitTests',
            project=unit_test_project,
            input=github_artifact,
        )

        test_stage = pipeline.add_stage(
            stage_name='RunTestStage',
            placement=StagePlacement(
                just_after=pipeline.stage(
                    'TestWave'
                )
            ),
            actions=[
                test_action,
                lambda_action,
            ]
        )

        if chatbot is not None:
            rule = pipeline.notify_on_execution_state_change(
                'NotifySlack',
                chatbot,
            )
