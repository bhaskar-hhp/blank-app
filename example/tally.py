import requests

xml_request = """
<ENVELOPE>
 <HEADER>
  <TALLYREQUEST>Export Data</TALLYREQUEST>
 </HEADER>
 <BODY>
  <DESC>
   <STATICVARIABLES>
    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
   </STATICVARIABLES>
   <REPORTNAME>List of Ledgers</REPORTNAME>
  </DESC>
 </BODY>
</ENVELOPE>
"""

response = requests.post("http://localhost:9000", data=xml_request)
print(response.text)
