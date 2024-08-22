from autogpt_server.data.block import Block, BlockSchema, BlockOutput
from autogpt_server.data.model import SchemaField

from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request

from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

class UpdateGoogleDocBlock(Block):
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/documents"]

    class Input(BlockSchema):
        document_id: str  # The ID of the Google Doc to update
        requests: list  # List of requests to perform the bulk update

    class Output(BlockSchema):
        updated: bool  # Indicates if the update was successful
        error: str = SchemaField(
            description="Error message if document update fails",
        )

    def __init__(self):
        super().__init__(
            id="e5f6a1b2-c3d4-7890-1234-367890abcdef",  # Unique ID for the block
            input_schema=UpdateGoogleDocBlock.Input,  # Assign input schema
            output_schema=UpdateGoogleDocBlock.Output,  # Assign output schema

            # Provide sample input, output, and test mock for testing the block
            test_input={"document_id": "1ljbv2jgs6lBB0_QQV9KLloaM4BltDeWVXBiHrf3e51Y",
                "requests": [
                    {
                        "insertText": {
                            "location": {
                                "index": 1,
                            },
                            "text": "Hello, world!"
                        }
                    }
                ]
            },
            test_output=[("updated", True)],  # Corrected test output format
        )

    def run(self, input_data: Input) -> BlockOutput:
        try:
            document_id = input_data.document_id
            requests = input_data.requests

            # Perform the bulk update on the Google Doc
            service = self.get_service()
            print(">>>>> Doc document_id: ", document_id)
            result = service.documents().batchUpdate(
                documentId=document_id,
                body={"requests": requests}
            ).execute()
            print(">>>>> Update result: ", result)

            yield "updated", True

        except HttpError as e:
            error_message = f"HTTP error occurred: {e}"
            print(error_message)
            yield "error", error_message

        except Exception as e:
            error_message = f"An error occurred: {e}"
            print(error_message)
            yield "error", error_message

    def get_service(self):
        try:
            credentials = service_account.Credentials.from_service_account_file(
                filename='./seamless-auto-gpt-13c700c536c2.json', 
                scopes=self.SCOPES
            )
            service = build('docs', 'v1', credentials=credentials)
            return service
        except Exception as e:
            print(f"Error occurred: {e}")
            return e