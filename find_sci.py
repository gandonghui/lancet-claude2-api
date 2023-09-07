from scihub_cn.scihub import SciHub
import re

class findSCI:
    def get_item_type(self,item):
        ret = ''
        if re.match(r'^\w:.*\.pdf$', item):  # Local PDF file path (e.g., D:\...\file.pdf)
            ret = 'local_pdf'
        elif re.match(r'^https?://.*\.pdf$', item):  # URL link ending with .pdf
            ret = 'url'
        elif re.match(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', item, re.I):  # DOI number format
            ret = 'doi'
        return ret
        
    def classify_items(self,items_list):
        local_pdf_paths = []
        url_links = []
        doi_numbers = []
        for item in items_list:
            item_type = get_item_type(item)
            if 'local_pdf' == item_type:  # Local PDF file path (e.g., D:\...\file.pdf)
                local_pdf_paths.append(item)
            elif 'url' == item_type:  # URL link ending with .pdf
                url_links.append(item)
            elif 'doi' == item_type:  # DOI number format
                doi_numbers.append(item)
        return local_pdf_paths, url_links, doi_numbers
    
    def get_pdf_url_base_title(self, title):
        ret = ''
        sh = SciHub()
        paperInfo = sh.search_by_google_scholar(title, 10)
        if [] != paperInfo: 
            pattern = r'(\.pdf).*'
            ret = re.sub(pattern, r'\1', paperInfo[0].url)
            if 'http' not in ret:
                ret = 'http://sci-hub.se/' + ret
        return ret

    def get_pdf_url_base_doi(self, doi):
        ret = ''
        sh = SciHub()
        paperInfo = sh._get_paper_info(doi)
        if None != paperInfo:
            pattern = r'(\.pdf).*'
            ret = re.sub(pattern, r'\1', paperInfo.url)
            if 'http' not in ret:
                ret = 'http://sci-hub.se/' + ret
        return ret

