"""
自定义返回数据格式
"""

def JsonResponse(data:str=None,msg:str=None,success:bool=None,code:int=200):
    """
      An HttpResponse that allows its data to be rendered into
      arbitrary media types.
    """
    data = {"data": data, "msg": msg, "success": success, "code": code}
    return data
