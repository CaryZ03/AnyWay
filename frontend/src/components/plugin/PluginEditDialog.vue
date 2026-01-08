<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { pluginApi } from '@/api'
import type { Plugin, PluginForm, OpenAPISpec, PluginConfig } from '@/types/plugin'
import type { Plugin as PluginType } from '@/types/plugin'

const props = defineProps<{
  modelValue: boolean
  plugin?: Plugin | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}>()

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const error = ref<string>('')

// 表单数据
const formData = ref<PluginForm>({
  name: '',
  description: '',
  type: 'custom',
  openapiSpec: {
    openapi: '3.0.0',
    info: {
      title: '',
      description: '',
      version: '1.0.0'
    },
    servers: [
      {
        url: '',
        description: ''
      }
    ],
    paths: {}
  },
  config: {
    baseUrl: ''
  },
  status: 'enabled'
})

// 初始化表单数据
watch([() => props.plugin, () => props.modelValue], async ([plugin, modelValue]) => {
  if (!modelValue) return
  
  if (plugin) {
    let currentPlugin: PluginType = plugin
    
    // 如果插件没有 openapiSpec，需要先获取详情
    if (!currentPlugin.openapiSpec || currentPlugin.openapiSpec === '') {
      if (currentPlugin.id) {
        try {
          const fullPlugin = await pluginApi.getDetail(currentPlugin.id)
          // 使用完整插件信息初始化表单
          currentPlugin = fullPlugin
        } catch (err: any) {
          console.error('获取插件详情失败:', err)
          error.value = '获取插件详情失败，请稍后重试'
          return
        }
      } else {
        // 没有 id，无法获取详情，使用空表单
        formData.value = {
          name: '',
          description: '',
          type: 'custom',
          openapiSpec: {
            openapi: '3.0.0',
            info: {
              title: '',
              description: '',
              version: '1.0.0'
            },
            servers: [
              {
                url: '',
                description: ''
              }
            ],
            paths: {}
          },
          config: {
            baseUrl: ''
          },
          status: 'enabled'
        }
        return
      }
    }

    if (!currentPlugin.openapiSpec) {
      error.value = '插件数据不完整，无法编辑'
      return
    }

    const spec = typeof currentPlugin.openapiSpec === 'string'
      ? JSON.parse(currentPlugin.openapiSpec)
      : currentPlugin.openapiSpec

    // 处理 config，确保是对象类型
    let config: PluginConfig = { baseUrl: '' }
    if (currentPlugin.config) {
      if (typeof currentPlugin.config === 'string') {
        try {
          config = JSON.parse(currentPlugin.config)
        } catch {
          config = { baseUrl: '' }
        }
      } else {
        config = currentPlugin.config
      }
    }

    formData.value = {
      id: currentPlugin.id,
      name: currentPlugin.name,
      description: currentPlugin.description || '',
      type: currentPlugin.type,
      openapiSpec: spec,
      config,
      status: currentPlugin.status
    }
  } else if (!plugin && props.modelValue) {
    // 新建模式，重置表单
    formData.value = {
      name: '',
      description: '',
      type: 'custom',
      openapiSpec: {
        openapi: '3.0.0',
        info: {
          title: '',
          description: '',
          version: '1.0.0'
        },
        servers: [
          {
            url: '',
            description: ''
          }
        ],
        paths: {}
      },
      config: {
        baseUrl: ''
      },
      status: 'enabled'
    }
  }
}, { immediate: true })

// JSON 编辑器内容
const jsonEditor = ref('')
const jsonError = ref('')

// 同步 openapiSpec 到 JSON 编辑器
watch(() => formData.value.openapiSpec, (spec) => {
  try {
    jsonEditor.value = JSON.stringify(spec, null, 2)
    jsonError.value = ''
  } catch (e) {
    jsonError.value = 'JSON格式化失败'
  }
}, { immediate: true, deep: true })

// 同步 JSON 编辑器到 openapiSpec
const updateFromJson = () => {
  try {
    const parsed = JSON.parse(jsonEditor.value)
    
    // 验证必需字段
    if (!parsed.openapi) {
      jsonError.value = 'JSON缺少必需字段: openapi'
      return
    }
    if (!parsed.info || typeof parsed.info !== 'object') {
      jsonError.value = 'JSON缺少必需字段: info'
      return
    }
    if (!parsed.info.title) {
      jsonError.value = 'JSON中info.title字段不能为空'
      return
    }
    if (!parsed.servers || !Array.isArray(parsed.servers) || parsed.servers.length === 0) {
      jsonError.value = 'JSON中servers字段必须是非空数组'
      return
    }
    if (!parsed.servers[0] || !parsed.servers[0].url) {
      jsonError.value = 'JSON中servers[0].url字段不能为空'
      return
    }
    if (!parsed.paths || typeof parsed.paths !== 'object') {
      jsonError.value = 'JSON缺少必需字段: paths'
      return
    }
    
    formData.value.openapiSpec = parsed as OpenAPISpec
    
    // 更新基本信息
    if (parsed.info) {
      formData.value.name = parsed.info.title || ''
      formData.value.description = parsed.info.description || ''
    }
    
    // 更新 baseUrl
    if (parsed.servers && parsed.servers.length > 0 && parsed.servers[0]) {
      formData.value.config.baseUrl = parsed.servers[0].url || ''
    }
    
    jsonError.value = ''
  } catch (e: any) {
    jsonError.value = `JSON解析失败: ${e.message}`
  }
}

// 验证表单
const validate = (): boolean => {
  if (!formData.value.openapiSpec.info?.title) {
    error.value = '请填写插件名称（在 info.title 中）'
    return false
  }
  
  if (!formData.value.openapiSpec.servers || formData.value.openapiSpec.servers.length === 0) {
    error.value = '请填写服务器地址（在 servers[0].url 中）'
    return false
  }
  
  if (!formData.value.openapiSpec.servers[0] || !formData.value.openapiSpec.servers[0].url) {
    error.value = '请填写服务器地址'
    return false
  }
  
  error.value = ''
  return true
}

// 保存
const handleSave = async () => {
  // 先同步 JSON 编辑器
  updateFromJson()
  
  // 如果 JSON 解析失败，阻止保存
  if (jsonError.value) {
    error.value = jsonError.value
    return
  }
  
  // 验证 openapiSpec 完整性
  const spec = formData.value.openapiSpec
  if (!spec) {
    error.value = 'OpenAPI规范数据为空，请检查JSON编辑器'
    return
  }
  
  if (!spec.openapi) {
    error.value = 'OpenAPI规范缺少 openapi 字段，请在JSON中添加 "openapi": "3.0.0"'
    return
  }
  
  if (!spec.info || typeof spec.info !== 'object') {
    error.value = 'OpenAPI规范缺少 info 字段，请在JSON中添加 info 对象'
    return
  }
  
  if (!spec.info.title) {
    error.value = 'OpenAPI规范中 info.title 字段不能为空，请填写插件名称'
    return
  }
  
  if (!spec.servers || !Array.isArray(spec.servers) || spec.servers.length === 0) {
    error.value = 'OpenAPI规范中 servers 字段必须是非空数组，请添加服务器地址'
    return
  }
  
  if (!spec.servers[0] || !spec.servers[0].url) {
    error.value = 'OpenAPI规范中 servers[0].url 字段不能为空，请填写服务器地址'
    return
  }
  
  if (!spec.paths || typeof spec.paths !== 'object') {
    error.value = 'OpenAPI规范缺少 paths 字段，请在JSON中添加 paths 对象（可以为空对象 {}）'
    return
  }
  
  // 验证表单
  if (!validate()) {
    return
  }

  loading.value = true
  error.value = ''

  try {
    console.log('准备保存插件，完整数据:', JSON.stringify(formData.value, null, 2))
    console.log('openapiSpec:', JSON.stringify(formData.value.openapiSpec, null, 2))
    
    if (props.plugin?.id) {
      // 更新
      await pluginApi.update(props.plugin.id, formData.value)
    } else {
      // 创建
      await pluginApi.create(formData.value)
    }
    
    emit('success')
    dialogVisible.value = false
  } catch (err: any) {
    console.error('保存插件失败:', err)
    // request.ts 的响应拦截器已经将错误转换为 Error 对象，message 字段包含错误信息
    // 兼容处理：支持直接 Error 对象和 axios 错误响应
    const errorMessage = err?.message || err?.response?.data?.message || err?.response?.data?.detail || '保存失败'
    error.value = errorMessage
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  dialogVisible.value = false
  error.value = ''
  jsonError.value = ''
}
</script>

<template>
  <div v-if="dialogVisible" class="dialog-overlay" @click.self="handleCancel">
    <div class="dialog-container">
      <div class="dialog-header">
        <h2 class="dialog-title">{{ plugin ? '编辑插件' : '创建插件' }}</h2>
        <button class="close-btn" @click="handleCancel">×</button>
      </div>

      <div class="dialog-body">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div class="form-group">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label required">插件名称</label>
              <input
                v-model="formData.openapiSpec.info.title"
                type="text"
                class="form-input"
                placeholder="例如：IoT设备控制"
                maxlength="100"
                required
                @input="formData.name = formData.openapiSpec.info.title"
              />
              <div class="char-count">{{ formData.openapiSpec.info.title.length }}/100</div>
            </div>
            <div class="form-group">
              <label class="form-label required">版本</label>
              <input
                v-model="formData.openapiSpec.info.version"
                type="text"
                class="form-input"
                placeholder="1.0.0"
                maxlength="20"
                required
              />
              <div class="char-count">{{ formData.openapiSpec.info.version.length }}/20</div>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">描述</label>
            <textarea
              v-model="formData.openapiSpec.info.description"
              class="form-textarea"
              rows="3"
              placeholder="插件功能描述..."
              maxlength="500"
              @input="formData.description = formData.openapiSpec.info.description"
            />
            <div class="char-count">{{ (formData.openapiSpec.info.description || '').length }}/500</div>
          </div>
        </div>

        <div class="form-group">
          <div class="section-header">
            <label class="form-label required">OpenAPI 规范（JSON）</label>
            <button class="sync-btn" @click="updateFromJson" :disabled="!!jsonError">
              同步到表单
            </button>
          </div>
          <div v-if="jsonError" class="json-error">
            {{ jsonError }}
          </div>
          <textarea
            v-model="jsonEditor"
            class="json-editor"
            placeholder="{\n  &quot;openapi&quot;: &quot;3.0.0&quot;,\n  &quot;info&quot;: {...},\n  &quot;paths&quot;: {...}\n}"
          />
          <div class="form-hint">
            提示：修改 JSON 后点击"同步到表单"按钮，或者直接修改上方表单字段
          </div>
        </div>

        <div class="form-group">
          <div class="radio-group">
            <label class="radio-item">
              <input
                v-model="formData.status"
                type="radio"
                value="enabled"
              />
              <span>已启用</span>
            </label>
            <label class="radio-item">
              <input
                v-model="formData.status"
                type="radio"
                value="disabled"
              />
              <span>已禁用</span>
            </label>
          </div>
        </div>
      </div>

      <div class="dialog-footer">
        <button type="button" class="btn btn-cancel" @click="handleCancel" :disabled="loading">
          取消
        </button>
        <button type="button" class="btn btn-primary" @click="handleSave" :disabled="loading">
          {{ loading ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-container {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.dialog-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  cursor: pointer;
  color: #6b7280;
  font-size: 24px;
  line-height: 1;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.dialog-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.error-message {
  padding: 12px 16px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  font-size: 14px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 6px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.form-label.required::after {
  content: ' *';
  color: #ef4444;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  transition: all 0.2s;
  box-sizing: border-box;
  background: white;
  color: #1f2937;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-textarea {
  resize: vertical;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.json-editor {
  width: 100%;
  min-height: 250px;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 13px;
  font-family: 'SF Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  line-height: 1.6;
  resize: vertical;
  background: #f9fafb;
  color: #1f2937;
}

.json-editor:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  background: white;
}

.json-error {
  padding: 8px 12px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #991b1b;
  font-size: 12px;
  margin-bottom: 8px;
}

.form-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #6b7280;
}

.sync-btn {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.sync-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.sync-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.radio-group {
  display: flex;
  gap: 24px;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.radio-item input[type="radio"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #2563eb;
}

.radio-item span {
  font-size: 14px;
  color: #374151;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.btn-primary:disabled,
.btn-cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

