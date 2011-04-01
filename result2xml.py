import traceback
import sys
from xml.dom import minidom
from logger import log,log_exce

def create_xml_doc():
    return  minidom.Document()

def xml_head(result,xml_doc):
    testResult = xml_doc.createElement("testResult")
    testResult.setAttribute("name",result.nodename)
    testResult.setAttribute("status",result.status)
    testResult.setAttribute("start_time",str(result.start_time))
    testResult.setAttribute("end_time",str(result.end_time))
    testResult.setAttribute("time_used",str(result.end_time-result.start_time))
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
    child.setAttribute('start_time',str(result.start_time))
    child.setAttribute('end_time',str(result.end_time))
    child.setAttribute('time_used',str(result.end_time-result.start_time))
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
        self.weave(result)
	

    def getdumper(self,name):
        from dumper import get_dumper,getRegdumpers
        dumpers = getRegdumpers()
        if dumpers.has_key(name):
            dum = get_dumper(name)
	else:
	    dum = get_dumper('DEFAULT')
	return dum()

    def weave(self,result):
        xml_doc = create_xml_doc()
        headnode = xml_head(result,xml_doc)
	for rs in result.sections:
	    if rs.nodetype in [u'sample','sample']:
	         child = xml_sample(rs,headnode,xml_doc)
		 if getattr(rs,'log',None):
		     #self.getdumpler(rs)
		     try:
                         demper = self.getdumper(rs._sample.type.upper())
                         demper.dump(rs,headnode,xml_doc) 
		     except:
		         log.debug('have no dumper about  %s sampler'%rs._sample.type)
                         print sys.exc_info()[0]
                         print sys.exc_info()[1]
                         for filename, lineno, function, msg in traceback.extract_tb(sys.exc_info()[2]):
			     print '%s line %s in %s function [%s]'%(filename,lineno,function,msg)
	         if rs.status in ['ERROR','FAIL']:
		         xml_except(rs,child,xml_doc)
            else:
	         xml_assert(rs,headnode,xml_doc)
	if result.__dict__.has_key('exc_info'):
	    xml_except(result,headnode,xml_doc)
	setattr(self,'xml_doc',xml_doc)
    
    def get_xml_doc(self):
        return self.xml_doc
