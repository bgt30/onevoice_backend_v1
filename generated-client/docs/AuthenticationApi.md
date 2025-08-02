# AuthenticationApi

All URIs are relative to *https://api.onevoice.com*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**apiAuthForgotPasswordPost**](#apiauthforgotpasswordpost) | **POST** /api/auth/forgot-password | Request password reset|
|[**apiAuthLoginPost**](#apiauthloginpost) | **POST** /api/auth/login | User login|
|[**apiAuthLogoutPost**](#apiauthlogoutpost) | **POST** /api/auth/logout | User logout|
|[**apiAuthResetPasswordPost**](#apiauthresetpasswordpost) | **POST** /api/auth/reset-password | Reset password with token|
|[**apiAuthSignupPost**](#apiauthsignuppost) | **POST** /api/auth/signup | User registration|

# **apiAuthForgotPasswordPost**
> ApiAuthForgotPasswordPost200Response apiAuthForgotPasswordPost(apiAuthForgotPasswordPostRequest)


### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    ApiAuthForgotPasswordPostRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let apiAuthForgotPasswordPostRequest: ApiAuthForgotPasswordPostRequest; //

const { status, data } = await apiInstance.apiAuthForgotPasswordPost(
    apiAuthForgotPasswordPostRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **apiAuthForgotPasswordPostRequest** | **ApiAuthForgotPasswordPostRequest**|  | |


### Return type

**ApiAuthForgotPasswordPost200Response**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Password reset email sent |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiAuthLoginPost**
> AuthResponse apiAuthLoginPost(loginRequest)


### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    LoginRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let loginRequest: LoginRequest; //

const { status, data } = await apiInstance.apiAuthLoginPost(
    loginRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **loginRequest** | **LoginRequest**|  | |


### Return type

**AuthResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful login |  -  |
|**401** | Invalid credentials |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiAuthLogoutPost**
> ApiAuthForgotPasswordPost200Response apiAuthLogoutPost()


### Example

```typescript
import {
    AuthenticationApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

const { status, data } = await apiInstance.apiAuthLogoutPost();
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
|**200** | Logout successful |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiAuthResetPasswordPost**
> ApiAuthForgotPasswordPost200Response apiAuthResetPasswordPost(apiAuthResetPasswordPostRequest)


### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    ApiAuthResetPasswordPostRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let apiAuthResetPasswordPostRequest: ApiAuthResetPasswordPostRequest; //

const { status, data } = await apiInstance.apiAuthResetPasswordPost(
    apiAuthResetPasswordPostRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **apiAuthResetPasswordPostRequest** | **ApiAuthResetPasswordPostRequest**|  | |


### Return type

**ApiAuthForgotPasswordPost200Response**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Password reset successful |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **apiAuthSignupPost**
> AuthResponse apiAuthSignupPost(signupRequest)


### Example

```typescript
import {
    AuthenticationApi,
    Configuration,
    SignupRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthenticationApi(configuration);

let signupRequest: SignupRequest; //

const { status, data } = await apiInstance.apiAuthSignupPost(
    signupRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **signupRequest** | **SignupRequest**|  | |


### Return type

**AuthResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | User created successfully |  -  |
|**400** | Invalid input data |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

