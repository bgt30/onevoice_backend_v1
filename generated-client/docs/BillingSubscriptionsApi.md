# BillingSubscriptionsApi

All URIs are relative to *https://api.onevoice.com*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**apiBillingHistoryGet**](#apibillinghistoryget) | **GET** /api/billing/history | Get billing history|
|[**apiBillingPaymentMethodPut**](#apibillingpaymentmethodput) | **PUT** /api/billing/payment-method | Update default payment method|
|[**apiBillingPaymentMethodsGet**](#apibillingpaymentmethodsget) | **GET** /api/billing/payment-methods | Get all payment methods|
|[**apiBillingPaymentMethodsIdDelete**](#apibillingpaymentmethodsiddelete) | **DELETE** /api/billing/payment-methods/{id} | Delete payment method|
|[**apiBillingPlansGet**](#apibillingplansget) | **GET** /api/billing/plans | Get available billing plans|
|[**apiBillingSetupIntentPost**](#apibillingsetupintentpost) | **POST** /api/billing/setup-intent | Create setup intent for payment method|
|[**apiBillingSubscribePost**](#apibillingsubscribepost) | **POST** /api/billing/subscribe | Create new subscription|
|[**apiBillingSubscriptionCancelPost**](#apibillingsubscriptioncancelpost) | **POST** /api/billing/subscription/cancel | Cancel subscription|
|[**apiBillingSubscriptionGet**](#apibillingsubscriptionget) | **GET** /api/billing/subscription | Get current subscription|
|[**apiBillingSubscriptionPut**](#apibillingsubscriptionput) | **PUT** /api/billing/subscription | Update subscription|
|[**apiBillingSubscriptionResumePost**](#apibillingsubscriptionresumepost) | **POST** /api/billing/subscription/resume | Resume cancelled subscription|
|[**apiBillingUpcomingInvoiceGet**](#apibillingupcominginvoiceget) | **GET** /api/billing/upcoming-invoice | Get upcoming invoice|
|[**apiBillingUsageGet**](#apibillingusageget) | **GET** /api/billing/usage | Get billing usage details|

# **apiBillingHistoryGet**
> ApiBillingHistoryGet200Response apiBillingHistoryGet()


### Example

```typescript
import {
    BillingSubscriptionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new BillingSubscriptionsApi(configuration);

let page: number; // (optional) (default to 1)
let perPage: number; // (optional) (default to 20)

const { status, data } = await apiInstance.apiBillingHistoryGet(
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

**ApiBillingHistoryGet200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Billing history retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiBillingPaymentMethodPut**
> ApiAuthForgotPasswordPost200Response apiBillingPaymentMethodPut(apiBillingPaymentMethodPutRequest)


### Example

```typescript
import {
    BillingSubscriptionsApi,
    Configuration,
    ApiBillingPaymentMethodPutRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new BillingSubscriptionsApi(configuration);

let apiBillingPaymentMethodPutRequest: ApiBillingPaymentMethodPutRequest; //

const { status, data } = await apiInstance.apiBillingPaymentMethodPut(
    apiBillingPaymentMethodPutRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **apiBillingPaymentMethodPutRequest** | **ApiBillingPaymentMethodPutRequest**|  | |


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
|**200** | Payment method updated successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiBillingPaymentMethodsGet**
> Array<ApiBillingPaymentMethodsGet200ResponseInner> apiBillingPaymentMethodsGet()


### Example

```typescript
import {
    BillingSubscriptionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new BillingSubscriptionsApi(configuration);

const { status, data } = await apiInstance.apiBillingPaymentMethodsGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**Array<ApiBillingPaymentMethodsGet200ResponseInner>**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Payment methods retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiBillingPaymentMethodsIdDelete**
> ApiAuthForgotPasswordPost200Response apiBillingPaymentMethodsIdDelete()


### Example

```typescript
import {
    BillingSubscriptionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new BillingSubscriptionsApi(configuration);

let id: string; // (default to undefined)

const { status, data } = await apiInstance.apiBillingPaymentMethodsIdDelete(
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
|**200** | Payment method deleted successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiBillingPlansGet**
> Array<BillingPlan> apiBillingPlansGet()


### Example

```typescript
import {
    BillingSubscriptionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new BillingSubscriptionsApi(configuration);

const { status, data } = await apiInstance.apiBillingPlansGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**Array<BillingPlan>**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Billing plans retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiBillingSetupIntentPost**
> ApiBillingSetupIntentPost200Response apiBillingSetupIntentPost()


### Example

```typescript
import {
    BillingSubscriptionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new BillingSubscriptionsApi(configuration);

const { status, data } = await apiInstance.apiBillingSetupIntentPost();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**ApiBillingSetupIntentPost200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Setup intent created |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiBillingSubscribePost**
> Subscription apiBillingSubscribePost(apiBillingSubscribePostRequest)


### Example

```typescript
import {
    BillingSubscriptionsApi,
    Configuration,
    ApiBillingSubscribePostRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new BillingSubscriptionsApi(configuration);

let apiBillingSubscribePostRequest: ApiBillingSubscribePostRequest; //

const { status, data } = await apiInstance.apiBillingSubscribePost(
    apiBillingSubscribePostRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **apiBillingSubscribePostRequest** | **ApiBillingSubscribePostRequest**|  | |


### Return type

**Subscription**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Subscription created successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiBillingSubscriptionCancelPost**
> ApiAuthForgotPasswordPost200Response apiBillingSubscriptionCancelPost()


### Example

```typescript
import {
    BillingSubscriptionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new BillingSubscriptionsApi(configuration);

const { status, data } = await apiInstance.apiBillingSubscriptionCancelPost();
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
|**200** | Subscription cancelled successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiBillingSubscriptionGet**
> Subscription apiBillingSubscriptionGet()


### Example

```typescript
import {
    BillingSubscriptionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new BillingSubscriptionsApi(configuration);

const { status, data } = await apiInstance.apiBillingSubscriptionGet();
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
|**200** | Current subscription retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiBillingSubscriptionPut**
> Subscription apiBillingSubscriptionPut(apiBillingSubscriptionPutRequest)


### Example

```typescript
import {
    BillingSubscriptionsApi,
    Configuration,
    ApiBillingSubscriptionPutRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new BillingSubscriptionsApi(configuration);

let apiBillingSubscriptionPutRequest: ApiBillingSubscriptionPutRequest; //

const { status, data } = await apiInstance.apiBillingSubscriptionPut(
    apiBillingSubscriptionPutRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **apiBillingSubscriptionPutRequest** | **ApiBillingSubscriptionPutRequest**|  | |


### Return type

**Subscription**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Subscription updated successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiBillingSubscriptionResumePost**
> Subscription apiBillingSubscriptionResumePost()


### Example

```typescript
import {
    BillingSubscriptionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new BillingSubscriptionsApi(configuration);

const { status, data } = await apiInstance.apiBillingSubscriptionResumePost();
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
|**200** | Subscription resumed successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiBillingUpcomingInvoiceGet**
> ApiBillingUpcomingInvoiceGet200Response apiBillingUpcomingInvoiceGet()


### Example

```typescript
import {
    BillingSubscriptionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new BillingSubscriptionsApi(configuration);

const { status, data } = await apiInstance.apiBillingUpcomingInvoiceGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**ApiBillingUpcomingInvoiceGet200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Upcoming invoice retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiBillingUsageGet**
> ApiBillingUsageGet200Response apiBillingUsageGet()


### Example

```typescript
import {
    BillingSubscriptionsApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new BillingSubscriptionsApi(configuration);

const { status, data } = await apiInstance.apiBillingUsageGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**ApiBillingUsageGet200Response**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Usage details retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

