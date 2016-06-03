import unittest
import os
import xmlUtil
import xml.etree.ElementTree as ET
import parse_context as pc
import copy

class XMLutilTest(unittest.TestCase):

    def testCompareDifferent(self):
        filePath = 'test/bean-diff.xml'
        tree = ET.parse(filePath)
        bean1 = {}
        bean2 = {}
        #Always different because of the different id attibutes
        for bean in tree.findall("bean[@id='SiteService_security_4.2.f']"):
            bean1 = bean
        for bean in tree.findall("bean[@id='SiteService_security_5.0.d']"):
            bean2 = bean
        cmpResult = xmlUtil.cmp_el(bean1, bean2)
        self.assertEqual(cmpResult,-1)

    def testCompareSame(self):
        filePath = 'test/bean-diff.xml'
        tree = ET.parse(filePath)
        bean1 = {}
        bean2 = {}
        for bean in tree.findall("bean[@id='SiteService_security_5.0.d']"):
            bean1 = bean
        for bean in tree.findall("bean[@id='SiteService_security_5.0.d']"):
            bean2 = bean
        cmpResult = xmlUtil.cmp_el(bean1, bean2)
        self.assertEqual(cmpResult,0)


    def testCollectAndCompareDifferent(self):
        filePath1 = 'test/old/public-services-security-context.xml'
        filePath2 = 'test/new/public-services-security-context.xml'

        beans1 = pc.collectBeansFromFile(filePath1)
        beans2 = pc.collectBeansFromFile(filePath2)
        bean1 = beans1['SiteService_security']
        bean2 = beans2['SiteService_security']
        cmpResult = xmlUtil.cmp_el(bean1['element'], bean2['element'])
        print bean1['path']
        print ET.tostring(bean1['element'])
        print bean2['path']
        print ET.tostring(bean2['element'])
        self.assertEqual(cmpResult,-1)

if __name__ == '__main__':
        unittest.main()
