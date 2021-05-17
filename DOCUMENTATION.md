<a name="powerbiclient"></a>
# powerbiclient

## Table of content

* [**Quick start**](#Quick-start)
* [**PowerBI report embedding widget**](#PowerBI-report-embedding-widget)
  * [Create an instance of a report](#Create-an-instance-of-a-report)
  * [Set a new access token for report](#Set-a-new-access-token-for-report)
  * [Set width and height of the report container in pixels](#Set-width-and-height-of-the-report-container-in-pixels)
  * [Export the data of a given visual of the report](#Export-the-data-of-a-given-visual-of-the-report)
  * [Register a callback to a report event](#Register-a-callback-to-a-report-event)
  * [Unregister a callback for a report event](#Unregister-a-callback-for-a-report-event)
  * [Get the list of applied report level filters](#Get-the-list-of-applied-report-level-filters)
  * [Add report level filters in the report](#Add-report-level-filters-in-the-report)
  * [Remove all report level filters](#Remove-all-report-level-filters)
  * [Get the list of the report's pages](#Get-the-list-of-the-report's-pages)
  * [Get the list of visuals of the given page of the report](#Get-the-list-of-visuals-of-the-given-page-of-the-report)
  * [Apply a bookmark by name on the report](#Apply-a-bookmark-by-name-on-the-report)
  * [Get the list of the report's bookmarks](#Get-the-list-of-the-report's-bookmarks)
* [**Authenticate to Power BI and acquire access token**](#Authenticate-to-Power-BI-and-acquire-access-token)
  * [Authentication result](#Authentication-result)
    * [Create instance of Authentication](#Create-instance-of-Authentication)
    * [Get access token](#Get-access-token)
    * [Get authentication result](#Get-authentication-result)
    * [Acquire token based on a refresh token obtained from authentication result](#Acquire-token-based-on-a-refresh-token-obtained-from-authentication-result)
  * [Device Flow Authentication](#Device-Flow-Authentication)
    * [Initiate a Device Flow Auth instance](#Initiate-a-Device-Flow-Auth-instance)
  * [Interactive Flow Authentication](#Interactive-Flow-Authentication)
    * [Acquire token interactively](#Acquire-token-interactively)
  * [Master User Authentication](#Master-User-Authentication)
    * [Acquire token with username and password](#Acquire-token-with-username-and-password)
  * [Service Principal Authentication](#Service-Principal-Authentication)
    * [Acquire token with Service Principal](#Acquire-token-with-Service-Principal)
* [**Configure Azure AD app to authenticate to Power BI**](#Configure-Azure-AD-app-to-authenticate-to-Power-BI)

# Quick start
The below example shows how to:
- Import Report class, models and authentication modules
- Use device authentication to authenticate to Power BI
- Embed report by group id and report id

```python
# Import Report class and models
from powerbiclient import Report, models

# Import DeviceCodeLoginAuthentication class to authenticate to Power BI
from powerbiclient.authentication import DeviceCodeLoginAuthentication

# Initiate device authentication
device_auth = DeviceCodeLoginAuthentication()

# Get access token from auth object
access_token = device_auth.get_access_token()

# Set workspace Id and report Id
group_id="<YOUR_WORKSPACE_ID>"
report_id="<YOUR_REPORT_ID>"

# Create an instance of Power BI Report (Use either of the below instances)
# Use auth object
report = Report(group_id=group_id, report_id=report_id, auth=device_auth)

# Use access token from device authentication
report = Report(group_id=group_id, report_id=report_id, access_token=access_token, token_type=models.TokenType.AAD.value)

# Load the report in the output cell
report
```

<a name="powerbiclient.report"></a>
# PowerBI report embedding widget
## powerbiclient.report

Embeds Power BI Report

<a name="powerbiclient.report.Report"></a>
## Report class

```python
class Report(DOMWidget)
```

**Example**:
```python
# Import Report class
from powerbiclient import Report
```

<br>

<a name="powerbiclient.report.Report.__init__"></a>
## Create an instance of a report
## \_\_init\_\_ Report

```python
__init__(access_token=None, embed_url=None, token_type=models.TokenType.AAD.value, group_id=None, report_id=None, auth=None, embed_token_request_body=None, view_mode=models.EmbedMode.VIEW.value, permissions=models.Permissions.READ.value, client_id=None, tenant=None, scopes=None, dataset_id=None, **kwargs)
```

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
  Id of Power BI Workspace where your report resides.
  It will be used if `embed_url` is not provided
  
- `report_id` _string_ - Optional.
  Id of Power BI report.
  It will be used if `embed_url` is not provided
  
- `auth` _object_ - Optional.
  Authentication object.
  It will be used if `access_token` is not provided.
  If not provided, Power BI User will be authenticated automatically using Device Flow authentication

- `embed_token_request_body` _JSON_ - Optional.
  JSON formatted request body to be used while calling Reports GenerateTokenInGroup API.
  For embedding Power BI report, refer: https://docs.microsoft.com/en-us/rest/api/power-bi/embedtoken/reports_generatetokeningroup.
  For creating Power BI report, refer: https://docs.microsoft.com/en-us/rest/api/power-bi/embedtoken/datasets_generatetokeningroup.
  It will be used if MasterUserAuthentication or ServicePrincipalAuthentication object is provided using `auth` parameter.
  (Default = { "accessLevel": "View" })

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
  Your Azure AD app has a client Id after you register it on AAD.
  To be provided if user wants to authenticate using own Azure AD app and `access_token` or `auth` is not provided.
  Power BI User will be authenticated automatically using Device Flow authentication using this client Id.
  Refer [Configure Azure AD app to authenticate to Power BI](#Configure-Azure-AD-app-to-authenticate-to-Power-BI) section.
  (Default = Microsoft Azure Cross-platform Command Line Interface AAD app Id)

- scopes _list[string]_ - Optional.
  Scopes required to access Power BI API
  (Default = Power BI API default permissions)

- tenant _string_ - Optional.
  Organization tenant Id
  (Default = "organizations")
  
- `dataset_id` _string_ - Optional.
  Create report based on the dataset configured on Power BI workspace.
  To be provided if user wants to create a report.
  
**Returns**:

- `object` - Report object

**Example**:
```python
# Instantiate report object with Power BI report embed token and embed URL
report = Report(access_token=access_token, embed_url=embed_url, token_type=models.TokenType.EMBED.value)
```

<br>

<a name="powerbiclient.report.Report.set_access_token"></a>
## Set a new access token for report
## set\_access\_token

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
## Set width and height of the report container in pixels
## set\_dimensions

```python
set_dimensions(container_height, container_width)
```

**Arguments**:

- `container_height` _number_ - container height
- `container_width` _number_ - container width

**Example**:
```python
# Set report container's height and width using report object
report.set_dimensions(container_height, container_width)
```

<br>

<a name="powerbiclient.report.Report.export_visual_data"></a>
## Export the data of a given visual of the report
## export\_visual\_data

```python
export_visual_data(page_name, visual_name, rows=10, export_data_type=models.ExportDataType.SUMMARIZED.value)
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

**Example**:
```python
# Get 50 rows of provided visual's summarized data
exported_data = report.export_visual_data(page_name, visual_name, rows=50, export_data_type=models.ExportDataType.SUMMARIZED.value)
```

<br>

<a name="powerbiclient.report.Report.on"></a>
## Register a callback to a report event
## on

```python
on(event, callback)
```

Register a callback to execute when the report emits the target event

**Arguments**:

- `event` _string_ - Name of Power BI event (eg. 'loaded', 'rendered', 'error')
- `callback` _function_ - User defined function. Callback function is invoked with event details as parameter

**Note:** _Currently supports only 'loaded', 'rendered' and 'error' report events_

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
## Unregister a callback for a report event
## off

```python
off(event)
```

Unregisters a callback on target event

**Arguments**:

- `event` _string_ - Name of Power BI event (eg. 'loaded', 'rendered', 'error')

**Note:** _Currently supports only 'loaded', 'rendered' and 'error' report events_

**Example**:
```python
# Unsubscribe the report 'loaded' event
report.off('loaded')
```

<br>

<a name="powerbiclient.report.Report.get_filters"></a>
## Get the list of applied report level filters
## get\_filters

```python
get_filters()
```

Returns the list of filters applied on the embedded Power BI report

**Returns**:

- `list` - list of filters

**Example**:
```python
# Get the list of filters applied on embedded report
filters = report.get_filters()
```

<br>

<a name="powerbiclient.report.Report.update_filters"></a>
## Add report level filters in the report
## update\_filters

```python
update_filters(filters)
```

Currently supports only replace option for filters, replacing existing filters and add new filters that are provided. (models.FiltersOperations.Replace)

**Arguments**:

- `filters` _[models.ReportLevelFilters]_ - List of report level filters
  

**Raises**:

- `Exception` - When report is not embedded

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
## Remove all report level filters
## remove\_filters

```python
remove_filters()
```

**Raises**:

- `Exception` - When report is not embedded

**Example**:
```python
# Remove all the report level filters from the embedded report
report.remove_filters()
```

<br>

<a name="powerbiclient.report.Report.get_pages"></a>
## Get the list of the report's pages
## get\_pages

```python
get_pages()
```

Returns the list of pages of the embedded Power BI report

**Returns**:

- `list` - list of pages

**Example**:
```python
# Get the list of pages from embedded report
pages = report.get_pages()
```

<br>

<a name="powerbiclient.report.Report.visuals_on_page"></a>
## Get the list of visuals of the given page of the report
## visuals\_on\_page

```python
visuals_on_page(page_name)
```

Returns the list of visuals of the given page of the embedded Power BI report

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

<a name="powerbiclient.report.Report.set_bookmark"></a>
## Apply a bookmark by name on the report
## set\_bookmark

```python
set_bookmark(bookmark_name)
```

**Arguments**:

  bookmark_name (string) : Bookmark Name

**Raises**:

- `Exception` - When report is not embedded

**Example**:
```python
# Apply a bookmark on the embedded report using report bookmark's name
report.set_bookmark(bookmark_name)
```

<br>

<a name="powerbiclient.report.Report.get_bookmarks"></a>
## Get the list of the report's bookmarks
## get\_bookmarks

```python
get_bookmarks()
```

Returns the list of bookmarks of the embedded Power BI report

**Returns**:

- `list` - list of bookmarks
  

**Raises**:

- `Exception` - When report is not embedded

**Example**:
```python
# Get the list of report bookmarks, if any
bookmarks = report.get_bookmarks()
```

<a name="powerbiclient.authentication"></a>
# Authenticate to Power BI and acquire access token
## powerbiclient.authentication

**Example**:
```python
# Import authentication module
from powerbiclient import authentication
```

<a name="powerbiclient.authentication.AuthenticationResult"></a>
## Authentication result
## AuthenticationResult class

```python
class AuthenticationResult()
```

<br>

<a name="powerbiclient.authentication.AuthenticationResult.__init__"></a>
## Create instance of Authentication
## \_\_init\_\_ AuthenticationResult

```python
__init__(client_id, scopes, authority_uri, access_token_result)
```

**Arguments**:

- `client_id` _string_ - Your Azure AD app has a client Id after you register it on AAD.
  Refer [Configure Azure AD app to authenticate to Power BI](#Configure-Azure-AD-app-to-authenticate-to-Power-BI) section.
- `scopes` _list[string]_ - Scopes required to access Power BI API
- `authority_uri` _string_ - Microsoft authority URI used for authentication
- `access_token_result` _dict_ - Authentication result

**Returns**:

- `object` - Authentication object

<br>

<a name="powerbiclient.authentication.AuthenticationResult.get_access_token"></a>
## Get access token
## get\_access\_token

```python
get_access_token()
```

Returns the access token

**Returns**:

- `string` - access token

**Example**:
```python
# Get the access token using authentication object
access_token = auth.get_access_token()
```

<br>

<a name="powerbiclient.authentication.AuthenticationResult.get_access_token_details"></a>
## Get authentication result
## get\_access\_token\_details

```python
get_access_token_details()
```

Returns the authentication result with access token

**Returns**:

- `dict` - authentication result

**Example**:
```python
# Get the authentication result using authentication object
auth_result = auth.get_access_token_details()
```

<br>

<a name="powerbiclient.authentication.AuthenticationResult.refresh_token"></a>
## Acquire token based on a refresh token obtained from authentication result
## refresh\_token

```python
refresh_token()
```

**Example**:
```python
# Acquire new access token from refresh token using authentication object
auth.refresh_token()
```

<br>

<a name="powerbiclient.authentication.DeviceCodeLoginAuthentication"></a>
## Device Flow Authentication
## DeviceCodeLoginAuthentication class

```python
class DeviceCodeLoginAuthentication(AuthenticationResult)
```
Inherits AuthenticationResult class

**Example**:
```python
# Import DeviceCodeLoginAuthentication class
from powerbiclient.authentication import DeviceCodeLoginAuthentication
```

<a name="powerbiclient.authentication.DeviceCodeLoginAuthentication.__init__"></a>
## Initiate a Device Flow Auth instance
## \_\_init\_\_ DeviceCodeLoginAuthentication

```python
__init__(client_id=None, scopes=None)
```

**Arguments**:

- `client_id` _string_ - Optional.
  Your Azure AD app has a client Id after you register it on AAD.
  Refer [Configure Azure AD app to authenticate to Power BI](#Configure-Azure-AD-app-to-authenticate-to-Power-BI) section.
  (Default = Microsoft Azure Cross-platform Command Line Interface Azure AD app Id)
- `scopes` _list[string]_ - Optional.
  Scopes required to access Power BI API
  (Default = Power BI API default permissions)
- `tenant` _string_ - Optional.
  Organization tenant Id
  (Default = "organizations")

**Returns**:

- `object` - Device Flow object

**Example**:
```python
# Initiate device flow authentication with default client Id and Power BI scopes
auth = DeviceCodeLoginAuthentication()
```

<a name="powerbiclient.authentication.InteractiveLoginAuthentication"></a>
## Interactive Flow Authentication
## InteractiveLoginAuthentication class

```python
class InteractiveLoginAuthentication(AuthenticationResult)
```
Inherits AuthenticationResult class

**Example**:
```python
# Import InteractiveLoginAuthentication class
from powerbiclient.authentication import InteractiveLoginAuthentication
```

<a name="powerbiclient.authentication.InteractiveLoginAuthentication.__init__"></a>
## Acquire token interactively
## \_\_init\_\_ InteractiveLoginAuthentication

```python
__init__(client_id=None, scopes=None)
```

Acquire token interactively i.e. via a local browser

**Arguments**:

- `client_id` _string_ - Optional.
  Your Azure AD app has a client Id after you register it on AAD.
  Refer [Configure Azure AD app to authenticate to Power BI](#Configure-Azure-AD-app-to-authenticate-to-Power-BI) section.
  (Default = Microsoft Azure Cross-platform Command Line Interface Azure AD app Id)
- `scopes` _list[string]_ - Optional.
  Scopes required to access Power BI API
  (Default = Power BI API default permissions)
- `tenant` _string_ - Optional.
  Organization tenant Id
  (Default = "organizations")
  

**Returns**:

- `object` - Interactive authentication object

**Example**:
```python
# Initiate interactive login authentication with default client Id and Power BI scopes
auth = InteractiveLoginAuthentication()
```

<a name="powerbiclient.authentication.MasterUserAuthentication"></a>
## Master User Authentication
## MasterUserAuthentication class

```python
class MasterUserAuthentication(AuthenticationResult)
```
Inherits AuthenticationResult class

**Example**:
```python
# Import MasterUserAuthentication class
from powerbiclient.authentication import MasterUserAuthentication
```

<a name="powerbiclient.authentication.MasterUserAuthentication.__init__"></a>
## Acquire token with username and password
## \_\_init\_\_ MasterUserAuthentication

```python
__init__(username, password, client_id=None, scopes=None, tenant=None)
```

**Arguments**:

- `username` _string_ - UPN in the form of an email address.
- `password` _string_ - Password to authenticate Power BI user.
- `client_id` _string_ - Optional.
  Your Azure AD app has a client Id after you register it on AAD.
  Refer [Configure Azure AD app to authenticate to Power BI](#Configure-Azure-AD-app-to-authenticate-to-Power-BI) section.
  (Default = Microsoft Azure Cross-platform Command Line Interface Azure AD app Id)
- `scopes` _list[string]_ - Optional.
  Scopes required to access Power BI API
  (Default = Power BI API default permissions)
- `tenant` _string_ - Optional.
  Organization tenant Id
  (Default = "organizations")
  

**Returns**:

- `object` - Master User authentication object

**Example**:
```python
# Initiate Master User authentication with default tenant, client Id and Power BI scopes
auth = MasterUserAuthentication('pbi_username', 'pbi_password')
```

<a name="powerbiclient.authentication.ServicePrincipalAuthentication"></a>
## Service Principal Authentication
## ServicePrincipalAuthentication class

```python
class ServicePrincipalAuthentication(AuthenticationResult)
```
Inherits AuthenticationResult class

**Example**:
```python
# Import ServicePrincipalAuthentication class
from powerbiclient.authentication import ServicePrincipalAuthentication
```

<a name="powerbiclient.authentication.ServicePrincipalAuthentication.__init__"></a>
## Acquire token with Service Principal
## \_\_init\_\_ ServicePrincipalAuthentication

```python
__init__(client_id, client_secret, tenant, scopes=None)
```

**Arguments**:

- `client_id` _string_ - Your Azure AD app has a client Id after you register it on AAD.
  Refer [Configure Azure AD app to authenticate to Power BI](#Configure-Azure-AD-app-to-authenticate-to-Power-BI) section.
- `client_secret` _string_ - Client secret associated with the Azure AD app
- `tenant` _string_ - Organization tenant Id
- `scopes` _list[string]_ - Optional.
  Scopes required to access Power BI API
  (Default = Power BI API default permissions)
  

**Returns**:

- `object` - Service Principal authentication object

**Example**:
```python
# Initiate interactive login authentication with default client Id and Power BI scopes
client_id = 'AAD_app_id'
client_secret = 'AAD_app_associated_secret'
tenant = 'Org_tenant_Id'

auth = ServicePrincipalAuthentication(client_id, client_secret, tenant)
```

# Configure Azure AD app to authenticate to Power BI

1. Visit Azure portal's [App registrations service](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)

2. Click on **New registration**

3. Enter display name to identify your Azure AD app

4. Select preferred account types option

5. Under **Redirect URI**, select **Public client/native (mobile & desktop)** in the dropdown

6. Click **Register**

7. After successful registration, you will be redirected to Azure AD app configurations. Click **Authentication** in left panel

8. Under **Advanced settings**, toggle **Allow public client flows** to "Yes" and click on Save

9. To get the Azure AD app details, click **Overview** in left panel