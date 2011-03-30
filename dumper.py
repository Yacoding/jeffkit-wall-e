#encoding=utf-8
#from xml.dom import minidom
import sys
from SOAPpy import Types

sample_dumper = {}

#ע����ص�dumper
def register(name,dumper):
    sample_dumper[name] = dumper

#ע��dumper
def unregister(name):
    del sample_dumper[name]

#
def get_dumper(name):
    return sample_dumper[name]

def getRegdumpers():
    return sample_dumper



#����sampleDumper,����dumper��Ӧ�ü̳�sampleDumpe����дdump������Ĭ������£�������Ƿȱ�������
#����SampleDumper��dump������û�о���ʵ�֣���
class SampleDumper:
    def dump(self,rs,headnode,xml_doc):pass




#��Ӧhttp����sample��dumper
class HTTPDumper(SampleDumper):

     def dump(self,rs,headnode,xml_doc):

         self.dump_httpHeader(rs,headnode,xml_doc)
	 self.dump_responseHeaders(rs,headnode,xml_doc)
         self.dump_responseText(rs,headnode,xml_doc)

     #����httpͷ
     def dump_httpHeader(self,rs,headnode,xml_doc):
         if rs.__dict__.has_key('httpHeader'):

             child_rs_httpheader = xml_doc.createElement('httpHeader')
             for item in rs.httpHeader:
	         child_rs_httpheader_attr =  xml_doc.createElement("attribute")
	         child_rs_httpheader_attr.setAttribute('name',item[0])
                 child_rs_httpheader_attr.setAttribute('value',item[1])
                 child_rs_httpheader.appendChild(child_rs_httpheader_attr)

             headnode.appendChild(child_rs_httpheader)

     #������Ӧͷ
     def dump_responseHeaders(self,rs,headnode,xml_doc):
         if rs.__dict__.has_key('responseHeaders'):

             child_rs_resheader = xml_doc.createElement('responseHeader')
             for rsitem in rs.responseHeaders.__dict__.items():
	         child_rs_resheader_attr =  xml_doc.createElement("attribute")
                 child_rs_resheader_attr.setAttribute('name',str(rsitem[0]))
	         if type(rsitem[1]) is list:
		     for i in rsitem[1]:
	                 if ':' in i:
		             child_rs_resheader_attr_list = xml_doc.createElement("key")
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

     #������Ӧ����
     def dump_responseText(self,rs,headnode,xml_doc):
         #��ȡ�ַ�����
         def getCharset():
	     content_type = rs.responseHeaders.dict['content-type']
	     charsets = content_type.split(';')
	     for item in charsets:
		 if 'charset=' in item:
	             if 'gb' in item.lower():
			 return 'gbk'
		     else:
			 return item[item.index('=')+1:]

	 if rs.__dict__.has_key('responseText'):
	     charset = getCharset()
             child_rs_resText = xml_doc.createElement('responseText')
             data = rs.responseText.decode(charset)
	     
	     if ']]>' in data:
	         data = data.replace(']]>',']] >')
             child_rs_resText_text = xml_doc.createCDATASection(data)
             child_rs_resText.appendChild(child_rs_resText_text)

             headnode.appendChild(child_rs_resText) 

#��Ӧsoap����sample��dumper
class SOAPDumper(SampleDumper):
    
     def dump(self,rs,headnode,xml_doc):
         try:
	     #print getattr(rs,'outcoming',None)
	     #print getattr(rs,'incoming',None)
	     if getattr(rs,'outcoming',None) and getattr(rs,'incoming',None):
                 self.dump_soap(rs,headnode,xml_doc,'outcoming','outcoming')
	         self.dump_soap(rs,headnode,xml_doc,'incoming','incoming')
             self.dump_soapsample_detail(rs,headnode,xml_doc)
	 except:
	     print 'this is the cause'
	     print sys.exc_info()[0],'  ',sys.exc_info()[1]
	     import traceback
	     for filename, lineno, function, msg in traceback.extract_tb(sys.exc_info()[2]):
	         print '%s line %s in %s function [%s]'%(filename,lineno,function,msg)
	

     #����soap incoming,outcoming
     def dump_soap(self,rs,headnode,xml_doc,nodename,attr):

         child_rs_soap = xml_doc.createElement(nodename)
	 data = getattr(rs,attr).decode('utf-8')

	 if ']]' in data:
	     data = data.replace(']]>',']] >')

	 child_rs_soaptext = xml_doc.createCDATASection(data)
	 child_rs_soap.appendChild(child_rs_soaptext)

	 headnode.appendChild(child_rs_soap) 

     # ������result��Ҫ�߼�  
     def dump_soapsample(self,rs,headnode,xml_doc):
      
         if rs.__class__ in [tuple,list]:
	     child_rs_soap_attr = xml_doc.createElement("list")
	     for item in rs:
	         self.dump_soapsample(item,child_rs_soap_attr,xml_doc)
	     headnode.appendChild(child_rs_soap_attr)
	 elif rs.__class__ is Types.structType:
	     child_rs_soap_attr1 = xml_doc.createElement("attribute")
	     child_rs_soap_attr1.setAttribute('name',rs._name)
	     child_rs_soap_attr1.setAttribute('type',str(rs.__class__))
	     for item in rs.__dict__.items():
	         if '_' not in item[0]:
                     child_rs_soap_attr1.setAttribute(item[0],item[1])
	     headnode.appendChild(child_rs_soap_attr1)
	 else:
	     child_rs_soap_text = xml_doc.createTextNode(str(rs))
             headnode.appendChild(child_rs_soap_text)

     #����soap���result
     def dump_soapsample_detail(self,rs,headnode,xml_doc):
         if getattr(rs,'soapRespone',None):
	     child_rs_soap = xml_doc.createElement('soap_Result')
	     
	     rs_soap = rs.soapRespone
	     self.dump_soapsample(rs_soap,child_rs_soap,xml_doc)
	     #���������Ϊdump_soapsample����
	     '''
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
                         child_rs_soap_attr.setAttribute(item[0],str(item[1]))
	         child_rs_soap.appendChild(child_rs_soap_attr)
	     else:
	         child_rs_soap_text = xml_doc.createTextNode(str(rs.soapRespone))
                 child_rs_soap.appendChild(child_rs_soap_text)
	     '''
	     headnode.appendChild(child_rs_soap)

#��Ӧftp����sample��dumper
class FTPDumper(SampleDumper):pass

register("HTTP",HTTPDumper)
register("SOAP",SOAPDumper)
register("FTP",FTPDumper)
register('DEFAULT',SampleDumper)

if __name__ == '__main__':
    print sample_dumper
    print get_dumper('SOAP')
