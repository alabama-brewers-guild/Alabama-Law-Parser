from html.parser import HTMLParser
from urllib.request import urlopen
from urllib import parse

class AlisonParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.in_section = False
        self.section = ''
        self.in_title = False
        self.title = ''
        self.in_body = False
        self.body = []
        self.in_h5 = False
        self.references = ''

    # This is a function that HTMLParser normally has but we are adding some functionality to it
    def handle_starttag(self, tag, attrs):
        # We are looking for the begining of a link. Links normally look like <a href="www.someurl.com"></a>
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    # We are grabbing the new URL. We are also adding the
                    # base URL to it. For example:
                    # www.netinstructions.com is the base and
                    # somepage.html is the new URL (a relative URL)
                    #
                    # We combine a relative URL with the base URL to create
                    # an absolute URL like:
                    # www.netinstructions.com/somepage.html
                    newUrl = parse.urljoin(self.baseUrl, value)
                    # And add it to our colection of links:
                    self.links = self.links + [newUrl]
        elif tag == 'title':
            self.in_section = True
        elif tag == 'h4':
            self.in_title = True
        elif tag == 'p':
            self.in_body = True
        elif tag == 'h5':
            self.in_h5 = True
        elif tag == '&' and self.in_h5 == true:
            self.body += '$'
        
    def handle_data(self, data):
        if 'Section' in data:
            self.in_h5 = False

        if self.in_section:
            self.section += data.rstrip()
        elif self.in_title:
            self.title += data.rstrip()
        elif self.in_body:
            self.body.append(data.rstrip())
        elif self.in_h5:
            self.references += data.rstrip()

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_section = False
        elif tag == 'h4':
            self.in_title = False
        elif tag == 'p':
            self.in_body = False
        elif tag == 'h5':
            self.in_h5 = False

    def handle_entityref(self, name):
        if name == 'sect' and self.in_h5:
            self.references += "§"

    
    # This is a new function that we are creating to get links
    # that our spider() function will call
    def getLinks(self, url):
        self.links = []
        # Remember the base URL which will be important when creating
        # absolute URLs
        self.baseUrl = url
        # Use the urlopen function from the standard Python 3 library
        response = urlopen(url)
        # Make sure that we are looking at HTML and not other things that
        # are floating around on the internet (such as
        # JavaScript files, CSS, or .PDFs for example)
        if response.getheader('Content-Type')=='text/html':
            htmlBytes = response.read()
            # Note that feed() handles Strings well, but not bytes
            # (A change from Python 2.x to Python 3.x)
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            return htmlString, self.links
        else:
            return "",[]

    