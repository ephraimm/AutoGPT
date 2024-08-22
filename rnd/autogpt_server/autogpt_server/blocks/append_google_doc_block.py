from autogpt_server.data.block import Block, BlockSchema, BlockOutput
from autogpt_server.data.model import SchemaField

from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request

from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

class AppendTextGoogleDocBlock(Block):
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/documents"]

    class Input(BlockSchema):
        document_id: str  # The ID of the Google Doc to update
        text: str  # Text to append to the document

    class Output(BlockSchema):
        updated: bool  # Indicates if the update was successful
        error: str = SchemaField(
            description="Error message if document update fails",
        )

    def __init__(self):
        super().__init__(
            id="e5f6a1b2-c3d4-7890-1234-567890abcdef",  # Unique ID for the block
            input_schema=AppendTextGoogleDocBlock.Input,  # Assign input schema
            output_schema=AppendTextGoogleDocBlock.Output,  # Assign output schema

            # Provide sample input, output, and test mock for testing the block
            test_input={"document_id": "1ljbv2jgs6lBB0_QQV9KLloaM4BltDeWVXBiHrf3e51Y", "text": "Hello, world!"},
            test_output=[("updated", True)],  # Corrected test output format
        )

    def run(self, input_data: Input) -> BlockOutput:
        try:
            document_id = input_data.document_id
            text = input_data.text

            # Retrieve the document to find the end index
            service = self.get_service()
            document = service.documents().get(documentId=document_id).execute()
            end_index = self.find_end_index(document)

            new_elements, new_text_length, explanation = manipulate_text(paragraph_elements)

            append_text_runs_to_document(document_id,new_elements)
            

            #  # Create a request to insert text at the end of the document
            # requests = [
            #     {
            #         'insertText': {
            #             'location': {
            #                 'index': end_index - 1,  # Adjusted to insert before the very last element
            #             },
            #             'text': text + '\n'  # Assuming you want the text to be in a new paragraph
            #         }
            #     }
            # ]

            # # Perform the update on the Google Doc
            # result = service.documents().batchUpdate(
            #     documentId=document_id,
            #     body={"requests": requests}
            # ).execute()
            # print(">>>>> Update result: ", result)

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

    def find_end_index(self, document):
        # Find the end index of the document
        content = document.get('body').get('content')
        if content:
            last_element = content[-1]
            end_index = last_element.get('endIndex')
        else:
            end_index = 1
        print(">>>>> End index: ", end_index)
        return end_index
    #  @title format markdown for google docs


    def markdown_to_text_runs_advanced(markdown_text):
        # Initialize state variables
        is_bold = False
        is_italic = False
        buffer = ""
        text_len = 0
        text_runs = []

        # markdown_text += '\n'

        i = 0
        while i < len(markdown_text):
            # Check for markdown characters and adjust state accordingly
            if markdown_text[i:i+3] == "***":  # Bold and Italic
                if not is_bold and not is_italic:  # Start of bold and italic
                    if buffer:
                        text_runs.append({"content": buffer, "textStyle": {"bold": is_bold, "italic": is_italic}})
                        buffer = ""
                    is_bold = is_italic = True
                else:  # End of bold and italic
                    text_runs.append({"content": buffer, "textStyle": {"bold": is_bold, "italic": is_italic}})
                    buffer = ""
                    is_bold = is_italic = False
                i += 3
            elif markdown_text[i:i+2] == "**":  # Bold
                if not is_bold:
                    if buffer:
                        text_runs.append({"content": buffer, "textStyle": {"bold": is_bold, "italic": is_italic}})
                        buffer = ""
                    is_bold = True
                else:
                    text_runs.append({"content": buffer, "textStyle": {"bold": is_bold, "italic": is_italic}})
                    buffer = ""
                    is_bold = False
                i += 2
            elif markdown_text[i:i+1] == "*":  # Italic
                if not is_italic:
                    if buffer:
                        text_runs.append({"content": buffer, "textStyle": {"bold": is_bold, "italic": is_italic}})
                        buffer = ""
                    is_italic = True
                else:
                    text_runs.append({"content": buffer, "textStyle": {"bold": is_bold, "italic": is_italic}})
                    buffer = ""
                    is_italic = False
                i += 1
            elif markdown_text[i:i+3] == "###":  # Heading 1
                if buffer:
                    text_runs.append({"content": buffer, "textStyle": {"bold": is_bold, "italic": is_italic}})
                    buffer = ""
                i += 3
                # Capture the heading content
                heading_buffer = ""
                while i < len(markdown_text) and markdown_text[i] != '\n':
                    heading_buffer += markdown_text[i]
                    i += 1
                text_runs.append({"content": heading_buffer, "textStyle": {"namedStyleType": "HEADING_1"}})
            else:
                buffer += markdown_text[i]
                text_len += len(markdown_text[i])
                i += 1

        # Append any remaining text
        if buffer:
            text_runs.append({"content": buffer, "textStyle": {"bold": is_bold, "italic": is_italic}})

        return text_runs, text_len
        
    def append_text_runs_to_document(document_id, text_runs):
        # Fetch the document's current end index and adjust for insertion
        end_index = get_document_end_index(document_id) - 1
        # if len(text_runs[0]['textRun']['content']) == 0: return


        requests = []
        for para in text_runs:
            if 'pageBreak' in para:
                requests.append({
                    'insertPageBreak': {
                        'endOfSegmentLocation': {}
                        # 'location': {
                        #     'index': end_index,
                        # },
                        # 'text': text_to_insert
                    }
                })
            else:
                run = para['textRun'] if 'textRun' in para else para
                text_length = len(run['content']) + 1  # +1 for the newline character if it's added
                text_to_insert = run['content'] + ('\n' if run is text_runs[-1] else '')

                requests.append({
                    'insertText': {
                        'location': {
                            'index': end_index,
                        },
                        'text': text_to_insert
                    }
                })
                if 'textStyle' in run:
                    # Assumes the end index is updated to reflect the new end of the document after each insertion
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': end_index,  # Start index of the newly inserted text
                                'endIndex': end_index + text_length - 1,  # End index of the newly inserted text, to be calculated
                            },
                            'textStyle': run['textStyle'],
                            'fields': 'bold,italic'
                        }
                    })

                # Update end_index for the next iteration. The new end index needs to account for
                # the text just inserted.
                end_index += text_length - 1

            # requests_json = json.dumps(requests, indent=4)
            # print(requests_json)

            # Here you would use the Google Docs API service to send the batchUpdate request
            service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
            return True

    def manipulate_text(elements):
        """Manipulate the text of a paragraph and preserve formatting."""
        original_text = ''
        for elem in elements:
            text_run = elem.get('textRun')
            if not text_run:
                continue

            content = text_run.get('content', '').replace('\n','')
            text_style = text_run.get('textStyle', {})

            # Check for both bold and italic and apply Markdown accordingly
            if text_style.get('bold') and text_style.get('italic'):
                content = f"***{content}***"
            elif text_style.get('bold'):
                content = f"**{content}**"
            elif text_style.get('italic'):
                content = f"*{content}*"

            original_text += content

            print(f"original_text: {original_text}")
            if len(original_text.strip("*")):
                translated_words = hebrew_words.update_and_report_existing(original_text)
                # edited = get_gpt_remove_descriptions(original_text, translated_words)
                edited = get_gpt4_ai_edits(original_text, translated_words)
                print(edited)
                text_runs, text_len = markdown_to_text_runs_advanced(edited['edited_text'].replace('\n\n','\n'))
                return text_runs, text_len, edited.get('explanation',[])
            else:
                return elements, 0, []