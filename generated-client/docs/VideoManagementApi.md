# VideoManagementApi

All URIs are relative to *https://api.onevoice.com*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**apiVideosGet**](#apivideosget) | **GET** /api/videos | Get user videos|
|[**apiVideosIdCancelPost**](#apivideosidcancelpost) | **POST** /api/videos/{id}/cancel | Cancel video processing|
|[**apiVideosIdDelete**](#apivideosiddelete) | **DELETE** /api/videos/{id} | Delete video|
|[**apiVideosIdDownloadGet**](#apivideosiddownloadget) | **GET** /api/videos/{id}/download | Download processed video|
|[**apiVideosIdDubPost**](#apivideosiddubpost) | **POST** /api/videos/{id}/dub | Start video dubbing process|
|[**apiVideosIdDuplicatePost**](#apivideosidduplicatepost) | **POST** /api/videos/{id}/duplicate | Duplicate video|
|[**apiVideosIdGet**](#apivideosidget) | **GET** /api/videos/{id} | Get video by ID|
|[**apiVideosIdPut**](#apivideosidput) | **PUT** /api/videos/{id} | Update video|

|[**apiVideosIdStatusGet**](#apivideosidstatusget) | **GET** /api/videos/{id}/status | Get video processing status|
|[**apiVideosIdThumbnailPost**](#apivideosidthumbnailpost) | **POST** /api/videos/{id}/thumbnail | Generate or update video thumbnail|
|[**apiVideosLanguagesGet**](#apivideoslanguagesget) | **GET** /api/videos/languages | Get supported languages|
|[**apiVideosPost**](#apivideospost) | **POST** /api/videos | Create new video|


|[**apiVideosUploadUrlPost**](#apivideosuploadurlpost) | **POST** /api/videos/upload-url | Get pre-signed upload URL|
|[**apiVideosVoicesGet**](#apivideosvoicesget) | **GET** /api/videos/voices | Get available voices for language|

# **apiVideosGet**
> ApiVideosGet200Response apiVideosGet()


### Example

```typescript
import {
    VideoManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VideoManagementApi(configuration);

let page: number; // (optional) (default to 1)
let perPage: number; // (optional) (default to 20)
let status: 'uploaded' | 'processing' | 'completed' | 'failed'; // (optional) (default to undefined)

const { status, data } = await apiInstance.apiVideosGet(
    page,
    perPage,
    status
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **page** | [**number**] |  | (optional) defaults to 1|
| **perPage** | [**number**] |  | (optional) defaults to 20|
| **status** | [**&#39;uploaded&#39; | &#39;processing&#39; | &#39;completed&#39; | &#39;failed&#39;**]**Array<&#39;uploaded&#39; &#124; &#39;processing&#39; &#124; &#39;completed&#39; &#124; &#39;failed&#39;>** |  | (optional) defaults to undefined|


### Return type

**ApiVideosGet200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Videos retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiVideosIdCancelPost**
> ApiAuthForgotPasswordPost200Response apiVideosIdCancelPost()


### Example

```typescript
import {
    VideoManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VideoManagementApi(configuration);

let id: string; // (default to undefined)

const { status, data } = await apiInstance.apiVideosIdCancelPost(
    id
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **id** | [**string**] |  | defaults to undefined|


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
|**200** | Processing cancelled |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiVideosIdDelete**
> ApiAuthForgotPasswordPost200Response apiVideosIdDelete()


### Example

```typescript
import {
    VideoManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VideoManagementApi(configuration);

let id: string; // (default to undefined)

const { status, data } = await apiInstance.apiVideosIdDelete(
    id
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **id** | [**string**] |  | defaults to undefined|


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
|**200** | Video deleted successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiVideosIdDownloadGet**
> ApiVideosIdDownloadGet200Response apiVideosIdDownloadGet()


### Example

```typescript
import {
    VideoManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VideoManagementApi(configuration);

let id: string; // (default to undefined)
let language: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.apiVideosIdDownloadGet(
    id,
    language
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **id** | [**string**] |  | defaults to undefined|
| **language** | [**string**] |  | (optional) defaults to undefined|


### Return type

**ApiVideosIdDownloadGet200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Download URL generated |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiVideosIdDubPost**
> ApiVideosIdDubPost202Response apiVideosIdDubPost(dubRequest)


### Example

```typescript
import {
    VideoManagementApi,
    Configuration,
    DubRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VideoManagementApi(configuration);

let id: string; // (default to undefined)
let dubRequest: DubRequest; //

const { status, data } = await apiInstance.apiVideosIdDubPost(
    id,
    dubRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **dubRequest** | **DubRequest**|  | |
| **id** | [**string**] |  | defaults to undefined|


### Return type

**ApiVideosIdDubPost202Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**202** | Dubbing process started |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiVideosIdDuplicatePost**
> Video apiVideosIdDuplicatePost()


### Example

```typescript
import {
    VideoManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VideoManagementApi(configuration);

let id: string; // (default to undefined)

const { status, data } = await apiInstance.apiVideosIdDuplicatePost(
    id
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **id** | [**string**] |  | defaults to undefined|


### Return type

**Video**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Video duplicated successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiVideosIdGet**
> Video apiVideosIdGet()


### Example

```typescript
import {
    VideoManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VideoManagementApi(configuration);

let id: string; // (default to undefined)

const { status, data } = await apiInstance.apiVideosIdGet(
    id
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **id** | [**string**] |  | defaults to undefined|


### Return type

**Video**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Video retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiVideosIdPut**
> Video apiVideosIdPut(apiVideosIdPutRequest)


### Example

```typescript
import {
    VideoManagementApi,
    Configuration,
    ApiVideosIdPutRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VideoManagementApi(configuration);

let id: string; // (default to undefined)
let apiVideosIdPutRequest: ApiVideosIdPutRequest; //

const { status, data } = await apiInstance.apiVideosIdPut(
    id,
    apiVideosIdPutRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **apiVideosIdPutRequest** | **ApiVideosIdPutRequest**|  | |
| **id** | [**string**] |  | defaults to undefined|


### Return type

**Video**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Video updated successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)



# **apiVideosIdStatusGet**
> JobStatus apiVideosIdStatusGet()


### Example

```typescript
import {
    VideoManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VideoManagementApi(configuration);

let id: string; // (default to undefined)

const { status, data } = await apiInstance.apiVideosIdStatusGet(
    id
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **id** | [**string**] |  | defaults to undefined|


### Return type

**JobStatus**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Processing status retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiVideosIdThumbnailPost**
> ApiVideosIdThumbnailPost200Response apiVideosIdThumbnailPost()


### Example

```typescript
import {
    VideoManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VideoManagementApi(configuration);

let id: string; // (default to undefined)
let thumbnail: File; // (optional) (default to undefined)
let timestamp: number; //Time in seconds to extract thumbnail from video (optional) (default to undefined)

const { status, data } = await apiInstance.apiVideosIdThumbnailPost(
    id,
    thumbnail,
    timestamp
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **id** | [**string**] |  | defaults to undefined|
| **thumbnail** | [**File**] |  | (optional) defaults to undefined|
| **timestamp** | [**number**] | Time in seconds to extract thumbnail from video | (optional) defaults to undefined|


### Return type

**ApiVideosIdThumbnailPost200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Thumbnail generated successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiVideosLanguagesGet**
> Array<Language> apiVideosLanguagesGet()


### Example

```typescript
import {
    VideoManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VideoManagementApi(configuration);

const { status, data } = await apiInstance.apiVideosLanguagesGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**Array<Language>**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Supported languages retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiVideosPost**
> Video apiVideosPost(apiVideosPostRequest)


### Example

```typescript
import {
    VideoManagementApi,
    Configuration,
    ApiVideosPostRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VideoManagementApi(configuration);

let apiVideosPostRequest: ApiVideosPostRequest; //

const { status, data } = await apiInstance.apiVideosPost(
    apiVideosPostRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **apiVideosPostRequest** | **ApiVideosPostRequest**|  | |


### Return type

**Video**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Video created successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)




# **apiVideosUploadUrlPost**
> ApiVideosUploadUrlPost200Response apiVideosUploadUrlPost(apiVideosUploadUrlPostRequest)


### Example

```typescript
import {
    VideoManagementApi,
    Configuration,
    ApiVideosUploadUrlPostRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new VideoManagementApi(configuration);

let apiVideosUploadUrlPostRequest: ApiVideosUploadUrlPostRequest; //

const { status, data } = await apiInstance.apiVideosUploadUrlPost(
    apiVideosUploadUrlPostRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **apiVideosUploadUrlPostRequest** | **ApiVideosUploadUrlPostRequest**|  | |


### Return type

**ApiVideosUploadUrlPost200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Upload URL generated |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiVideosVoicesGet**
> Array<Voice> apiVideosVoicesGet()


### Example

```typescript
import {
    VideoManagementApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new VideoManagementApi(configuration);

let language: string; // (default to undefined)

const { status, data } = await apiInstance.apiVideosVoicesGet(
    language
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **language** | [**string**] |  | defaults to undefined|


### Return type

**Array<Voice>**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Available voices retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

