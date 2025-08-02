# UserManagementApi

All URIs are relative to *https://api.onevoice.com*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**apiUsersActivityGet**](#apiusersactivityget) | **GET** /api/users/activity | Get user activity log|
|[**apiUsersAvatarDelete**](#apiusersavatardelete) | **DELETE** /api/users/avatar | Delete user avatar|
|[**apiUsersAvatarPost**](#apiusersavatarpost) | **POST** /api/users/avatar | Upload user avatar|
|[**apiUsersCreditsUsageGet**](#apiuserscreditsusageget) | **GET** /api/users/credits/usage | Get user credits usage|
|[**apiUsersDashboardStatsGet**](#apiusersdashboardstatsget) | **GET** /api/users/dashboard/stats | Get dashboard statistics|
|[**apiUsersDeleteAccountPost**](#apiusersdeleteaccountpost) | **POST** /api/users/delete-account | Delete user account|
|[**apiUsersNotificationsPreferencesGet**](#apiusersnotificationspreferencesget) | **GET** /api/users/notifications/preferences | Get notification preferences|
|[**apiUsersNotificationsPreferencesPut**](#apiusersnotificationspreferencesput) | **PUT** /api/users/notifications/preferences | Update notification preferences|
|[**apiUsersPasswordPut**](#apiuserspasswordput) | **PUT** /api/users/password | Change user password|
|[**apiUsersProfileGet**](#apiusersprofileget) | **GET** /api/users/profile | Get user profile|
|[**apiUsersProfilePut**](#apiusersprofileput) | **PUT** /api/users/profile | Update user profile|
|[**apiUsersSubscriptionGet**](#apiuserssubscriptionget) | **GET** /api/users/subscription | Get user subscription details|

# **apiUsersActivityGet**
> ApiUsersActivityGet200Response apiUsersActivityGet()


### Example

```typescript
import {
    UserManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UserManagementApi(configuration);

let page: number; // (optional) (default to 1)
let perPage: number; // (optional) (default to 20)

const { status, data } = await apiInstance.apiUsersActivityGet(
    page,
    perPage
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **page** | [**number**] |  | (optional) defaults to 1|
| **perPage** | [**number**] |  | (optional) defaults to 20|


### Return type

**ApiUsersActivityGet200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Activity log retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiUsersAvatarDelete**
> ApiAuthForgotPasswordPost200Response apiUsersAvatarDelete()


### Example

```typescript
import {
    UserManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UserManagementApi(configuration);

const { status, data } = await apiInstance.apiUsersAvatarDelete();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**ApiAuthForgotPasswordPost200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Avatar deleted successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiUsersAvatarPost**
> ApiUsersAvatarPost200Response apiUsersAvatarPost()


### Example

```typescript
import {
    UserManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UserManagementApi(configuration);

let avatar: File; // (optional) (default to undefined)

const { status, data } = await apiInstance.apiUsersAvatarPost(
    avatar
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **avatar** | [**File**] |  | (optional) defaults to undefined|


### Return type

**ApiUsersAvatarPost200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Avatar uploaded successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiUsersCreditsUsageGet**
> ApiUsersCreditsUsageGet200Response apiUsersCreditsUsageGet()


### Example

```typescript
import {
    UserManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UserManagementApi(configuration);

const { status, data } = await apiInstance.apiUsersCreditsUsageGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**ApiUsersCreditsUsageGet200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Credits usage retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiUsersDashboardStatsGet**
> ApiUsersDashboardStatsGet200Response apiUsersDashboardStatsGet()


### Example

```typescript
import {
    UserManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UserManagementApi(configuration);

const { status, data } = await apiInstance.apiUsersDashboardStatsGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**ApiUsersDashboardStatsGet200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Dashboard stats retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiUsersDeleteAccountPost**
> ApiAuthForgotPasswordPost200Response apiUsersDeleteAccountPost(apiUsersDeleteAccountPostRequest)


### Example

```typescript
import {
    UserManagementApi,
    Configuration,
    ApiUsersDeleteAccountPostRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new UserManagementApi(configuration);

let apiUsersDeleteAccountPostRequest: ApiUsersDeleteAccountPostRequest; //

const { status, data } = await apiInstance.apiUsersDeleteAccountPost(
    apiUsersDeleteAccountPostRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **apiUsersDeleteAccountPostRequest** | **ApiUsersDeleteAccountPostRequest**|  | |


### Return type

**ApiAuthForgotPasswordPost200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Account deleted successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiUsersNotificationsPreferencesGet**
> ApiUsersNotificationsPreferencesGet200Response apiUsersNotificationsPreferencesGet()


### Example

```typescript
import {
    UserManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UserManagementApi(configuration);

const { status, data } = await apiInstance.apiUsersNotificationsPreferencesGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**ApiUsersNotificationsPreferencesGet200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Notification preferences retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiUsersNotificationsPreferencesPut**
> ApiAuthForgotPasswordPost200Response apiUsersNotificationsPreferencesPut(apiUsersNotificationsPreferencesGet200Response)


### Example

```typescript
import {
    UserManagementApi,
    Configuration,
    ApiUsersNotificationsPreferencesGet200Response
} from './api';

const configuration = new Configuration();
const apiInstance = new UserManagementApi(configuration);

let apiUsersNotificationsPreferencesGet200Response: ApiUsersNotificationsPreferencesGet200Response; //

const { status, data } = await apiInstance.apiUsersNotificationsPreferencesPut(
    apiUsersNotificationsPreferencesGet200Response
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **apiUsersNotificationsPreferencesGet200Response** | **ApiUsersNotificationsPreferencesGet200Response**|  | |


### Return type

**ApiAuthForgotPasswordPost200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Preferences updated successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiUsersPasswordPut**
> ApiAuthForgotPasswordPost200Response apiUsersPasswordPut(apiUsersPasswordPutRequest)


### Example

```typescript
import {
    UserManagementApi,
    Configuration,
    ApiUsersPasswordPutRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new UserManagementApi(configuration);

let apiUsersPasswordPutRequest: ApiUsersPasswordPutRequest; //

const { status, data } = await apiInstance.apiUsersPasswordPut(
    apiUsersPasswordPutRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **apiUsersPasswordPutRequest** | **ApiUsersPasswordPutRequest**|  | |


### Return type

**ApiAuthForgotPasswordPost200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Password changed successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiUsersProfileGet**
> User apiUsersProfileGet()


### Example

```typescript
import {
    UserManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UserManagementApi(configuration);

const { status, data } = await apiInstance.apiUsersProfileGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**User**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | User profile retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiUsersProfilePut**
> User apiUsersProfilePut(apiUsersProfilePutRequest)


### Example

```typescript
import {
    UserManagementApi,
    Configuration,
    ApiUsersProfilePutRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new UserManagementApi(configuration);

let apiUsersProfilePutRequest: ApiUsersProfilePutRequest; //

const { status, data } = await apiInstance.apiUsersProfilePut(
    apiUsersProfilePutRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **apiUsersProfilePutRequest** | **ApiUsersProfilePutRequest**|  | |


### Return type

**User**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Profile updated successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiUsersSubscriptionGet**
> Subscription apiUsersSubscriptionGet()


### Example

```typescript
import {
    UserManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UserManagementApi(configuration);

const { status, data } = await apiInstance.apiUsersSubscriptionGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**Subscription**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Subscription details retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

