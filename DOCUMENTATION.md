<a name="powerbiclient"></a>
# powerbiclient

## Table of contents

* [**Quick start**](#Quick-start)
* [**Authenticate to Power BI and acquire an access token**](#Authenticate-to-Power-BI-and-acquire-an-access-token)
  * [Authentication result](#Authentication-result)
    * [Import powerbiclient.authentication](#Import-powerbiclientauthentication)
    * [Create instance of Authentication](#\_\_init\_\_-AuthenticationResult)
    * [Get access token](#get\_access\_token)
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
  * [Set a new access token for the report](#report-set_access_token)
  * [Set width and height of the report container in pixels](#report-set_size)
  * [Register a callback to a report event](#report-on)
  * [Unregister a callback for a report event](#report-off)
  * [Get a list of the report's pages](#get\_pages)
  * [Get visuals list of the given page of the report](#visuals\_on\_page)
  * [Export the data of a given visual of the report](#export\_visual\_data)
  * [Get a list of applied report level filters](#get\_filters)
  * [Add and update report level filters in the report](#update\_filters)
  * [Remove all report level filters](#remove\_filters)
  * [Get the list of the report's bookmarks](#get\_bookmarks)
  * [Apply a bookmark by name on the report](#set\_bookmark)
  * [Set a page as active](#set\_active_page)
* [**Power BI quick visualization widget**](#Power-BI-quick-visualization-widget)
  * [QuickVisualize class](#QuickVisualize-class)
    * [Create an instance of Power BI quick visualization](#\_\_init\_\_-QuickVisualize)
    * [Set a new access token](#qv-set_access_token)
    * [Set width and height of the Power BI quick visualization container in pixels](#qv-set_size)
    * [Register a callback to a Power BI quick visualization event](#qv-on)
    * [Unregister a callback for a Power BI quick visualization event](#qv-off)
    * [Get saved report](#get-saved-report)
  * [Get dataset create configuration](#Get-dataset-create-configuration)
* [**Considerations and limitations**](#Considerations-and-limitations)
<br>
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
device_auth = DeviceCodeLoginAuthentication(tenant_id) # tenant_id is an optional argument

# Set workspace Id and report Id
group_id="<YOUR_WORKSPACE_ID>"
report_id="<YOUR_REPORT_ID>"

# Create an instance of Power BI Report
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
__init__(self)
```

**Returns**:

- `object` - AuthenticationResult object. The authentication result object should be passed only to trusted code in your notebook.

<br>

<a name="powerbiclient.authentication.AuthenticationResult.get_access_token"></a>
### get\_access\_token

```python
get_access_token(self, force_refresh=False)
```

**Arguments**:

- `force_refresh` - whether to force refresh a new token or not, default is False

**Returns**:

- `string` - access token

**Example**:
```python
# Get the access token using authentication object
access_token = auth.get_access_token()
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
__init__(self, tenant_id=None)
```

**Arguments**:

- `tenant_id` _string_ - Optional.
  Id of Power BI tenant where your report resides. If not specified, the default tenant will be used.

**Returns**:
- `object` - Device flow object. The device flow object should be passed only to trusted code in your notebook.

**Example**:
```python
# Initiate device flow authentication
auth = DeviceCodeLoginAuthentication(tenant_id)
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
__init__(self, tenant_id=None)
```

**Arguments**:

- `tenant_id` _string_ - Optional.
  Id of Power BI tenant where your report resides. If not specified, the default tenant will be used.

**Returns**:

- `object` - Interactive authentication object. The interactive authentication object should be passed only to trusted code in your notebook.

**Example**:
```python
# Initiate interactive login authentication with default client Id and Power BI scopes
auth = InteractiveLoginAuthentication(tenant_id) # tenant_id is an optional argument
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
  Create a new report using this dataset in the provided Power BI workspace. Must be provided to create a new report from an existing dataset if report_id is not provided.

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

<a id="report-set_access_token" name="powerbiclient.report.Report.set_access_token"></a>
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

<a id="report-set_size" name="powerbiclient.report.Report.set_size"></a>
### set\_size
Set height and width of the report container in pixels

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

<a id="report-on" name="powerbiclient.report.Report.on"></a>
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

<a id="report-off" name="powerbiclient.report.Report.off"></a>
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
exported_data = report.export_visual_data(page_name, visual_name)
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
# Apply a bookmark on the embedded report using the bookmark's name
report.set_bookmark(bookmark_name)
```

<br>

<a name="powerbiclient.report.Report.set_active_page"></a>
### set\_active\_page
Set the input page as active

```python
set_active_page(page_name)
```

**Arguments**:

  page_name (string): name of the page you want to set as active

**Example**:
```python
# Set the input page as active
report.set_active_page(page_name)
```

<br>

<a name="powerbiclient.quick_visualize"></a>
# Power BI quick visualization widget

The following section explains how to create a Power BI quick visualization widget in Jupyter Notebook.

<a name="powerbiclient.quick_visualize.QuickVisualize"></a>
## QuickVisualize class
Embed a Power BI quick visualization.

```python
class QuickVisualize(DOMWidget)
```

<br>

### Import QuickVisualize
```python
# Import QuickVisualize class
from powerbiclient import QuickVisualize
```

<br>

<a name="powerbiclient.quick_visualize.QuickVisualize.__init__"></a>
### \_\_init\_\_ QuickVisualize
Create an instance of Power BI quick visualization

```python
__init__(self, dataset_create_config, auth=None, **kwargs)
```

**Arguments**:

- `dataset_create_config` _object_: Required.
  A dict representing the data used to create the report, formatted as IDatasetCreateConfiguration (See: [Embed a quick report in a Power BI embedded analytics application](https://learn.microsoft.com/en-us/javascript/api/overview/powerbi/embed-quick-report#step-11---create-a-dataset-without-a-data-source))

- `auth` _string or object_: Optional.
    We have 3 authentication options to embed Power BI quick visualization:
    - Access token (string)
    - Authentication object (object) - instance of AuthenticationResult (DeviceCodeLoginAuthentication or InteractiveLoginAuthentication)
    - If not provided, Power BI user will be authenticated using Device Flow authentication

**Returns**:

- `QuickVisualize`: _object_

**Examples**:
```python
# Instantiate quick visualization object with access token
qv = QuickVisualize(dataset_create_config=dataset_create_config, auth=access_token)

# Instantiate quick visualization object with authentication object (e.g DeviceCodeLoginAuthentication)
qv = QuickVisualize(dataset_create_config=dataset_create_config, auth=device_auth)

# Instantiate quick visualization object withouth auth (will trigger device flow authentication)
qv = QuickVisualize(dataset_create_config=dataset_create_config)

# Instantiate quick visualization object with pandas DataFrame
qv = QuickVisualize(get_dataset_config(df), auth=auth)
```

<br>

<a id="qv-set_access_token" name="powerbiclient.quick_visualize.QuickVisualize.set_access_token"></a>
### set\_access\_token
Set an access token for the Power BI quick visualization

```python
set_access_token(access_token)
```

**Arguments**:

- `access_token` _string_

**Example**:
```python
# Set a new access token to the Power BI quick visualization
qv.set_access_token(access_token)
```

<br>

<a id="qv-set_size"  name="powerbiclient.quick_visualize.QuickVisualize.set_size"></a>
### set\_size
Set height and width of Power BI quick visualization in px

```python
set_size(container_height, container_width)
```

**Arguments**:

- `container_height` _number_ - container height
- `container_width` _number_ - container width

**Example**:
```python
# Set Power BI quick visualization container's height and width
qv.set_size(container_height, container_width)
```

<br>

<a name="powerbiclient.utils.get_dataset_config"></a>
## Get dataset create configuration
Utility method to get the dataset create configuration dict from a [pandas](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) or [spark](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/dataframe.html) DataFrame. To be used as input for instantiating a quick visualization object.

```python
get_dataset_config(df, locale='en-US')
```

**Arguments**:
  - `df` _object_: Required.
    Pandas or Spark DataFrame instance
  - `locale` _string_: Optional.
    This value is used to evaluate the data and parse values of the given DataFrame. Supported locales can be found here: [supported locales](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-lcid/a9eac961-e77d-41a6-90a5-ce1a8b0cdb9c?redirectedfrom=MSDN)

**Returns**:
  - `dataset_create_config`: _dict_

**Example**:
```python
from powerbiclient import get_dataset_config

# Create an example DataFrame using pandas
df = pd.DataFrame(data={'col1': [1, 2], 'col2': [3, 4]})

# Use the dataset_create_config dict to instantiate a quick visualization object
qv = QuickVisualize(get_dataset_config(df), auth=auth)
```

<br>


<a id="qv-on" name="powerbiclient.quick_visualize.QuickVisualize.on"></a>
### on
Register a callback to execute when the Power BI quick visualization emits the target event

```python
on(event, callback)
```

**Arguments**:

- `event` _string_ - Name of Power BI event (supported events: 'loaded', 'rendered', 'saved')
- `callback` _function_ - User defined function. Callback function is invoked with event details as parameter

**Note:** _Currently supports only 'loaded' ,'rendered' and 'saved' events_

**Example**:
```python
# Create a method to be executed on Power BI quick visualization 'loaded' event
def loaded_callback(event_details):
  print('Quick visualize has loaded')

# Bind callback method with the Power BI quick visualization 'loaded' event
qv.on('loaded', loaded_callback)
```

<br>

<a id="qv-off" name="powerbiclient.quick_visualize.QuickVisualize.off"></a>
### off
Unregister a callback for a Power BI quick visualization event

```python
off(event)
```

**Arguments**:

- `event` _string_ - Name of Power BI event (supported events: 'loaded', 'rendered', 'saved')

**Note:** _Currently supports only 'loaded' ,'rendered' and 'saved' events_

**Example**:
```python
# Unsubscribe the Power BI quick visualization 'loaded' event
qv.off('loaded')
```

<br>

<a id="get-saved-report" name="powerbiclient.quick_visualize.QuickVisualize.get_saved_report"></a>
### get_saved_report
Retrieve the saved report associated with the Power BI quick visualization instance

```python
get_saved_report()
```

**Example**:
```python
# Returns the saved report associated with the Power BI quick visualization instance
report = qv.get_saved_report()
```

<br>

# Considerations and limitations
- Embedding and creating Power BI content in Jupyter notebooks is not available in sovereign and government clouds.
- When creating a Power BI report with the quick visualization widget, the following limitations apply to your data:
  - The table name can't be longer than 80 characters, and column names can't be longer than 512 characters.
  - Column names must be unique.
