import aws_cdk as cdk

from aws_cdk.pipelines import CodePipeline
from aws_cdk.pipelines import CodePipelineSource
from aws_cdk.pipelines import ShellStep


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
        pipeline = CodePipeline(
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
        wave = pipeline.add_wave(
            'TestWave',
            pre=[
                custom_step
            ]
        )
