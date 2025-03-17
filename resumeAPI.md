# API 接口文档

--- 

## 1. 用户认证相关
### 1.1 用户注册

**URL:** /api/register

**方法:** POST

**请求参数 (JSON):**


```python
    {
        "username": "string",  
        "password": "string",  
        "email": "string (optional)",  
        "role": "string (optional)"  
    }
```
    

+ username: 用户名，必须唯一
+ password: 密码
+ email: 用户邮箱 (可选)
+ role: 用户角色，默认为 job_seeker (可选)

**响应：**
+ 成功：

```python
    {
        "message": "注册成功"
    }
```
    

+ 失败：

```python
    {
        "error": "用户名已存在"
    }
```


### 1.2 用户登录

**URL:** /api/login

**方法:** POST

**请求参数 (JSON):**

```python
    {
        "username": "string",  
        "password": "string"
    }
```

+ username: 用户名
+ password: 密码

**响应:**

+ 成功:

```python
    {
        "access_token": "jwt_token"
    }
```


+ 失败:

```python
    {
        "error": "无效的用户名或密码"
    }
```


## 2. 简历管理相关
### 2.1 上传简历

**URL:** /api/resumes/upload

**方法:** POST

**请求参数 (Form Data):**

+ file: 简历文件 (必填)

**认证:** JWT (jwt_required())

**响应:**

+ 成功:

```python
    {
        "resume_id": "int",
        "status": "上传成功"
    }
```

+ 失败:

```python
    {
        "error": "未上传文件"
    }
```


### 2.2 获取当前用户简历列表
**URL:** /api/resumes

**方法:** GET

**认证:** JWT (jwt_required())

**响应:**

```python
    [
      {
        "id": "int",
        "upload_time": "string (ISO 8601)",
        "status": "string"
      }
    ]
```

### 2.3 获取简历详情

**URL:** /api/resumes/<int:resume_id>

**方法:** GET

**认证:** JWT (jwt_required())

**参数:**

+ resume_id: 简历 ID

**响应:**

+ 成功:

```python
    {
      "id": "int",
      "file_path": "string",
      "status": "string",
      "upload_time": "string (ISO 8601)"
    }
```

+ 失败:

```python
    {
      "error": "无权访问"
    }
```

## 3. 数据分析相关

### 3.1 获取简历分析结果

**URL:** /api/resumes/<int:resume_id>/analysis

**方法:** GET

**认证:** JWT (jwt_required())

**参数:**

+ resume_id: 简历 ID

**响应:**

+ 成功:

```python
    {
      "basic_info": {
        "name": "string",
        "age": "int",
        "contact": {
          "email": "string",
          "phone": "string"
        }
      },
      "career_interest": "string"
    }
```


+ 失败:

```python
    {
      "error": "分析结果不存在"
    }
```

## 3.2 获取职位匹配结果

**URL:** /api/resumes/<int:resume_id>/matches

**方法:** GET

**认证:** JWT (jwt_required())

**参数:**

+ resume_id: 简历 ID

**响应:**

```python
    [
      {
        "position": "string",
        "salary_range": "string",
        "match_score": "string",
        "analysis": "string"
      }
    ]
```

## 4. 管理员路由

### 4.1 获取所有用户（仅管理员）

**URL:** /api/admin/users

**方法:** GET

**认证:** JWT (jwt_required())

**响应:**

+ 成功:

```python
    [
      {
        "id": "int",
        "username": "string",
        "role": "string"
      }
    ]

```

+ 失败:

```python
    {
      "error": "权限不足"
    }
```

## 4.2 获取所有简历（仅管理员）

**URL:** /api/admin/resumes

**方法:** GET

**认证:** JWT (jwt_required())

**响应:**

+ 成功: 

```python
    [
      {
        "id": "int",
        "user_id": "int",
        "status": "string"
      }
    ]
```

+ 失败:

```python
    {
      "error": "权限不足"
    }
```

## 5. 错误处理

### 5.1 资源不存在 (404)

**响应:**

```python
    {
      "error": "资源不存在"
    }
```

### 5.2 服务器内部错误 (500)

**响应:**

```python
    {
      "error": "服务器内部错误"
    }
```
