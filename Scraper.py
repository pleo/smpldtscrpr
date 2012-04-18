#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
A simple data scraper.

Created on Aug 10, 2010

@author: Leon Pajk
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@version: 0.1
"""

import re
import urllib

class Scraper:
    """
    Scraper class.
    """
    filename    = 'untitled.csv'
    max_pagers  = 10
    domain_name = str()
    
    def __init__(self, filename, max_pagers, domain_name):
        """
        Initialize class with a filename and
        maximum number of search results pages.
        """
        self.filename    = filename
        self.max_pagers  = max_pagers
        self.domain_name = domain_name
    
    def getText(self, url):
        """
        Download a content from a specified URL.
        """
        text = str()
        try:
            ufile = urllib.urlopen(url) # get object from url
            text  = ufile.read()        # read all its text
        except IOError as err:
            print 'Problem in reading URL: ', url
            print "I/O error({0}): {1}".format(err.errno, err.strerror)
        return text
    
    def getUrls(self, url):
        """
        Get all URLs for a given URL.
        """
        text = self.getText(url)
        lst = []
        data_begin = text.find('<ul class="searchResults">')
        
        if not data_begin:
            return lst
        
        data_end = text.find('</ul>', data_begin)
        
        if not data_end:
            return lst
        
        tuples = re.findall(r'href="([^"]+)',
                            text[data_begin:data_end],
                            re.M | re.S | re.X)
        for tpl in tuples:
            tpl = str.replace(tpl, '&amp;', '&')
            lst.append(self.domain_name + tpl)
        return lst
    
    def captureDataOnPersonalURI(self, url):
        """
        Return a list of data for one person for a given URL.
        """
        data = self.getText(url) # get HTML text
        lst  = []
        
        name = data.find('<h2 class="sub-heading-main">')
        if name:
            namel = data.find('<h3>', name)
            namer = data.find('</h3>', namel)
            
            # Remove a comma from name/surname and
            # prevent a document corruption.
            name = data[namel + 4:namer].translate(None, ',');
            lst.append('"' + str.replace(name, '&amp;', '&') + '",')
        else:
            lst.append('"",')
        
        address = data.find('Address:')
        
        if not address:
            return lst
        
        address_begin = data.find('<td>',address)
        
        if not address_begin:
            return lst
        
        address_end = data.find('</td>', address_begin + 4)
        
        if not address_end:
            return lst
        
        address = data[address_begin+4:address_end]
              
        # Match all addresses (address can be multiline!)
        tuples = re.findall(r'\s*([\w\s-]+)<br', address, re.M | re.S | re.X)
        
        for t in tuples:
            lst.append('"' + (t if len(t.strip()) > 0 else '') + '",')
        
        # When address is not avaliable insert commas for a proper format
        j = len(tuples)
        if j != 4:
            while j < 4:
                list.append('"",');
                j += 1
        
        email = data.find('Email:')
        
        if not email:
            return lst
        
        # Match an email with regex
        match = re.search(r'>([\w.-]+@[\w.-]+)<', data[email:])
        
        if match:
            email = match.group(1)
            lst.append(email)
        return lst
    
    def parseSearchResults(self, search_page_url):
        """
        Extract data from one search result page.
        """
        # Get all href links on a URL
        urls = self.getUrls(search_page_url)
        
        for url in urls:
            # Retrieve the data from a personal URI
            data = self.captureDataOnPersonalURI(url)
            self.writeDataToCSVFile(data)
    
    def writeDataToCSVFile(self, data):
        """
        Writes the data to the CSV file.
        """
        try:
            file_object = open(self.filename, 'a')
            for el in data:
                file_object.write(el)
            file_object.write('\r\n')
            file_object.close()
        except IOError as err:
            print 'Problem in writing file: ', self.filename
            print "I/O error({0}): {1}".format(err.errno, err.strerror)
    
    def search(self, url):
        """
        Browse all search results.
        """
        i = 1
        while i <= self.max_pagers:
            self.parseSearchResults('%s%d' % (self.domain_name + url, i))
            i += 1

def main():
    """
    Main function.
    """
    searchString = r'test'
    scraper = Scraper('document.csv', 100, r'http://domain-name.tld')
    scraper.writeDataToCSVFile(['"Name","Address",,,,"Email"'])
    scraper.search('/search?q=' + searchString + '&start=')

if __name__ == '__main__':
    """
    Entry point.
    """
    main()

