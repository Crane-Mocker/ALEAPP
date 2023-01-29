import datetime
import email
import os
import struct
import magic
import gzip
import shutil
from io import BytesIO

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, media_to_html

def get_browserCachechrome(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('_0'):
        
            filename = os.path.basename(file_found)
            
            modified_time = os.path.getmtime(file_found)
            utc_modified_date = datetime.datetime.utcfromtimestamp(modified_time)
            
            with open(file_found, 'rb') as file:
                data = file.read()
                ab = BytesIO(data)
                
                eofloc = data.index(b'\xD8\x41\x0D\x97\x45\x6F\xFA\xF4')
                
                header = ab.read(8)
                version = ab.read(4)
                lenghturl = ab.read(4)
                lenghturl = (struct.unpack_from("<i",lenghturl)[0])
                dismiss = ab.read(8)
                
                headerlenght = lenghturl + 8 + 4 + 4 + 8
                
                url = ab.read(lenghturl)
                url = (url.decode())
                filedata = ab.read(eofloc - headerlenght)
                
                mime = magic.from_buffer(filedata, mime=True)
                ext = (mime.split('/')[1])
                
                sfilename = filename + '.' + ext
                spath = os.path.join(report_folder,sfilename)
                
                with open(f'{spath}', 'wb') as d:
                    d.write(filedata)
                
                if ext == 'x-gzip':
                    try:
                        with gzip.open(f'{spath}', 'rb') as f_in:
                            file_content = f_in.read()
                                
                            mime = magic.from_buffer(file_content, mime=True)
                            extin = (mime.split('/')[1])
                            #logfunc(f'Gzip mime: {mime} for {spath}')    
                            sfilenamein = filename + '.' + extin
                            spath = os.path.join(report_folder,sfilenamein)
                            
                        with open(f'{spath}', 'wb') as f_out:
                            f_out.write(file_content)

                    except Exception as e: logfunc(str(e))
                
                if 'video' in mime:
                    spath = f'<video width="320" height="240" controls="controls"><source src="{spath}" type="video/mp4">Your browser does not support the video tag.</video>'
                elif 'image' in mime:
                    spath = f'<img src="{spath}"width="300"></img>'
                elif 'audio' in mime:
                    spath = f'<audio controls><source src="{spath}" type="audio/ogg"><source src="{spath}" type="audio/mpeg">Your browser does not support the audio element.</audio>'
                else:
                    spath = f'<a href="{spath}"> Link to {mime} </>'
        
                data_list.append((utc_modified_date, filename, mime, spath, url, file_found))
        
    if len(data_list) > 0:
        note = 'Source location in extraction found in the report for each item.'
        report = ArtifactHtmlReport('Chrome Browser Cache')
        report.start_artifact_report(report_folder, f'Chrome Browser Cache')
        report.add_script()
        data_headers = ('Timestamp Modified', 'Filename', 'Mime Type', 'Cached File', 'Source URL', 'Source')
        report.write_artifact_data_table(data_headers, data_list, note, html_no_escape=['Cached File'])
        report.end_artifact_report()
        
        tsvname = f'Chrome Browser Cache'
        tsv(report_folder, data_headers, data_list, tsvname)
    
__artifacts__ = {
        "browserCachechrome": (
                "Browser Cache",
                ( '*/data/com.android.chrome/cache/Cache/*_0'),
                get_browserCachechrome)
}
            