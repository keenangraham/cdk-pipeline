import aws_cdk as cdk
import aws_cdk.aws_chatbot as chatbot
from constructs import Construct

class ChatBot(Construct):

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        self.target = chatbot.SlackChannelConfiguration(
            self,
            'ChatBotChannel',
            slack_channel_configuration_name='aws-chatbot',
            slack_workspace_id='T1KMV4JJZ',
            slack_channel_id='C034GTRCCLU',
        )
