<a name="powerbiclient"></a>
# powerbiclient

## Table of content

* [**PowerBI report embedding widget**](#powerbiclient.report)                       
  * [Create an instance of a report](#\_\_init\_\_-report)                               
  * [Set a new access token for report](#set\_access\_token)                           
  * [Set width and height of a report in px](#set\_dimensions)                           
  * [Export the data of a given visual of the report](#export\_visual\_data)             
  * [Register a callback to a report event](#on)                                       
  * [Set report level filters in the report](#update\_filters)                         
  * [Remove all report level filters](#remove\_filters)                
  * [Get the list of the report's pages](#get\_pages)                                     
  * [Get the list of visuals of the given page of the report](#visuals\_on\_page)          
  * [Apply a bookmark by name on the report](#set\_bookmark)                           
  * [Get the list of the report's bookmarks](#get\_bookmarks)                             
* [**Authenticate to Power BI and acquire access token**](#powerbiclient.authentication)
  * [Authentication result](#authenticationResult-class)                               
    * [Create instance of Authentication](#\_\_init\_\_-authenticationresult)            
    * [Get access token](#get\_access\_token)                                            
    * [Get authentication result](#get\_access\_token\_details)                          
    * [Acquire token based on a refresh token obtained from authentication result](#refresh\_token)
  * [Device Flow Authentication](#devicecodeloginauthentication-class)                 
    * [Initiate a Device Flow Auth instance](#\_\_init\_\_-deviceCodeloginauthentication)
  * [Interactive Flow Authentication](#interactiveloginauthentication-class)           
    * [Acquire token interactively](#\_\_init\_\_-interactiveloginauthentication)        

<a name="powerbiclient.report"></a>
# powerbiclient.report

Embeds Power BI Report

<a name="powerbiclient.report.Report"></a>
## Report class

```python
class Report(DOMWidget)
```

PowerBI report embedding widget

**Code snippet**:
```python
# Import Report class
from powerbiclient import Report
```

<br>

<a name="powerbiclient.report.Report.__init__"></a>
## \_\_init\_\_ Report

```python
__init__(access_token=None, embed_url=None, token_type=TokenType.AAD.value, group_id=None, report_id=None, auth=None, view_mode=EmbedMode.VIEW.value, permissions=Permissions.READ.value, client_id=None, dataset_id=None, **kwargs)
```

Create an instance of Power BI report

**Arguments**:

- `access_token` _string_ - Optional.
  access token, which will be used to embed a Power BI report.
  If not provided, authentication object will be used (to be provided using `auth` parameter)
  
- `embed_url` _string_ - Optional.
  embed URL of Power BI report.
  If not provided, `group_id` and `report_id` parameters will be used to generate embed URL
  
- `token_type` _number_ - Optional.
  type of access token (0: AAD, 1: EMBED).
  (Default = AAD)
  
- `group_id` _string_ - Optional.
  Id of Power BI Group or Workspace where your report resides.
  It will be used if `embed_url` is not provided
  
- `report_id` _string_ - Optional.
  Id of Power BI report.
  It will be used if `embed_url` is not provided
  
- `auth` _object_ - Optional.
  Authentication object.
  It will be used if `access_token` is not provided.
  If not provided, Power BI User will be authenticated automatically using Device Flow authentication
  
- `view_mode` _number_ - Optional.
  Mode for embedding Power BI report (VIEW: 0, EDIT: 1, CREATE: 2).
  To be provided if you want to edit or create a report.
  (Default = VIEW)
  
- `permissions` _number_ - Optional.
  Permissions required while embedding report in EDIT mode.
  Values for permissions:
  \n `READ` - Users can view the report.
  \n `READWRITE` - Users can view, edit, and save the report.
  \n `COPY` - Users can save a copy of the report by using Save As.
  \n `CREATE` - Users can create a new report.
  \n `ALL` - Users can create, view, edit, save, and save a copy of the report.
  \n To be provided if the report is embedded in EDIT mode by passing `1` in `view_mode` parameter.
  (Default = READ)
  
- `client_id` _string_ - Optional.
  Your app has a client_id after you register it on AAD.
  To be provided if user wants to create a report and `access_token` or `auth` is not provided.
  Power BI User will be authenticated automatically using Device Flow authentication using this client_id.
  
- `dataset_id` _string_ - Optional.
  Create report based on the dataset configured on Power BI workspace.
  To be provided if user wants to create a report.
  
**Returns**:

- `object` - Report object

**Code snippet**:
```python
# Instantiate report object with Power BI report embed token and embed URL
report = Report(access_token=access_token, embed_url=embed_url, token_type=models.TokenType.EMBED.value)
```

<br>

<a name="powerbiclient.report.Report.set_access_token"></a>
## set\_access\_token

```python
set_access_token(access_token)
```

Set access token for Power BI report

**Arguments**:

- `access_token` _string_ - report access token

**Code snippet**:
```python
# Set new access token to the embedded report
report.set_access_token(access_token)
```

<br>

<a name="powerbiclient.report.Report.set_dimensions"></a>
## set\_dimensions

```python
set_dimensions(container_height, container_width)
```

Set width and height of Power BI report in px

**Arguments**:

- `container_height` _number_ - report height
- `container_width` _number_ - report width

**Code snippet**:
```python
# Set report height and width using report object
report.set_dimensions(container_height, container_width)
```

<br>

<a name="powerbiclient.report.Report.export_visual_data"></a>
## export\_visual\_data

```python
export_visual_data(page_name, visual_name, rows=10, export_data_type=ExportDataType.SUMMARIZED.value)
```

Returns the data of given visual of the embedded Power BI report

**Arguments**:

- `page_name` _string_ - Page name of the report's page containing the target visual
- `visual_name` _string_ - Visual's unique name
- `rows` _int, optional_ - Number of rows of data. Defaults to 10
- `export_data_type` _number, optional_ - Type of data to be exported (SUMMARIZED: 0, UNDERLYING: 1).
  (Default = SUMMARIZED)
  

**Returns**:

- `string` - visual's exported data

**Code snippet**:
```python
# Get 50 rows of provided visual's summarized data
exported_data = report.export_visual_data(page_name, visual_name, rows=50, export_data_type=ExportDataType.SUMMARIZED.value)
```

<br>

<a name="powerbiclient.report.Report.on"></a>
## on

```python
on(event, callback)
```

Register a callback to execute when the report emits the target event
Parameters

**Arguments**:

- `event` _string_ - Name of Power BI event (eg. 'loaded', 'rendered', 'error')
- `callback` _function_ - User defined function. Callback function is invoked with event details as parameter

**Code snippet**:
```python
# Create a method to be executed on report 'loaded' event to print 'Report is loaded'
def loaded_callback(event_details):
  print('Report is loaded')

# Bind callback method with the report 'loaded' event
report.on('loaded', loaded_callback)
```

<br>

<a name="powerbiclient.report.Report.update_filters"></a>
## update\_filters

```python
update_filters(filters)
```

Set report level filters in the embedded report.
Currently supports models.FiltersOperations.Add

**Arguments**:

- `filters` _[models.ReportLevelFilters]_ - List of report level filters
  

**Raises**:

- `Exception` - When report is not embedded

**Code snippet**:
```python
# Create a basic filter to filter the report with value "East" in column "Region" of table "Geo"
region_filter = {
  '$schema': "http://powerbi.com/product/schema#basic",
  'target': {
      'table': "Geo",
      'column': "Region"
  },
  'operator': "In",
  'values': ["East"]
}

# Apply the basic filter by passing it in a List of filters in update_filters() method
report.update_filters([region_filter])
```

<br>

<a name="powerbiclient.report.Report.remove_filters"></a>
## remove\_filters

```python
remove_filters()
```

Remove all report level filters from the embedded report

**Raises**:

- `Exception` - When report is not embedded

**Code snippet**:
```python
# Remove all the report level filters from the embedded report
report.remove_filters()
```

<br>

<a name="powerbiclient.report.Report.get_pages"></a>
## get\_pages

```python
get_pages()
```

Returns the list of pages of the embedded Power BI report

**Returns**:

- `string` - list of pages

**Code snippet**:
```python
# Get the list of pages from embedded report
pages = report.get_pages()
```

<br>

<a name="powerbiclient.report.Report.visuals_on_page"></a>
## visuals\_on\_page

```python
visuals_on_page(page_name)
```

Returns the list of visuals of the given page of the embedded Power BI report

**Arguments**:

- `page_name` _string_ - Page name of the embedded report
  

**Returns**:

- `string` - list of visuals

**Code snippet**:
```python
# Get the list of visuals on a page
visuals = report.visuals_on_page(page_name)
```

<br>

<a name="powerbiclient.report.Report.set_bookmark"></a>
## set\_bookmark

```python
set_bookmark(bookmark_name)
```

Applies a bookmark by name on the embedded report.

**Arguments**:

  bookmark_name (string) : Bookmark Name

**Raises**:

- `Exception` - When report is not embedded

**Code snippet**:
```python
# Apply a bookmark on the embedded report using report bookmark's name
report.set_bookmark(bookmark_name)
```

<br>

<a name="powerbiclient.report.Report.get_bookmarks"></a>
## get\_bookmarks

```python
get_bookmarks()
```

Returns the list of bookmarks of the embedded Power BI report

**Returns**:

- `list` - list of bookmarks
  

**Raises**:

- `Exception` - When report is not embedded

**Code snippet**:
```python
# Get the list of report bookmarks, if any
bookmarks = report.get_bookmarks()
```

<a name="powerbiclient.authentication"></a>
# powerbiclient.authentication

Authenticates a Power BI User and acquires an access token

**Code snippet**:
```python
# Import authentication module
from powerbiclient import authentication
```

<a name="powerbiclient.authentication.AuthenticationResult"></a>
## AuthenticationResult class

```python
class AuthenticationResult()
```

<br>

<a name="powerbiclient.authentication.AuthenticationResult.__init__"></a>
## \_\_init\_\_ AuthenticationResult

```python
__init__(client_id, scopes, access_token_result)
```

Create an instance of Authentication

**Arguments**:

- `client_id` _string_ - your app has a client_id after you register it on AAD
- `scopes` _list[string]_ - scopes requested to access Power BI API
- `access_token_result` _dict_ - authentication result
  

**Returns**:

- `object` - Authentication object

<br>

<a name="powerbiclient.authentication.AuthenticationResult.get_access_token"></a>
## get\_access\_token

```python
get_access_token()
```

Returns the access token

**Returns**:

- `string` - access token

**Code snippet**:
```python
# Get the access token using authentication object
access_token = auth.get_access_token()
```

<br>

<a name="powerbiclient.authentication.AuthenticationResult.get_access_token_details"></a>
## get\_access\_token\_details

```python
get_access_token_details()
```

Returns the authentication result with access token

**Returns**:

- `dict` - authentication result

**Code snippet**:
```python
# Get the authentication result using authentication object
auth_result = auth.get_access_token_details()
```

<br>

<a name="powerbiclient.authentication.AuthenticationResult.refresh_token"></a>
## refresh\_token

```python
refresh_token()
```

Acquire token(s) based on a refresh token obtained from authentication result

**Code snippet**:
```python
# Acquire new access token from refresh token using authentication object
auth.refresh_token()
```

<br>

<a name="powerbiclient.authentication.DeviceCodeLoginAuthentication"></a>
## DeviceCodeLoginAuthentication class

```python
class DeviceCodeLoginAuthentication(AuthenticationResult)
```
Inherits AuthenticationResult class

**Code snippet**:
```python
# Import DeviceCodeLoginAuthentication class
from powerbiclient.authentication import DeviceCodeLoginAuthentication
```

<a name="powerbiclient.authentication.DeviceCodeLoginAuthentication.__init__"></a>
## \_\_init\_\_ DeviceCodeLoginAuthentication

```python
__init__(client_id=None, scopes=None)
```

Initiate a Device Flow Auth instance

**Arguments**:

- `client_id` _string_ - your app has a client_id after you register it on AAD
- `scopes` _list[string]_ - scopes requested to access Power BI API


**Returns**:

- `object` - Device Flow object

**Code snippet**:
```python
# Initiate device flow authentication with default client Id and Power BI scopes
auth = DeviceCodeLoginAuthentication()
```

<a name="powerbiclient.authentication.InteractiveLoginAuthentication"></a>
## InteractiveLoginAuthentication class

```python
class InteractiveLoginAuthentication(AuthenticationResult)
```
Inherits AuthenticationResult class

**Code snippet**:
```python
# Import InteractiveLoginAuthentication class
from powerbiclient.authentication import InteractiveLoginAuthentication
```

<a name="powerbiclient.authentication.InteractiveLoginAuthentication.__init__"></a>
## \_\_init\_\_ InteractiveLoginAuthentication

```python
__init__(client_id=None, scopes=None)
```

Acquire token interactively i.e. via a local browser

**Arguments**:

- `client_id` _string_ - your app has a client_id after you register it on AAD
- `scopes` _list[string]_ - scopes requested to access Power BI API
  

**Returns**:

- `object` - Interactive authentication object

**Code snippet**:
```python
# Initiate interactive login authentication with default client Id and Power BI scopes
auth = InteractiveLoginAuthentication()
```