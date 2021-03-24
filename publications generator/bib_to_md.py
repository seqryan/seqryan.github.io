#!/usr/bin/env python
# coding: utf-8

# # Publications markdown generator for academicpages
# 
# Takes a set of bibtex of publications and converts them for use with [academicpages.github.io](academicpages.github.io). This is an interactive Jupyter notebook ([see more info here](http://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/what_is_jupyter.html)). 
# 
# The core python code is also in `pubsFromBibs.py`. 
# Run either from the `markdown_generator` folder after replacing updating the publist dictionary with:
# * bib file names
# * specific venue keys based on your bib file preferences
# * any specific pre-text for specific files
# * Collection Name (future feature)
# 
# TODO: Make this work with other databases of citations, 
# TODO: Merge this with the existing TSV parsing solution


from pybtex.database.input import bibtex
import pybtex.database.input.bibtex 
from time import strptime
import string
import html
import os
import re

#todo: incorporate different collection types rather than a catch all publications, requires other changes to template
# publist = {
#     "proceeding": {
#         "file" : "proceedings.bib",
#         "venuekey": "booktitle",
#         "venue-pretext": "In the proceedings of ",
#         "collection" : {"name":"publications",
#                         "permalink":"/publication/"}
        
#     },
#     "journal":{
#         "file": "proceedings.bib",
#         "venuekey" : "journal",
#         "venue-pretext" : "",
#         "collection" : {"name":"publications",
#                         "permalink":"/publication/"}
#     } 
# }


publist = {
    "journal":{
        "file": "journal_proceedings.bib",
        "venuekey" : "journal",
        "venue-pretext" : "",
        "collection" : {"name":"publications",
                        "permalink":"/publication/"}
    },
    "proceeding": {
        "file" : "conference_proceedings.bib",
        "venuekey": "booktitle",
        "venue-pretext": "In the proceedings of ",
        "collection" : {"name":"publications",
                        "permalink":"/publication/"}
        
    } 
}


html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;"
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)


for pubsource in publist:
    print(pubsource)
    parser = bibtex.Parser()
    bibdata = parser.parse_file(publist[pubsource]["file"])

    #loop through the individual references in a given bibtex file
    for bib_id in bibdata.entries:
        #reset default date
        pub_year = "1900"
        pub_month = "01"
        pub_day = "01"

        pub_volume = "01"
        pub_issue = "01"
        
        b = bibdata.entries[bib_id].fields
        
        try:
            pub_year = f'{b["year"]}'

            #todo: this hack for month and day needs some cleanup
            if "month" in b.keys(): 
                if(len(b["month"])<3):
                    pub_month = "0"+b["month"]
                    pub_month = pub_month[-2:]
                elif(b["month"] not in range(12)):
                    tmnth = strptime(b["month"][:3],'%b').tm_mon   
                    pub_month = "{:02d}".format(tmnth) 
                else:
                    pub_month = str(b["month"])
            if "day" in b.keys(): 
                pub_day = str(b["day"])

            if "volume" in b.keys():
                pub_volume = str(b["volume"]) 
            pub_doi = str(b["doi"])     

                
            pub_date = pub_year+"-"+pub_month+"-"+pub_day
            

            #strip out {} as needed (some bibtex entries that maintain formatting)
            clean_title = b["title"].replace("{", "").replace("}","").replace("\\","").replace(" ","-") 

            url_slug = re.sub("\\[.*\\]|[^a-zA-Z0-9_-]", "", clean_title)
            url_slug = url_slug.replace("--","-")

            md_filename = (str(pub_date) + "-" + url_slug + ".md").replace("--","-")
            html_filename = (str(pub_date) + "-" + url_slug).replace("--","-")

            #Build Citation from text
            authors = "" 

            #citation authors - todo - add highlighting for primary author?
            for author in bibdata.entries[bib_id].persons["author"]:
                authors = authors+" "+author.first_names[0]+" "+author.last_names[0]+", "

            #add venue logic depending on citation type
            venue = publist[pubsource]["venue-pretext"]+b[publist[pubsource]["venuekey"]].replace("{", "").replace("}","").replace("\\","")
            
            ## YAML variables
            md = "---\ntitle: \""   + html_escape(b["title"].replace("{", "").replace("}","").replace("\\","")) + "\""
            md += "\nlayout: post"
            md += """\ncategory: """ +  publist[pubsource]["collection"]["name"]
            md += "\ndate: " + str(pub_date) 
            md += """\ncollection: """ +  publist[pubsource]["collection"]["name"]
            md += """\npermalink: """ + publist[pubsource]["collection"]["permalink"]  + html_filename 
            
            md += "\n\nwork-type: Paper"
            md += "\nref-authors: " + authors
            md += "\nref-year: " + pub_year
            md += "\nref-title: \"" + html_escape(b["title"].replace("{", "").replace("}","").replace("\\","")) + "\""
            md += "\nref-journal: '" + html_escape(venue) + "'"
            md += "\nref-vol: " + pub_volume
            md += "\nref-doi: " + pub_doi
            md += "\n---"

            
            ## Markdown description for individual page
            md_filename = os.path.basename(md_filename)

            with open("../_publications/" + md_filename, 'w') as f:
                f.write(md)
            print(f'SUCESSFULLY PARSED {bib_id}: \"', b["title"][:60],"..."*(len(b['title'])>60),"\"")
        # field may not exist for a reference
        except KeyError as e:
            print(f'WARNING Missing Expected Field {e} from entry {bib_id}: \"', b["title"][:30],"..."*(len(b['title'])>30),"\"")
            continue