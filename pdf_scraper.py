"""
Simple scraper

WORK IN PROGRESS

"""

import re

class XMPObject:
    def __init__(self, obj):
        self.obj = self.load_object(obj)
        self.fields = ['xmpMM:InstanceID', 'xmpMM:OriginalDocumentID', 'xmpMM:DocumentID', 'xmpMM:RenditionClass', 'xmpMM:VersionID', 'stRef:instanceID', 'stRef:documentID', 'stRef:renditionClass', 'xmpMM:History', 'stEvt:action', 'stEvt:parameters', 'stEvt:softwareAgent', 'stEvt:when', 'stEvt:action', 'stEvt:instanceID', 'stEvt:parameters', 'stEvt:softwareAgent', 'stEvt:when', 'xmpMM:History', 'xmp:CreateDate', 'xmp:CreatorTool', 'xmp:ModifyDate', 'xmp:MetadataDate', 'dc:format', 'dc:title', 'dc:title', 'dc:creator', 'dc:creator', 'dc:rights', 'dc:rights', 'photoshop:AuthorsPosition', 'pdf:Producer', 'pdf:Trapped', 'pdfaid:part', 'pdfaid:conformance', 'pdfaExtension:schemas', 'pdfaSchema:namespaceURI', 'pdfaSchema:prefix', 'pdfaSchema:schema', 'pdfaSchema:property', 'pdfaProperty:category', 'pdfaProperty:description', 'pdfaProperty:name', 'pdfaProperty:valueType', 'pdfaProperty:category', 'pdfaProperty:description', 'pdfaProperty:name', 'pdfaProperty:valueType', 'pdfaSchema:property', 'pdfaSchema:namespaceURI', 'pdfaSchema:prefix', 'pdfaSchema:schema', 'pdfaSchema:property', 'pdfaProperty:category', 'pdfaProperty:description', 'rapping information<pdfaProperty:description', 'pdfaProperty:name', 'pdfaProperty:valueType', 'pdfaSchema:property', 'pdfaSchema:namespaceURI', 'pdfaSchema:prefix', 'pdfaSchema:schema', 'pdfaSchema:property', 'pdfaProperty:category', 'pdfaProperty:description', 'pdfaProperty:name', 'pdfaProperty:valueType', 'pdfaProperty:category', 'pdfaProperty:description', 'pdfaProperty:name', 'pdfaProperty:valueType', 'pdfaProperty:category', 'pdfaProperty:description', 'pdfaProperty:name']
        
        self.obj_data = {field:self.extract_field(self.obj, field) for field in self.fields}

    def extract_field(self, obj, field):
        for attr in obj:
            if field in attr:
                return attr.replace('<{}>'.format(field), '').replace('</{}>'.format(field),'')
            
    def load_object(self, obj):
        return list(filter(None, [i.strip() for i in obj.decode().split('\n')]))
    
    def __str__(self):
        return ''.join([str(i) + " = " + str(self.obj_data[i]) + "\n" for i in self.obj_data.keys()])

def de_dupe_list(list_var):
    """Removes duplicate elements from list

    This function reads the input list, and creates a new
    blank list. It iterates over each element of the input
    list and adds each unique elelemnt to the new list, with
    any duplicated elements being ignored.

    Args:
        list_var: Any list object.

    Returns:
        This function returns a list of unique elements from
        the input arg.
    """
    new_list = []
    for element in list_var:
        if element not in new_list:
            new_list.append(element)
    return new_list


class BinaryPdfForensics:
    def __init__(self, 
                 file_path, 
                 password=None):
        """Inits class object with attributes"""
        self.file_path = file_path
        self.temp_path = self.file_path
        self.output_path = self.file_path
        self.password = password

    def get_info_ref(self):
        """Tests if a PDF file contains an /Info reference

        This method reads the input file as a binary stream,
        and then performs a regex search, to determine if it 
        contains a document information dictionary reference. 
        This method only works with valid PDF files, and will 
        produce unexpected errors if used on other file types. 
        PDF file type should be verified first with the 
        pdf_magic() method.

        Args:
            temp_path: The path (can be full or abbreviated) of
            the file to be tested.

        Returns:
            This method returns a tuple containing two values:
            (1) a Boolean value identifying whether or not the PDF
            contains the /Info reference, and (2) a list of any
            located binary document information dictionary string
            references. Example of the info value:

                /Info 2 0 R
        """
        with open(self.temp_path, 'rb') as raw_file:
            read_file = raw_file.read()
            regex = b'[/]Info[\s0-9]*?R'
            pattern = re.compile(regex, re.DOTALL)
            info_ref = re.findall(pattern, read_file)
            info_ref = de_dupe_list(info_ref)
            if len(info_ref) == 0:
                info_ref_exists = False
            else:
                info_ref_exists = True
            return (info_ref_exists, info_ref)
        
    def get_xmp_ref(self):
        """Tests if a PDF file contains a /Metadata reference

        This method reads the input file as a binary stream,
        and then performs a regex search, to determine if it
        contains an XMP metadata reference. This method only
        works with valid PDF files, and will produce unexpected
        errors if used on other file types. PDF file type should
        be verified first with the pdf_magic() method.

        Args:
            temp_path: The path (can be full or abbreviated) of
            the file to be tested.

        Returns:
            This method returns a tuple containing two values:
            (1) a Boolean value identifying whether or not the PDF
            contains the /Metadata reference, and (2) a list of
            any located binary XMP metadata string references.
            Example of the XMP metadata reference:

                /Metadata 3 0 R
        """
        with open(self.temp_path, 'rb') as raw_file:
            read_file = raw_file.read()
            regex = b'[/]Metadata[\s0-9]*?R'
            pattern = re.compile(regex, re.DOTALL)
            xmp_ref = re.findall(pattern, read_file)
            xmp_ref = de_dupe_list(xmp_ref)
            if len(xmp_ref) == 0:
                xmp_ref_exists = False
            else:
                xmp_ref_exists = True
            return (xmp_ref_exists, xmp_ref)

    def get_info_obj(self):
        """Extracts /Info objects from PDF file
        
        This method reads the input file as a binary stream,
        and then calls the get_info_ref() function to get any
        /Info references in the file. Any located /Info refs
        are then used to locate any matching /Info objects
        in the file. Example of the /Info object:

            2 0 obj
            << ... >>
            endobj

        Args:
            temp_path: The path (can be full or abbreviated) of
            the file to be tested.

        Returns:
            This method returns a tuple containing the following
            elements: (1) a boolean value of whether or not an
            /Info object exists, and (2) a dictionary which maps
            the /Info references with their objects.
        """
        with open(self.temp_path, 'rb') as raw_file:
            read_file = raw_file.read()
            info_ref_tuple = BinaryPdfForensics.get_info_ref(self)
            info_obj_dict = {}
            for ref in info_ref_tuple[1]:
                info_ref = ref.decode()
                info_ref = info_ref.replace('/Info ', '') \
                                   .replace(' R', '')
                info_ref = str.encode(info_ref)
                regex = b'[^0-9]' + info_ref + b'[ ]obj.*?endobj'
                pattern = re.compile(regex, re.DOTALL)
                info_obj = re.findall(pattern, read_file)
                info_obj = de_dupe_list(info_obj)
                if len(info_obj) > 0:
                    for obj in info_obj:
                        info_obj_dict[ref] = obj
            if len(info_obj_dict) == 0:
                info_obj_exists = False
            else:
                info_obj_exists = True
            return (info_obj_exists, info_obj_dict)
        
    def get_xmp_obj(self):
        """Extracts /Metadata objects from PDF file
        
        This method reads the input file as a binary stream,
        and then calls the get_xmp_ref() function to get any
        /Info references in the file. Any located /Metadata refs
        are then used to locate any matching /Metadata objects
        in the file. Example of /Metadata object:

            3 0 obj
            <</Length 4718/Subtype/XML/Type/Metadata>>stream
            <?xpacket begin="ï»¿" id="W5M0MpCehiHzreSzNTczkc9d"?>
            <x:xmpmeta ...
            </x:xmpmeta>
            <?xpacket end="w"?>
            endstream
            endobj

        Args:
            temp_path: The path (can be full or abbreviated) of
            the file to be tested.

        Returns:
            This method returns a tuple containing the following
            elements: (1) a boolean value of whether or not an
            /Metadata object exists, and (2) a dictionary which 
            maps the /Metadata references with their objects.
        """
        with open(self.temp_path, 'rb') as raw_file:
            read_file = raw_file.read()
            xmp_ref_tuple = BinaryPdfForensics.get_xmp_ref(self)
            xmp_obj_dict = {}
            for ref in xmp_ref_tuple[1]:
                xmp_ref = ref.decode()
                xmp_ref = xmp_ref.replace('/Metadata ', '') \
                                 .replace(' R', '')
                xmp_ref = str.encode(xmp_ref)
                regex = b'[^0-9]' + xmp_ref + b'[ ]obj.*?endobj'
                pattern = re.compile(regex, re.DOTALL)
                xmp_obj = re.findall(pattern, read_file)
                xmp_obj = de_dupe_list(xmp_obj)
                if len(xmp_obj) > 0:
                    for obj in xmp_obj:
                        xmp_obj_dict[ref] = obj
            if len(xmp_obj_dict) == 0:
                xmp_obj_exists = False
            else:
                xmp_obj_exists = True
            return (xmp_obj_exists, xmp_obj_dict)



def main():
    results = BinaryPdfForensics(file_path='data/pdf5.pdf').get_xmp_obj()
    for xmp_key in results[1]:
        print("Results for XMP {}".format(xmp_key.decode()))
        print(XMPObject(results[1][xmp_key]))


if __name__ == '__main__':
    main()
