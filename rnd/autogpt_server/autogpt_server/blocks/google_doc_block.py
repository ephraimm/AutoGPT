from autogpt_server.data.block import Block, BlockSchema, BlockOutput
from autogpt_server.data.model import SchemaField

from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request

from google.oauth2.credentials import Credentials

class GetGoogleDocContentBlock(Block):
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/documents"]

    class Input(BlockSchema):
        document_id: str  # The ID of the Google Doc to retrieve content from

    class Output(BlockSchema):
        title: str  # The title of the Google Doc
        content: list  # The entire content of the Google Doc
        error: str = SchemaField(
            description="Error message if document retrieval fails",
        )

    def __init__(self):
        super().__init__(
            id="a1b2c3d4-e5f6-7890-1234-567890abcdef",  # Unique ID for the block
            input_schema=GetGoogleDocContentBlock.Input,  # Assign input schema
            output_schema=GetGoogleDocContentBlock.Output,  # Assign output schema

            # Provide sample input, output, and test mock for testing the block
            test_input={"document_id": "1ljbv2jgs6lBB0_QQV9KLloaM4BltDeWVXBiHrf3e51Y"},
            test_output=[("content", list({}))],  # Corrected test output format
            # test_mock=GetGoogleDocContentBlock.mock,
        
        )

    def run(self, input_data: Input) -> BlockOutput:
        try:
            document_id = input_data.document_id

            # Retrieve the Google Doc content 
            service = self.get_service()
            print(">>>>> Doc document_id: ", document_id)
            document = service.documents().get(documentId=document_id).execute()
            print(">>>>> Doc content: ", document)

            content = self.extract_text(document)
            
            yield "title", document.get('title')
            yield "content", content

        except Exception as e:
            print(f"Error occurred: {e}")
            yield "error", str(e)

    def get_service(self):
        try:
            credentials = service_account.Credentials.from_service_account_file(
                                filename='./seamless-auto-gpt-13c700c536c2.json', 
                                scopes=self.SCOPES)
            service = build('docs', 'v1', credentials=credentials)
            return service
        except Exception as e:
            print(f"Error occurred: {e}")
            return e
        

    def extract_text(self, document):
        # Extract and concatenate all text from the document content
        content = document.get('body').get('content')
        # text_content = ''.join([element.get('textRun', {}).get('content', '') for element in content if 'textRun' in element])
        return content