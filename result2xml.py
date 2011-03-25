import traceback
from xml.dom import minidom
#xml_doc = minidom.Document()
def create_xml_doc():
    return  minidom.Document()

def xml_head(result,xml_doc):
    testResult = xml_doc.createElement("testResult")
    testResult.setAttribute("name",result.nodename)
    testResult.setAttribute("status",result.status)
    testResult.setAttribute("start_time",str(result.start_time))
    testResult.setAttribute("end_time",str(result.end_time))
    testResult.setAttribute("time_use",str(result.end_time-result.start_time))
    xml_doc.appendChild(testResult)
    return testResult

def xml_body(result,headnode):pass

def xml_sample(result,headnode,xml_doc):
    child = xml_doc.createElement(result.nodetype)
    child.setAttribute('id',result._sample.id)
    if getattr(result._sample,'url',None):
        child.setAttribute('url',result._sample.url)
    if getattr(result._sample,'wsdl',None):
        child.setAttribute('wsdl',result._sample.wsdl)
    child.setAttribute('method',result._sample.method)
    if getattr(result,'code',None):
        child.setAttribute('code',str(result.code))
    child.setAttribute('status',result.status)
    headnode.appendChild(child)
    return child
   
def xml_assert(result,headnode,xml_doc):
    child = xml_doc.createElement(result.nodetype)
    child.setAttribute('status',result.status)
    if result._assert.__dict__.has_key('type'):
        child.setAttribute('type',result._assert.type)
	if result._assert.__dict__.has_key('item'):
	    args = [item._text for item in result._assert.item]
	    exp = result._assert.type+'['
	    for i in args:
		exp += i+','
	    exp = exp[:-1]+']'
            child.setAttribute('expression',exp)
    headnode.appendChild(child)
    return child

def xml_soapsample_detail(rs,headnode,xml_doc):
    if getattr(rs,'soapRespone',None):
        from SOAPpy import Types
	child_rs_soap = xml_doc.createElement('soap_Result')
	if type(rs.soapRespone) in [tuple,list]:
	    child_rs_soap_attr = xml_doc.createElement("list")
	    for item in rs.soapRespone:
		if item.__class__ is Types.structType:
	            child_rs_soap_attr.setAttribute('name',item._name)
		    child_rs_soap_attr_list = xml_doc.createElement("attribute")
		    for i in item.__dict__.items():
			if '_' not in i[0]:
			    child_rs_soap_attr_list.setAttribute(i[0],i[1])
		    child_rs_soap_attr.appendChild(child_rs_soap_attr_list)
		else:
                    child_rs_soap_text = xml_doc.createTextNode(item)
                    child_rs_soap.appendChild(child_rs_soap_text)
	    child_rs_soap.appendChild(child_rs_soap_attr)

	elif rs.soapRespone.__class__ is Types.structType:
	    child_rs_soap_attr = xml_doc.createElement("attribute")
	    child_rs_soap_attr.setAttribute('name',rs.soapRespone._name)
	    child_rs_soap_attr.setAttribute('type',str(rs.soapRespone.__class__))
	    print rs.soapRespone.__dict__.items()
	    for item in rs.soapRespone.__dict__.items():
	        if '_' not in item[0]:
		    print item[0].ljust(20),str(item[1])
                    child_rs_soap_attr.setAttribute(item[0],str(item[1]))
	    child_rs_soap.appendChild(child_rs_soap_attr)
	else:
	    child_rs_soap_text = xml_doc.createTextNode(str(rs.soapRespone))
            child_rs_soap.appendChild(child_rs_soap_text)
	headnode.appendChild(child_rs_soap)

def xml_httpsample_detail(rs,headnode,xml_doc):
    if rs.__dict__.has_key('httpHeader'):
        child_rs_httpheader = xml_doc.createElement('httpHeader')
        for item in rs.httpHeader:
	    child_rs_httpheader_attr =  xml_doc.createElement("attribute")
	    child_rs_httpheader_attr.setAttribute('name',item[0])
            child_rs_httpheader_attr.setAttribute('value',item[1])
            child_rs_httpheader.appendChild(child_rs_httpheader_attr)
        headnode.appendChild(child_rs_httpheader)
    if rs.__dict__.has_key('responseHeaders'):
        child_rs_resheader = xml_doc.createElement('responseHeader')
        for rsitem in rs.responseHeaders.__dict__.items():
	    child_rs_resheader_attr =  xml_doc.createElement("attribute")
            child_rs_resheader_attr.setAttribute('name',str(rsitem[0]))
	    if type(rsitem[1]) is list:
		for i in rsitem[1]:
	            if ':' in i:
		        child_rs_resheader_attr_list =  xml_doc.createElement("key")
                        key = i[:i.index(':')]
		        value = i[i.index(':')+1:]
			child_rs_resheader_attr_list.setAttribute(key,value)
                        child_rs_resheader_attr.appendChild(child_rs_resheader_attr_list)
	    elif type(rsitem[1]) is dict:
		for i in rsitem[1].items():
		    child_rs_resheader_attr_list =  xml_doc.createElement("key")				
		    child_rs_resheader_attr_list.setAttribute(i[0],i[1])
                    child_rs_resheader_attr.appendChild(child_rs_resheader_attr_list)
            else:
		child_rs_resheader_attr.setAttribute('value',str(rsitem[1]))
            child_rs_resheader.appendChild(child_rs_resheader_attr)
        headnode.appendChild(child_rs_resheader)
    if rs.__dict__.has_key('responseText'):
	def getCharset():
	    content_type = rs.responseHeaders.dict['content-type']
	    charsets = content_type.split(';')
	    for item in charsets:
		if 'charset=' in item:
	            if 'gb' in item.lower():
			return 'gbk'
		    else:
			return item[item.index('=')+1:]
	charset = getCharset()
        child_rs_resText = xml_doc.createElement('responseText')
        data = rs.responseText.decode(charset)
	if ']]>' in data:
	    data = data.replace(']]>',']] >')
        child_rs_resText_text = xml_doc.createCDATASection(data)
        child_rs_resText.appendChild(child_rs_resText_text)
        headnode.appendChild(child_rs_resText) 

def xml_except(result,headnode,xml_doc):
    rs_except = xml_doc.createElement('exception')
    rs_except_text1 = xml_doc.createTextNode('ERROR: %s'%str(result.exc_info[0]).replace('<','').replace('>',''))
    rs_except.appendChild(rs_except_text1)
    rs_except_text2 = xml_doc.createTextNode('ERROR: %s'%result.exc_info[1].message)
    rs_except.appendChild(rs_except_text2)
    rs_except_textmsg = xml_doc.createTextNode('More Information:')
    rs_except.appendChild(rs_except_textmsg)
    for filename, lineno, function, msg in traceback.extract_tb(result.exc_info[2]):
	rs_except_text3 = xml_doc.createTextNode('%s line %s in %s function [%s]'%(filename,lineno,function,msg))
	rs_except.appendChild(rs_except_text3)
    headnode.appendChild(rs_except)

class build:
    def __init__(self,result): 
        try:
           self.weave(result)
	except:
	   print 'error!!!!!!!!!!!'
	
    def weave(self,result):
        xml_doc = create_xml_doc()
        headnode = xml_head(result,xml_doc)
	for rs in result.sections:
	    if rs.nodetype in [u'sample','sample']:
	         child = xml_sample(rs,headnode,xml_doc)
		 if getattr(rs,'log',None):
		     print '-------result----------'
		     print rs.log
                     if getattr(rs,'_sample',None) and rs._sample.type.lower() == 'soap':
		         xml_soapsample_detail(rs,child,xml_doc)
		     elif getattr(rs,'_sample',None) and rs._sample.type.lower() == 'http':
		         xml_httpsample_detail(rs,child,xml_doc)
	         if rs.status in ['ERROR','FAIL']:
		         xml_except(rs,child,xml_doc)
            else:
	         xml_assert(rs,headnode,xml_doc)
	if result.__dict__.has_key('exc_info'):
	    xml_except(result,headnode,xml_doc)
	setattr(self,'xml_doc',xml_doc)
    
    def get_xml_doc(self):
        return self.xml_doc
