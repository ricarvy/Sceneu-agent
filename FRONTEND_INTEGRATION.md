# 社交媒体营销图片生成智能体 - 前端接入文档

## 目录
- [概述](#概述)
- [系统架构](#系统架构)
- [后端部署](#后端部署)
- [API 接口说明](#api-接口说明)
- [前端接入步骤](#前端接入步骤)
- [代码示例](#代码示例)
- [参数说明](#参数说明)
- [错误处理](#错误处理)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 概述

本智能体是一个基于 LangChain 和 AI 图像生成技术的社交媒体营销图片生成系统，能够将用户照片与商品照片合成为高质量、多样化的营销图片。

### 核心功能
- ✅ **多商品支持**：支持单个或多个商品组合（如上衣+裙子+挎包）
- ✅ **场景定制**：支持用户上传场景图，所有图片都符合用户指定场景
- ✅ **9:16 比例**：生成适合社交媒体分享的竖版图片
- ✅ **人脸高度一致**：4张图片的人脸保持高度一致，细节刻画精细
- ✅ **背景自然融合**：人物与背景自然融合，无剥离感
- ✅ **智能组合**：自动识别商品类型，匹配合适的组合方式和场景

### 适用场景
- 电商营销图生成
- 社交媒体内容创作
- 穿搭种草图片生成
- 产品体验图制作

---

## 系统架构

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   前端应用   │────────>│   后端 API   │────────>│   AI 智能体  │
│  (Vue/React)│  HTTP   │  (FastAPI)  │  调用   │  (LangChain) │
└─────────────┘         └─────────────┘         └─────────────┘
                                │                         │
                                v                         v
                         ┌─────────────┐         ┌─────────────┐
                         │  对象存储   │         │  生图服务   │
                         │  (OSS/S3)  │         │ (Image SDK) │
                         └─────────────┘         └─────────────┘
```

---

## 后端部署

### 1. 环境准备

#### 系统要求
- Python 3.8+
- 4GB+ RAM
- 稳定的网络连接

#### 安装依赖

```bash
cd /workspace/projects
pip install -r requirements.txt
```

主要依赖包：
- `langchain` - Agent 框架
- `langgraph` - 图编排框架
- `langchain-openai` - OpenAI 兼容接口
- `coze-coding-dev-sdk` - Coze 开发工具包
- `fastapi` - 后端 API 框架
- `uvicorn` - ASGI 服务器

### 2. 配置环境变量

创建 `.env` 文件（如果需要）：

```bash
# Coze API 配置
COZE_INTEGRATION_MODEL_BASE_URL=https://integration.coze.cn/api/v3
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key_here

# 工作空间路径
COZE_WORKSPACE_PATH=/workspace/projects
```

### 3. 启动后端服务

#### 方式一：使用内置的 API 示例

```bash
cd /workspace/projects
python api_example.py
```

服务将在 `http://localhost:8000` 启动。

#### 方式二：使用 Uvicorn

```bash
cd /workspace/projects
uvicorn api_example:app --host 0.0.0.0 --port 8000 --reload
```

#### 方式三：生产环境部署

```bash
# 使用 Gunicorn + Uvicorn
pip install gunicorn
gunicorn api_example:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 4. 验证服务

访问健康检查接口：
```bash
curl http://localhost:8000/health
```

预期返回：
```json
{
  "status": "ok",
  "service": "marketing-image-generator"
}
```

---

## API 接口说明

### 生成营销图片

#### 接口地址
```
POST /generate
```

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_photo | File | 是 | 用户照片文件 |
| product_photo | File | 是 | 商品照片文件（支持多个） |
| scene_photo | File | 否 | 场景照片文件（可选） |
| prompt | String | 是 | 风格与场景描述 |

#### 请求示例

```bash
curl -X POST "http://localhost:8000/generate" \
  -F "user_photo=@user.jpg" \
  -F "product_photo=@shirt.jpg" \
  -F "product_photo=@skirt.jpg" \
  -F "prompt=高级感，自然光线，温馨咖啡馆"
```

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| success | Boolean | 是否成功 |
| message | String | 消息内容 |
| image_urls | Array | 生成的图片URL列表（4张） |
| explanation | String | 详细说明（可选） |
| error | String | 错误信息（失败时） |

#### 成功响应示例

```json
{
  "success": true,
  "message": "成功生成 4 张营销图片",
  "image_urls": [
    "https://oss.example.com/images/img1_1080x1920.jpg",
    "https://oss.example.com/images/img2_1080x1920.jpg",
    "https://oss.example.com/images/img3_1080x1920.jpg",
    "https://oss.example.com/images/img4_1080x1920.jpg"
  ],
  "explanation": "生成的4张图片展示了用户在不同角度使用商品的体验，人脸高度一致，背景自然融合。"
}
```

#### 失败响应示例

```json
{
  "success": false,
  "error": "图片生成失败：InvalidParameter"
}
```

---

## 前端接入步骤

### 步骤 1：确定前端技术栈

支持的前端框架：
- Vue 2/3
- React
- Angular
- 原生 JavaScript

### 步骤 2：选择接入方式

#### 方式一：使用现有的 HTML 页面（快速测试）

直接使用项目提供的 Web UI 页面：
- `test_ui_connected_v4.html` - 支持多商品和场景图

```html
<!DOCTYPE html>
<html>
<head>
  <title>营销图片生成器</title>
  <script src="app.js"></script>
</head>
<body>
  <!-- 页面内容 -->
</body>
</html>
```

#### 方式二：集成到现有前端项目

将 API 接口集成到现有的前端项目中。

---

## 代码示例

### 示例 1：Vue 3 接入

#### 组件代码

```vue
<template>
  <div class="image-generator">
    <!-- API 配置 -->
    <div class="config-section">
      <label>API 地址：</label>
      <input v-model="apiUrl" placeholder="http://localhost:8000" />
    </div>

    <!-- 用户照片上传 -->
    <div class="upload-section">
      <label>用户照片：</label>
      <input 
        type="file" 
        accept="image/*" 
        @change="handleUserPhotoUpload" 
      />
      <img v-if="userPhotoPreview" :src="userPhotoPreview" class="preview" />
    </div>

    <!-- 商品照片上传 -->
    <div class="upload-section">
      <label>商品照片（支持多个）：</label>
      <input 
        type="file" 
        accept="image/*" 
        multiple 
        @change="handleProductPhotoUpload" 
      />
      <div class="product-previews">
        <div v-for="(preview, index) in productPhotoPreviews" :key="index">
          <img :src="preview" class="preview" />
          <button @click="removeProductPhoto(index)">删除</button>
        </div>
      </div>
    </div>

    <!-- 场景照片上传 -->
    <div class="upload-section">
      <label>场景照片（可选）：</label>
      <input 
        type="file" 
        accept="image/*" 
        @change="handleScenePhotoUpload" 
      />
      <img v-if="scenePhotoPreview" :src="scenePhotoPreview" class="preview" />
    </div>

    <!-- 提示词输入 -->
    <div class="prompt-section">
      <label>风格描述：</label>
      <textarea 
        v-model="prompt" 
        placeholder="高级感，自然光线，温馨咖啡馆"
      ></textarea>
    </div>

    <!-- 生成按钮 -->
    <button 
      @click="generateImage" 
      :disabled="loading || !canGenerate"
    >
      {{ loading ? '生成中...' : '生成营销图片' }}
    </button>

    <!-- 生成结果 -->
    <div v-if="result" class="result-section">
      <h3>生成结果</h3>
      <div class="result-images">
        <div v-for="(url, index) in result.image_urls" :key="index">
          <img :src="url" class="result-image" @click="openImage(url)" />
          <p>图片 {{ index + 1 }}</p>
        </div>
      </div>
      <p v-if="result.explanation">{{ result.explanation }}</p>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// 状态管理
const apiUrl = ref('http://localhost:8000')
const loading = ref(false)
const error = ref(null)
const result = ref(null)

// 文件存储
const userPhotoFile = ref(null)
const productPhotoFiles = ref([])
const scenePhotoFile = ref(null)

// 预览图
const userPhotoPreview = ref(null)
const productPhotoPreviews = ref([])
const scenePhotoPreview = ref(null)

// 提示词
const prompt = ref('')

// 计算属性
const canGenerate = computed(() => {
  return userPhotoFile.value && 
         productPhotoFiles.value.length > 0 && 
         prompt.value.trim()
})

// 处理用户照片上传
const handleUserPhotoUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (!file.type.startsWith('image/')) {
    error.value = '请上传图片文件'
    return
  }
  
  userPhotoFile.value = file
  
  // 生成预览
  const reader = new FileReader()
  reader.onload = (e) => {
    userPhotoPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

// 处理商品照片上传
const handleProductPhotoUpload = (event) => {
  const files = Array.from(event.target.files)
  
  files.forEach(file => {
    if (!file.type.startsWith('image/')) {
      error.value = '请上传图片文件'
      return
    }
    
    if (!productPhotoFiles.value.some(f => f.name === file.name)) {
      productPhotoFiles.value.push(file)
      
      // 生成预览
      const reader = new FileReader()
      reader.onload = (e) => {
        productPhotoPreviews.value.push(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  })
}

// 删除商品照片
const removeProductPhoto = (index) => {
  productPhotoFiles.value.splice(index, 1)
  productPhotoPreviews.value.splice(index, 1)
}

// 处理场景照片上传
const handleScenePhotoUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (!file.type.startsWith('image/')) {
    error.value = '请上传图片文件'
    return
  }
  
  scenePhotoFile.value = file
  
  // 生成预览
  const reader = new FileReader()
  reader.onload = (e) => {
    scenePhotoPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

// 生成图片
const generateImage = async () => {
  error.value = null
  result.value = null
  loading.value = true
  
  try {
    // 构建 FormData
    const formData = new FormData()
    formData.append('user_photo', userPhotoFile.value)
    
    // 添加所有商品照片
    productPhotoFiles.value.forEach(file => {
      formData.append('product_photo', file)
    })
    
    // 添加场景照片（如果有）
    if (scenePhotoFile.value) {
      formData.append('scene_photo', scenePhotoFile.value)
    }
    
    // 添加提示词
    formData.append('prompt', prompt.value)
    
    // 发送请求
    const response = await fetch(`${apiUrl.value}/generate`, {
      method: 'POST',
      body: formData
    })
    
    const data = await response.json()
    
    if (!response.ok || !data.success) {
      throw new Error(data.error || data.message || '生成失败')
    }
    
    result.value = data
    
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// 打开图片
const openImage = (url) => {
  window.open(url, '_blank')
}
</script>

<style scoped>
.image-generator {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.config-section,
.upload-section,
.prompt-section {
  margin-bottom: 20px;
}

.upload-section label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

.config-section input,
.prompt-section textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.preview {
  max-width: 200px;
  max-height: 200px;
  border-radius: 6px;
  margin-top: 10px;
}

.product-previews {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.product-previews img {
  max-width: 100px;
  max-height: 100px;
  border-radius: 6px;
}

button {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1em;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.result-section {
  margin-top: 30px;
}

.result-images {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin: 15px 0;
}

.result-image {
  width: 100%;
  border-radius: 8px;
  cursor: pointer;
  aspect-ratio: 9/16;
  object-fit: cover;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 15px;
  border-radius: 6px;
  margin-top: 20px;
}
</style>
```

---

### 示例 2：React 接入

```jsx
import React, { useState, useRef } from 'react'

function ImageGenerator() {
  const [apiUrl, setApiUrl] = useState('http://localhost:8000')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [prompt, setPrompt] = useState('')
  
  const [userPhotoFile, setUserPhotoFile] = useState(null)
  const [userPhotoPreview, setUserPhotoPreview] = useState(null)
  const [productPhotoFiles, setProductPhotoFiles] = useState([])
  const [productPhotoPreviews, setProductPhotoPreviews] = useState([])
  const [scenePhotoFile, setScenePhotoFile] = useState(null)
  const [scenePhotoPreview, setScenePhotoPreview] = useState(null)
  
  const userPhotoInputRef = useRef(null)
  const productPhotoInputRef = useRef(null)
  const scenePhotoInputRef = useRef(null)

  const canGenerate = userPhotoFile && productPhotoFiles.length > 0 && prompt.trim()

  // 处理用户照片上传
  const handleUserPhotoUpload = (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    if (!file.type.startsWith('image/')) {
      setError('请上传图片文件')
      return
    }
    
    setUserPhotoFile(file)
    
    const reader = new FileReader()
    reader.onload = (e) => {
      setUserPhotoPreview(e.target.result)
    }
    reader.readAsDataURL(file)
  }

  // 处理商品照片上传
  const handleProductPhotoUpload = (event) => {
    const files = Array.from(event.target.files)
    
    files.forEach(file => {
      if (!file.type.startsWith('image/')) {
        setError('请上传图片文件')
        return
      }
      
      if (!productPhotoFiles.some(f => f.name === file.name)) {
        setProductPhotoFiles(prev => [...prev, file])
        
        const reader = new FileReader()
        reader.onload = (e) => {
          setProductPhotoPreviews(prev => [...prev, e.target.result])
        }
        reader.readAsDataURL(file)
      }
    })
  }

  // 删除商品照片
  const removeProductPhoto = (index) => {
    setProductPhotoFiles(prev => prev.filter((_, i) => i !== index))
    setProductPhotoPreviews(prev => prev.filter((_, i) => i !== index))
  }

  // 处理场景照片上传
  const handleScenePhotoUpload = (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    if (!file.type.startsWith('image/')) {
      setError('请上传图片文件')
      return
    }
    
    setScenePhotoFile(file)
    
    const reader = new FileReader()
    reader.onload = (e) => {
      setScenePhotoPreview(e.target.result)
    }
    reader.readAsDataURL(file)
  }

  // 生成图片
  const generateImage = async () => {
    setError(null)
    setResult(null)
    setLoading(true)
    
    try {
      const formData = new FormData()
      formData.append('user_photo', userPhotoFile)
      
      productPhotoFiles.forEach(file => {
        formData.append('product_photo', file)
      })
      
      if (scenePhotoFile) {
        formData.append('scene_photo', scenePhotoFile)
      }
      
      formData.append('prompt', prompt)
      
      const response = await fetch(`${apiUrl}/generate`, {
        method: 'POST',
        body: formData
      })
      
      const data = await response.json()
      
      if (!response.ok || !data.success) {
        throw new Error(data.error || data.message || '生成失败')
      }
      
      setResult(data)
      
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="image-generator">
      {/* API 配置 */}
      <div className="config-section">
        <label>API 地址：</label>
        <input 
          value={apiUrl}
          onChange={(e) => setApiUrl(e.target.value)}
          placeholder="http://localhost:8000"
        />
      </div>

      {/* 用户照片上传 */}
      <div className="upload-section">
        <label>用户照片：</label>
        <input 
          type="file" 
          accept="image/*" 
          ref={userPhotoInputRef}
          onChange={handleUserPhotoUpload}
        />
        {userPhotoPreview && (
          <img src={userPhotoPreview} className="preview" alt="用户照片" />
        )}
      </div>

      {/* 商品照片上传 */}
      <div className="upload-section">
        <label>商品照片（支持多个）：</label>
        <input 
          type="file" 
          accept="image/*"
          multiple
          ref={productPhotoInputRef}
          onChange={handleProductPhotoUpload}
        />
        <div className="product-previews">
          {productPhotoPreviews.map((preview, index) => (
            <div key={index}>
              <img src={preview} className="preview" alt={`商品${index + 1}`} />
              <button onClick={() => removeProductPhoto(index)}>删除</button>
            </div>
          ))}
        </div>
      </div>

      {/* 场景照片上传 */}
      <div className="upload-section">
        <label>场景照片（可选）：</label>
        <input 
          type="file" 
          accept="image/*"
          ref={scenePhotoInputRef}
          onChange={handleScenePhotoUpload}
        />
        {scenePhotoPreview && (
          <img src={scenePhotoPreview} className="preview" alt="场景照片" />
        )}
      </div>

      {/* 提示词输入 */}
      <div className="prompt-section">
        <label>风格描述：</label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="高级感，自然光线，温馨咖啡馆"
        />
      </div>

      {/* 生成按钮 */}
      <button 
        onClick={generateImage} 
        disabled={loading || !canGenerate}
      >
        {loading ? '生成中...' : '生成营销图片'}
      </button>

      {/* 生成结果 */}
      {result && (
        <div className="result-section">
          <h3>生成结果</h3>
          <div className="result-images">
            {result.image_urls.map((url, index) => (
              <div key={index}>
                <img 
                  src={url} 
                  className="result-image" 
                  alt={`图片${index + 1}`}
                  onClick={() => window.open(url, '_blank')}
                />
                <p>图片 {index + 1}</p>
              </div>
            ))}
          </div>
          {result.explanation && <p>{result.explanation}</p>}
        </div>
      )}

      {/* 错误提示 */}
      {error && <div className="error-message">{error}</div>}
    </div>
  )
}

export default ImageGenerator
```

---

### 示例 3：原生 JavaScript 接入

```html
<!DOCTYPE html>
<html>
<head>
  <title>营销图片生成器</title>
  <style>
    /* 样式代码 */
    .image-generator { max-width: 1200px; margin: 0 auto; padding: 20px; }
    .upload-section { margin-bottom: 20px; }
    .upload-section label { display: block; margin-bottom: 8px; font-weight: bold; }
    .preview { max-width: 200px; border-radius: 6px; margin-top: 10px; }
    .result-images { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 15px 0; }
    .result-image { width: 100%; border-radius: 8px; cursor: pointer; aspect-ratio: 9/16; object-fit: cover; }
    button { width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; cursor: pointer; }
    button:disabled { background: #ccc; cursor: not-allowed; }
    .error-message { background: #fee; color: #c33; padding: 15px; border-radius: 6px; margin-top: 20px; }
  </style>
</head>
<body>
  <div class="image-generator">
    <!-- API 配置 -->
    <div class="upload-section">
      <label>API 地址：</label>
      <input id="apiUrl" value="http://localhost:8000" />
    </div>

    <!-- 用户照片上传 -->
    <div class="upload-section">
      <label>用户照片：</label>
      <input type="file" id="userPhotoInput" accept="image/*" />
      <img id="userPhotoPreview" class="preview" style="display: none;" />
    </div>

    <!-- 商品照片上传 -->
    <div class="upload-section">
      <label>商品照片（支持多个）：</label>
      <input type="file" id="productPhotoInput" accept="image/*" multiple />
      <div id="productPreviews"></div>
    </div>

    <!-- 场景照片上传 -->
    <div class="upload-section">
      <label>场景照片（可选）：</label>
      <input type="file" id="scenePhotoInput" accept="image/*" />
      <img id="scenePhotoPreview" class="preview" style="display: none;" />
    </div>

    <!-- 提示词输入 -->
    <div class="upload-section">
      <label>风格描述：</label>
      <textarea id="promptInput" placeholder="高级感，自然光线，温馨咖啡馆"></textarea>
    </div>

    <!-- 生成按钮 -->
    <button id="generateBtn" disabled>生成营销图片</button>

    <!-- 生成结果 -->
    <div id="resultSection" style="display: none; margin-top: 30px;">
      <h3>生成结果</h3>
      <div id="resultImages"></div>
      <p id="resultExplanation"></p>
    </div>

    <!-- 错误提示 -->
    <div id="errorMessage" class="error-message" style="display: none;"></div>
  </div>

  <script>
    // 状态管理
    const state = {
      apiUrl: 'http://localhost:8000',
      userPhotoFile: null,
      productPhotoFiles: [],
      scenePhotoFile: null,
      prompt: ''
    }

    // DOM 元素
    const elements = {
      apiUrl: document.getElementById('apiUrl'),
      userPhotoInput: document.getElementById('userPhotoInput'),
      userPhotoPreview: document.getElementById('userPhotoPreview'),
      productPhotoInput: document.getElementById('productPhotoInput'),
      productPreviews: document.getElementById('productPreviews'),
      scenePhotoInput: document.getElementById('scenePhotoInput'),
      scenePhotoPreview: document.getElementById('scenePhotoPreview'),
      promptInput: document.getElementById('promptInput'),
      generateBtn: document.getElementById('generateBtn'),
      resultSection: document.getElementById('resultSection'),
      resultImages: document.getElementById('resultImages'),
      resultExplanation: document.getElementById('resultExplanation'),
      errorMessage: document.getElementById('errorMessage')
    }

    // 更新按钮状态
    function updateButtonState() {
      const canGenerate = state.userPhotoFile && 
                           state.productPhotoFiles.length > 0 && 
                           state.prompt.trim()
      elements.generateBtn.disabled = !canGenerate
    }

    // 处理用户照片上传
    elements.userPhotoInput.addEventListener('change', (e) => {
      const file = e.target.files[0]
      if (!file) return
      
      if (!file.type.startsWith('image/')) {
        showError('请上传图片文件')
        return
      }
      
      state.userPhotoFile = file
      
      const reader = new FileReader()
      reader.onload = (e) => {
        elements.userPhotoPreview.src = e.target.result
        elements.userPhotoPreview.style.display = 'block'
      }
      reader.readAsDataURL(file)
      
      updateButtonState()
    })

    // 处理商品照片上传
    elements.productPhotoInput.addEventListener('change', (e) => {
      const files = Array.from(e.target.files)
      
      files.forEach(file => {
        if (!file.type.startsWith('image/')) {
          showError('请上传图片文件')
          return
        }
        
        if (!state.productPhotoFiles.some(f => f.name === file.name)) {
          state.productPhotoFiles.push(file)
          
          const reader = new FileReader()
          reader.onload = (e) => {
            const div = document.createElement('div')
            div.innerHTML = `
              <img src="${e.target.result}" class="preview" style="max-width: 100px;">
              <button onclick="removeProductPhoto(${state.productPhotoFiles.length - 1})">删除</button>
            `
            elements.productPreviews.appendChild(div)
          }
          reader.readAsDataURL(file)
        }
      })
      
      updateButtonState()
    })

    // 删除商品照片
    window.removeProductPhoto = function(index) {
      state.productPhotoFiles.splice(index, 1)
      elements.productPreviews.innerHTML = ''
      updateButtonState()
    }

    // 处理场景照片上传
    elements.scenePhotoInput.addEventListener('change', (e) => {
      const file = e.target.files[0]
      if (!file) return
      
      if (!file.type.startsWith('image/')) {
        showError('请上传图片文件')
        return
      }
      
      state.scenePhotoFile = file
      
      const reader = new FileReader()
      reader.onload = (e) => {
        elements.scenePhotoPreview.src = e.target.result
        elements.scenePhotoPreview.style.display = 'block'
      }
      reader.readAsDataURL(file)
    })

    // 监听提示词输入
    elements.promptInput.addEventListener('input', (e) => {
      state.prompt = e.target.value
      updateButtonState()
    })

    // 生成图片
    elements.generateBtn.addEventListener('click', async () => {
      hideError()
      elements.resultSection.style.display = 'none'
      elements.generateBtn.disabled = true
      elements.generateBtn.textContent = '生成中...'
      
      try {
        const formData = new FormData()
        formData.append('user_photo', state.userPhotoFile)
        
        state.productPhotoFiles.forEach(file => {
          formData.append('product_photo', file)
        })
        
        if (state.scenePhotoFile) {
          formData.append('scene_photo', state.scenePhotoFile)
        }
        
        formData.append('prompt', state.prompt)
        
        const response = await fetch(`${state.apiUrl}/generate`, {
          method: 'POST',
          body: formData
        })
        
        const data = await response.json()
        
        if (!response.ok || !data.success) {
          throw new Error(data.error || data.message || '生成失败')
        }
        
        // 显示结果
        elements.resultImages.innerHTML = data.image_urls.map((url, index) => `
          <div>
            <img src="${url}" class="result-image" onclick="window.open('${url}', '_blank')">
            <p>图片 ${index + 1}</p>
          </div>
        `).join('')
        
        elements.resultExplanation.textContent = data.explanation || ''
        elements.resultSection.style.display = 'block'
        
      } catch (err) {
        showError(err.message)
      } finally {
        elements.generateBtn.disabled = false
        elements.generateBtn.textContent = '生成营销图片'
      }
    })

    // 显示错误
    function showError(message) {
      elements.errorMessage.textContent = message
      elements.errorMessage.style.display = 'block'
    }

    // 隐藏错误
    function hideError() {
      elements.errorMessage.style.display = 'none'
    }
  </script>
</body>
</html>
```

---

## 参数说明

### 必填参数

| 参数 | 类型 | 说明 | 限制 |
|------|------|------|------|
| user_photo | File | 用户照片 | 最大 10MB，支持 jpg/png |
| product_photo | File | 商品照片 | 最大 10MB，支持 jpg/png，支持多个 |
| prompt | String | 风格描述 | 建议长度：10-500 字符 |

### 可选参数

| 参数 | 类型 | 说明 | 限制 |
|------|------|------|------|
| scene_photo | File | 场景照片 | 最大 10MB，支持 jpg/png |

### prompt 参数建议

推荐的风格描述：
- `高级感，自然光线，温馨咖啡馆`
- `清新度假风，户外阳光`
- `法式复古美妆大片`
- `办公室通勤，简约专业`
- `温馨居家场景，暖色调`

---

## 错误处理

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 400 | 参数错误 | 检查文件格式、大小是否符合要求 |
| 404 | API 不存在 | 检查 API 地址是否正确 |
| 500 | 服务器错误 | 联系技术支持 |
| 503 | 服务不可用 | 等待服务恢复 |

### 错误处理示例

```javascript
try {
  const response = await fetch(`${apiUrl}/generate`, {
    method: 'POST',
    body: formData
  })
  
  const data = await response.json()
  
  if (!response.ok) {
    switch (response.status) {
      case 400:
        throw new Error('参数错误：请检查文件格式和大小')
      case 404:
        throw new Error('API 不存在：请检查 API 地址')
      case 500:
        throw new Error('服务器错误：请稍后重试')
      case 503:
        throw new Error('服务不可用：请稍后重试')
      default:
        throw new Error(data.error || '生成失败')
    }
  }
  
  if (!data.success) {
    throw new Error(data.error || '生成失败')
  }
  
  // 处理成功结果
  console.log('生成成功:', data.image_urls)
  
} catch (error) {
  console.error('生成失败:', error.message)
  // 显示错误信息给用户
}
```

---

## 最佳实践

### 1. 文件上传优化

```javascript
// 添加文件大小限制
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

function validateFile(file) {
  if (!file.type.startsWith('image/')) {
    throw new Error('请上传图片文件')
  }
  
  if (file.size > MAX_FILE_SIZE) {
    throw new Error('文件大小不能超过 10MB')
  }
  
  return true
}
```

### 2. 进度显示

```javascript
// 使用 XMLHttpRequest 显示上传进度
function uploadWithProgress(formData) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percentComplete = (e.loaded / e.total) * 100
        console.log(`上传进度：${percentComplete}%`)
      }
    })
    
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        const data = JSON.parse(xhr.responseText)
        resolve(data)
      } else {
        reject(new Error('上传失败'))
      }
    })
    
    xhr.addEventListener('error', () => {
      reject(new Error('网络错误'))
    })
    
    xhr.open('POST', `${apiUrl}/generate`)
    xhr.send(formData)
  })
}
```

### 3. 超时处理

```javascript
// 设置请求超时
async function generateWithTimeout(formData, timeout = 120000) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)
  
  try {
    const response = await fetch(`${apiUrl}/generate`, {
      method: 'POST',
      body: formData,
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)
    return await response.json()
    
  } catch (error) {
    clearTimeout(timeoutId)
    if (error.name === 'AbortError') {
      throw new Error('请求超时，请稍后重试')
    }
    throw error
  }
}
```

### 4. 图片预加载

```javascript
// 预加载生成的图片
function preloadImages(urls) {
  return Promise.all(
    urls.map(url => {
      return new Promise((resolve, reject) => {
        const img = new Image()
        img.onload = () => resolve(url)
        img.onerror = () => reject(new Error(`图片加载失败: ${url}`))
        img.src = url
      })
    })
  )
}

// 使用示例
try {
  await preloadImages(data.image_urls)
  console.log('所有图片加载完成')
} catch (error) {
  console.error('图片加载失败:', error)
}
```

### 5. 重试机制

```javascript
// 自动重试失败的请求
async function generateWithRetry(formData, maxRetries = 3, delay = 2000) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(`${apiUrl}/generate`, {
        method: 'POST',
        body: formData
      })
      
      const data = await response.json()
      
      if (response.ok && data.success) {
        return data
      }
      
      throw new Error(data.error || '生成失败')
      
    } catch (error) {
      if (i === maxRetries - 1) {
        throw error
      }
      
      console.log(`第 ${i + 1} 次尝试失败，${delay / 1000} 秒后重试...`)
      await new Promise(resolve => setTimeout(resolve, delay))
      delay *= 2 // 指数退避
    }
  }
}
```

---

## 常见问题

### Q1: 如何配置生产环境的 API 地址？

**A:** 在前端代码中配置 API 地址，建议使用环境变量：

```javascript
// 开发环境
const apiUrl = process.env.VUE_APP_API_URL || 'http://localhost:8000'

// 或者使用配置文件
import config from './config'
const apiUrl = config.production.apiUrl
```

### Q2: 如何处理跨域问题？

**A:** 在后端配置 CORS：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请替换为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q3: 生成的图片需要保存多久？

**A:** 图片URL通常有有效期（如7天），建议：
- 及时下载图片到本地服务器
- 或者保存图片的永久链接

### Q4: 如何限制并发请求数？

**A:** 使用请求队列：

```javascript
class RequestQueue {
  constructor(maxConcurrent = 3) {
    this.queue = []
    this.running = 0
    this.maxConcurrent = maxConcurrent
  }
  
  async add(request) {
    return new Promise((resolve, reject) => {
      this.queue.push({ request, resolve, reject })
      this.process()
    })
  }
  
  async process() {
    if (this.running >= this.maxConcurrent || this.queue.length === 0) {
      return
    }
    
    this.running++
    const { request, resolve, reject } = this.queue.shift()
    
    try {
      const result = await request()
      resolve(result)
    } catch (error) {
      reject(error)
    } finally {
      this.running--
      this.process()
    }
  }
}

// 使用示例
const queue = new RequestQueue(3)

async function generateImage(formData) {
  return await queue.add(() => {
    return fetch(`${apiUrl}/generate`, {
      method: 'POST',
      body: formData
    })
  })
}
```

### Q5: 如何优化大文件上传？

**A:** 使用分片上传：

```javascript
async function uploadLargeFile(file, chunkSize = 5 * 1024 * 1024) {
  const chunks = Math.ceil(file.size / chunkSize)
  const uploadId = generateUploadId()
  
  for (let i = 0; i < chunks; i++) {
    const start = i * chunkSize
    const end = Math.min(start + chunkSize, file.size)
    const chunk = file.slice(start, end)
    
    await uploadChunk(uploadId, i, chunk)
  }
  
  await completeUpload(uploadId)
}
```

### Q6: 如何监控 API 性能？

**A:** 添加性能监控：

```javascript
async function generateWithMonitoring(formData) {
  const startTime = performance.now()
  
  try {
    const response = await fetch(`${apiUrl}/generate`, {
      method: 'POST',
      body: formData
    })
    
    const endTime = performance.now()
    const duration = endTime - startTime
    
    // 发送监控数据
    trackApiPerformance({
      endpoint: '/generate',
      duration,
      status: response.ok ? 'success' : 'error'
    })
    
    return await response.json()
    
  } catch (error) {
    const endTime = performance.now()
    trackApiPerformance({
      endpoint: '/generate',
      duration: endTime - startTime,
      status: 'error',
      error: error.message
    })
    throw error
  }
}
```

---

## 联系方式

如有问题或建议，请联系技术支持。

---

**文档版本**: v1.0  
**最后更新**: 2025-03-02
