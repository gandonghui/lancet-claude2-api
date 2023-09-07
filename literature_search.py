from io import StringIO
import pandas as pd
import re
from chatpdf import ChatPDF
from find_sci import findSCI
from askyourpdf import AskYourPDF

class LiteratureSearch:
    def __init__(self, api_key):
        if 'sec_' in api_key:
            self.chat = ChatPDF(api_key)
        elif 'ask_' in api_key:
            self.chat = AskYourPDF(api_key)
        self.hub = findSCI()
    def md_table_to_array(self, input_string):
        data = []
        if '|' not in input_string:
            return data

        table_pattern = r'\|.*\|\n((?:\|.*\|\n*)*)'
        markdown_tables = re.findall(table_pattern, input_string)
        final_markdown_table = '\n'.join(markdown_tables)

        df = pd.read_csv(StringIO(final_markdown_table), sep="|", skipinitialspace=True)
        for index in range(df.shape[0]):
            data.append(df.iloc[index].dropna().to_numpy())
        return data

    def create_prompt_base_param(self, columns, rows=['']):
        if [''] == rows:
            prompt = f"Help me summarize the {', '.join(columns)} in the form of {len(columns)} columns and 2 rows; " \
                     f"If there is no relevant information, please fill in \"NA\" in the relevant column of the table."
        else:
            prompt = f"Help me summarize a table information of {len(rows)} rows and {len(columns)} columns based on " \
                     f"the document content, including:{', '.join(rows)}. The column information includes: " \
                     f"{', '.join(columns)}. If there is no relevant information, please fill in \"NA\" in the " \
                     f"relevant column of the table."
        return prompt

    def parse_file(self, prompt, item):
        ret = []
        item_type = self.hub.get_item_type(item)
        if 'local_pdf' == item_type:
            source_id = self.chat.generate_source_id_base_local_pdf(item)
        elif 'url' == item_type:
            source_id = self.chat.generate_source_id_baseurl(item)
        elif 'doi' == item_type:
            url = hub.get_pdfurl_base_doi(item)
            if '' == url:
                return ret
            source_id = self.chat.generate_source_id_baseurl(url)
        elif 'title' == item_type:
            url = hub.get_pdfurl_base_title(item)
            if '' == url:
                return ret
            source_id = self.chat.generate_source_id_baseurl(url)
        if '' == source_id:
            return ret
        result = self.chat.chat_base_prompt(source_id, prompt)
        self.chat.delete_source_id(source_id)
        ret = self.md_table_to_array(result)
        return ret
