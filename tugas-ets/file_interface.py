import os
import json
import base64
from glob import glob


class FileInterface:
    def __init__(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        files_dir = os.path.join(base_path, 'files')
        os.chdir(files_dir)


    def list(self,params=[]):
        try:
            filelist = glob('*.*')
            return dict(status='OK',data=filelist)
        except Exception as e:
            return dict(status='ERROR',data=str(e))

    def get(self,params=[]):
        try:
            filename = params[0]
            if (filename == ''):
                return None
            fp = open(f"{filename}",'rb')
            isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK',data_namafile=filename,data_file=isifile)
        except Exception as e:
            return dict(status='ERROR',data=str(e))

    def upload(self,params=[]):
        try:
            filename = params[0]
            if(filename == ''):
                return None
            fp = open(f"{filename}", "wb")
            fp.write(base64.b64decode(params[1]))
            return dict(status='OK')
        except Exception as e:
            return dict(status='ERROR',data=str(e))
        
    def delete(self,params=[]):
        try:
            filename=params[0]
            if(filename==''):
                return None
            os.remove(filename)
            return dict(status="OK")
        except Exception as e:
            return dict(status="ERROR",data=str(e))


if __name__=='__main__':
    f = FileInterface()
    print(f.list())
    print(f.get(['pokijan.jpg']))
