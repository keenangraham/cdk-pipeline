import aws_cdk as cdk

from aws_cdk.aws_chatbot import SlackChannelConfiguration


class NotificationStack(cdk.Stack):

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        self.chatbot = SlackChannelConfiguration(
            self,
            'aws-chatbot',
            slack_channel_configuration_name='aws-chatbot',
            slack_workspace_id='T1KMV4JJZ',
            slack_channel_id='C034GTRCCLU',
        )
