<a name="powerbiclient"></a>
# powerbiclient

## Table of content

* [**Quick start**](#Quick-start)
* [**Authenticate to Power BI and acquire an access token**](#Authenticate-to-Power-BI-and-acquire-an-access-token)
  * [Authentication result](#Authentication-result)
    * [Import powerbiclient.authentication](#Import-powerbiclient.authentication)
    * [Create instance of Authentication](#\_\_init\_\_-AuthenticationResult)
    * [Get access token](#get\_access\_token)
    * [Get authentication result](#get\_access\_token\_details)
    * [Refresh token](#refresh\_token)
  * [Device Flow Authentication](#Device-Flow-Authentication)
    * [Import DeviceCodeLoginAuthentication](#Import-DeviceCodeLoginAuthentication)
    * [Create instance of Device Flow Authentication](#\_\_init\_\_-DeviceCodeLoginAuthentication)
  * [Interactive Flow Authentication](#Interactive-Flow-Authentication)
    * [Import InteractiveLoginAuthentication](#Import-InteractiveLoginAuthentication)
    * [Create instance of Interactive Authentication](#\_\_init\_\_-InteractiveLoginAuthentication)
* [**PowerBI report embedding widget**](#PowerBI-report-embedding-widget)
  * [Report class](#Report-class)
  * [Import Report](#Import-Report)
  * [Create an instance of Power BI report](#\_\_init\_\_-Report)
  * [Set a new access token for the report](#set\_access\_token)
  * [Set width and height of the report container in pixels](#set\_size)
  * [Register a callback to a report event](#on)
  * [Unregister a callback for a report event](#off)
  * [Get a list of the report's pages](#get\_pages)
  * [Get visuals list of the given page of the report](#visuals\_on\_page)
  * [Export the data of a given visual of the report](#export\_visual\_data)
  * [Get a list of applied report level filters](#get\_filters)
  * [Add and update report level filters in the report](#update\_filters)
  * [Remove all report level filters](#remove\_filters)
  * [Get the list of the report's bookmarks](#get\_bookmarks)
  * [Apply a bookmark by name on the report](#set\_bookmark)
<br>
# Quick start
The below example shows how to:
- Import Report class and authentication modules
- Use device authentication to authenticate to Power BI
- Embed report by group id and report id

```python
# Import Report class
from powerbiclient import Report

# Import DeviceCodeLoginAuthentication class to authenticate to Power BI
from powerbiclient.authentication import DeviceCodeLoginAuthentication

# Initiate device authentication
device_auth = DeviceCodeLoginAuthentication()

# Set workspace Id and report Id
group_id="<YOUR_WORKSPACE_ID>"
report_id="<YOUR_REPORT_ID>"

# Create an instance of Power BI Report (Use either of the below instances)
# Use auth object
report = Report(group_id=group_id, report_id=report_id, auth=device_auth)

# Load the report in the output cell.
report
```
<br>

<a name="powerbiclient.authentication"></a>
# Authenticate to Power BI and acquire an access token

The following section explains how to authenticate the user to enable report embedding.

## Import powerbiclient.authentication

```python
# Import authentication module
from powerbiclient import authentication
```

<a name="powerbiclient.authentication.AuthenticationResult"></a>
## Authentication result
Base class for available authentication methods. Not to be used explicitly.

```python
class AuthenticationResult()
```

<br>

<a name="powerbiclient.authentication.AuthenticationResult.__init__"></a>
### \_\_init\_\_ AuthenticationResult
Create instance of Authentication

```python
__init__(self, access_token_result)
```

**Arguments**:

- `access_token_result` _dict_ - Authentication result. A dict representing the json response from AAD. A successful response would contain "access_token" key.


**Returns**:

- `object` - AuthenticationResult object

<br>

<a name="powerbiclient.authentication.AuthenticationResult.get_access_token"></a>
### get\_access\_token

```python
get_access_token()
```

**Returns**:

- `string` - access token

**Example**:
```python
# Get the access token using authentication object
access_token = auth.get_access_token()
```

<br>

<a name="powerbiclient.authentication.AuthenticationResult.get_access_token_details"></a>
### get\_access\_token\_details

Returns the authentication result - a dict representing the json response from AAD.

```python
get_access_token_details()
```


**Returns**:

- `dict` - authentication result

**Example**:
```python
# Get the authentication result using authentication object
auth_result = auth.get_access_token_details()
```

<br>

<a name="powerbiclient.authentication.AuthenticationResult.refresh_token"></a>
### refresh\_token
Acquire a token based on the refresh token obtained from the authentication result

```python
refresh_token()
```

**Example**:
```python
# Acquire a new access token from refresh token using authentication object
auth.refresh_token()
```

<br>

<a name="powerbiclient.authentication.DeviceCodeLoginAuthentication"></a>
## Device Flow Authentication

Inherits from AuthenticationResult class. Obtain token by a device flow object. 

```python
class DeviceCodeLoginAuthentication(AuthenticationResult)
```

### Import DeviceCodeLoginAuthentication
```python
# Import DeviceCodeLoginAuthentication class
from powerbiclient.authentication import DeviceCodeLoginAuthentication
```

<a name="powerbiclient.authentication.DeviceCodeLoginAuthentication.__init__"></a>
### \_\_init\_\_ DeviceCodeLoginAuthentication
Create instance of Device Flow Authentication. 

```python
__init__(self)
```

**Returns**:
- `object` - Device Flow object

**Example**:
```python
# Initiate device flow authentication
auth = DeviceCodeLoginAuthentication()
```

<br>

<a name="powerbiclient.authentication.InteractiveLoginAuthentication"></a>
## Interactive Flow Authentication

Inherits from AuthenticationResult class. Acquire token interactively i.e. via a local browser.

```python
class InteractiveLoginAuthentication(AuthenticationResult)
```

### Import InteractiveLoginAuthentication
```python
# Import InteractiveLoginAuthentication class
from powerbiclient.authentication import InteractiveLoginAuthentication
```

<a name="powerbiclient.authentication.InteractiveLoginAuthentication.__init__"></a>
### \_\_init\_\_ InteractiveLoginAuthentication

Create instance of Interactive Authentication.

```python
__init__(self)
```

**Returns**:

- `object` - Interactive authentication object

**Example**:
```python
# Initiate interactive login authentication with default client Id and Power BI scopes
auth = InteractiveLoginAuthentication()
```

<br>

<a name="powerbiclient.report"></a>
# Power BI report embedding widget

The following section explains how to create a Power BI report embedding widget in Jupyter Notebook.

<a name="powerbiclient.report.Report"></a>
## Report class
Embed a Power BI report.

```python
class Report(DOMWidget)
```

<br>

### Import Report
```python
# Import Report class
from powerbiclient import Report
```

<br>

<a name="powerbiclient.report.Report.__init__"></a>
### \_\_init\_\_ Report
Create an instance of a Power BI report. Provide a report ID for viewing or editing an existing report, or a dataset ID for creating a new report.

```python
__init__(self, group_id, report_id=None, auth=None, view_mode=EmbedMode.VIEW.value, permissions=None, dataset_id=None, **kwargs)
```

**Arguments**:

- `group_id` _string_ - Optional.
  Id of Power BI Workspace where your report resides. If value is not provided, My workspace will be used.
  
- `report_id` _string_ - Optional.
  Id of Power BI report. Must be provided to view or edit an existing report.
  
- `auth` _object_ - Optional.
  We have 3 authentication options to embed a Power BI report:
   - Access token (string)
   - Authentication object (object) - instance of AuthenticationResult (DeviceCodeLoginAuthentication or InteractiveLoginAuthentication)
   - If not provided, Power BI user will be authenticated using Device Flow authentication

- `view_mode` _number_ - Optional.
  Mode for embedding Power BI report (VIEW: 0, EDIT: 1, CREATE: 2).
  To be provided if user wants to edit or create a report.
  (Default = VIEW)
  
- `permissions` _number_ - Optional.
  Permissions required while embedding report in EDIT mode. Ignored in VIEW or CREATE mode.

  Values for permissions:
    - `READWRITE` - Users can view, edit, and save the report.
    - `COPY` - Users can save a copy of the report by using Save As.
    - `ALL` - Users can create, view, edit, save, and save a copy of the report.
  
- `dataset_id` _string_ - Optional.
  Create report based on the dataset configured on Power BI workspace.
  Must be provided to create a new report from an existing dataset if report_id is not provided.
  
**Returns**:

- `object` - Report object

**Examples**:
```python
# Instantiate report object with access token
report = Report(group_id=group_id, report_id=report_id, auth=access_token)

# Instantiate report object with authentication object (e.g DeviceCodeLoginAuthentication)
report = Report(group_id=group_id, report_id=report_id, auth=device_auth)

# Instantiate report object withouth auth (will trigger device flow authentication)
report = Report(group_id=group_id, report_id=report_id)

# Instantiate report object in EDIT mode
report_edit = Report(group_id=group_id, report_id=report_id, auth=auth, view_mode=models.EmbedMode.EDIT.value, permissions=models.Permissions.READWRITE.value)

# Instantiate report object in CREATE mode
report_create = Report(group_id=group_id, auth=auth, view_mode=models.EmbedMode.CREATE.value, dataset_id=dataset_id)
```

<br>

<a name="powerbiclient.report.Report.set_access_token"></a>
### set\_access\_token
Set a new access token for the report

```python
set_access_token(access_token)
```

**Arguments**:

- `access_token` _string_ - report access token

**Example**:
```python
# Set new access token to the embedded report
report.set_access_token(access_token)
```

<br>

<a name="powerbiclient.report.Report.set_dimensions"></a>
### set\_size
Set width and height of the report container in pixels

```python
set_size(container_height, container_width)
```

**Arguments**:

- `container_height` _number_ - container height
- `container_width` _number_ - container width

**Example**:
```python
# Set report container's height and width using report object
report.set_size(container_height, container_width)
```


<br>

<a name="powerbiclient.report.Report.on"></a>
### on
Register a callback to execute when the report emits the target event

```python
on(event, callback)
```

**Arguments**:

- `event` _string_ - Name of Power BI event (supported events: 'loaded', 'rendered')
- `callback` _function_ - User defined function. Callback function is invoked with event details as parameter

**Note:** _Currently supports only 'loaded' and 'rendered' report events_

**Example**:
```python
# Create a method to be executed on report 'loaded' event to print 'Report is loaded'
def loaded_callback(event_details):
  print('Report is loaded')

# Bind callback method with the report 'loaded' event
report.on('loaded', loaded_callback)
```

<br>

<a name="powerbiclient.report.Report.off"></a>
### off
Unregister a callback for a report event

```python
off(event)
```

**Arguments**:

- `event` _string_ - Name of Power BI event (supported events: 'loaded', 'rendered')

**Note:** _Currently supports only 'loaded' and 'rendered' report events_

**Example**:
```python
# Unsubscribe the report 'loaded' event
report.off('loaded')
```

<br>

**The following functions are only available for reports embedded in VIEW or EDIT mode**


<a name="powerbiclient.report.Report.get_pages"></a>
### get\_pages
Get a list of the report's pages

```python
get_pages()
```

**Returns**:

- `list` - list of pages

**Example**:
```python
# Get the list of pages from embedded report
pages = report.get_pages()
```

<br>

<a name="powerbiclient.report.Report.visuals_on_page"></a>
### visuals\_on\_page
Get visuals list of the given page of the report

```python
visuals_on_page(page_name)
```

**Arguments**:

- `page_name` _string_ - Page name of the embedded report
  

**Returns**:

- `list` - list of visuals

**Example**:
```python
# Get the list of visuals on a page
visuals = report.visuals_on_page(page_name)
```

<br>

<a name="powerbiclient.report.Report.export_visual_data"></a>
### export\_visual\_data
Export the data of a given visual of the report

```python
export_visual_data(page_name, visual_name, rows=None, export_data_type=models.ExportDataType.SUMMARIZED.value)
```

**Arguments**:

- `page_name` _string_ - Page name of the report's page containing the target visual
- `visual_name` _string_ - Visual's unique name
- `rows` _int, optional_ - Number of data rows to export (default - exports all rows)
- `export_data_type` _number, optional_ - Type of data to be exported (SUMMARIZED: 0, UNDERLYING: 1), Default = SUMMARIZED

**Returns**:

- `string` - visual's exported data

**Example**:
```python
# Get 50 rows of provided visual's summarized data
exported_data = report.export_visual_data(page_name, visual_name, rows=50, export_data_type=models.ExportDataType.SUMMARIZED.value)

# Get all rows of provided visual's summarized data
exported_data = report.export_visual_data(page_name, visual_name, export_data_type=models.ExportDataType.SUMMARIZED.value)
```

<br>

<a name="powerbiclient.report.Report.get_filters"></a>
### get\_filters
Get a list of applied report level filters

```python
get_filters()
```

**Returns**:

- `list` - list of filters

**Example**:
```python
# Get the list of filters applied on embedded report
filters = report.get_filters()
```

<br>

<a name="powerbiclient.report.Report.update_filters"></a>
### update\_filters
Update report level filters in the embedded report: replaces an existing filter or adds it if it doesn't exist. 

```python
update_filters(filters)
```

**Arguments**:

- `filters` _[models.ReportLevelFilters]_ - List of report level filters

**Example**:
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
### remove\_filters
Remove all report level filters

```python
remove_filters()
```

**Example**:
```python
# Remove all the report level filters from the embedded report
report.remove_filters()
```

<br>

<a name="powerbiclient.report.Report.get_bookmarks"></a>
### get\_bookmarks
Get a list of the report's bookmarks

```python
get_bookmarks()
```

**Returns**:

- `list` - list of bookmarks

**Example**:
```python
# Get the list of report bookmarks, if any
bookmarks = report.get_bookmarks()
```
<br>

<a name="powerbiclient.report.Report.set_bookmark"></a>
### set\_bookmark
Apply a bookmark by name on the report

```python
set_bookmark(bookmark_name)
```

**Arguments**:

  bookmark_name (string) : Bookmark Name

**Example**:
```python
# Apply a bookmark on the embedded report using report bookmark's name
report.set_bookmark(bookmark_name)
```
