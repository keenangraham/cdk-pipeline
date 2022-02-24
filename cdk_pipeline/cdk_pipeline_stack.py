import aws_cdk as cdk

from aws_cdk.pipelines import CodePipeline
from aws_cdk.pipelines import CodePipelineSource
from aws_cdk.pipelines import ShellStep

from aws_cdk.aws_codepipeline import StagePlacement
from aws_cdk.aws_codepipeline_actions import ManualApprovalAction
from aws_cdk.aws_chatbot import SlackChannelConfiguration

class CdkPipelineStack(cdk.Stack):

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
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
            commands=[
                'npm install -g aws-cdk',
                'python -m pip install -r requirements.txt',
                'cdk synth',
            ]
        )
        code_pipeline = CodePipeline(
            self,
            'Pipeline',
            synth=synth
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
                    'Build'
                )
            ),
            actions=[
                custom_action,
            ],
        )

        # Notify Slack with pipeline stages.
        target = SlackChannelConfiguration(
            self,
            'aws-chatbot',
            slack_channel_configuration_name='aws-chatbot',
            slack_workspace_id='T1KMV4JJZ',
            slack_channel_id='C034GTRCCLU',
        )
        rule = pipeline.notify_on_execution_state_change(
            'NotifySlack',
            target,
        )
