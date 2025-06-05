<template>
    <div class="upload-container">
        <el-upload
            v-model:file-list="uploadedFiles"
            class="drop-zone"
            :auto-upload="false"
            @change="handleChange"
            :http-request="() => {}"
            drag
            multiple
        >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
            Drop file here or <em>click to upload</em>
            </div>
            <template #tip>
            <div class="el-upload__tip">
              upload jpg/png/audio/video files
            </div>
            </template>
        </el-upload>
    </div>
</template>
<script setup>
import { ref, reactive } from 'vue';
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus';
import axios from 'axios';

const uploadedFiles = reactive([]);

const handleChange = async (uploadFile, uploadFiles) => {
  const rawFile = uploadFile.raw;
  if (!rawFile) return;
  await handleBeforeUpload(rawFile);
};

const handleBeforeUpload = async (file) => {
    const idToken = localStorage.getItem('idToken')
    if (!idToken) throw new Error('User not authenticated')

    try {
      const fileType = file.type;
      let folder = '';
      if (fileType.startsWith('image/')) {
        folder = 'Images';
      } else if (fileType.startsWith('audio/')) {
        folder = 'Audios';
      } else if (fileType.startsWith('video/')) {
        folder = 'Videos';
      } else {
        throw new Error('Unsupported file type');
      }
      const requestBody = {
        folder: folder,
        suffix: "." + file.name.split('.').pop(), 
        contentType: fileType,
      };
    const response = await axios.post('/bird/upload', requestBody, {
      headers: {
        'Content-Type': 'application/json',
         Authorization: idToken, 
      }
    });
    if (response.status === 200) {
      const { uploadUrl } = response.data;
      if (uploadUrl) {
        await axios.put(uploadUrl, file, {
          headers: {
            'Content-Type': fileType,
          },
        });
        ElMessage.success('Upload Successful');
      }
    } else {
      ElMessage.error('Upload Fail Please again');
    }
    } catch (error) {
    console.error('Error:', error);
    ElMessage.error('Upload Fail Please again');
  }
}

</script>

<style lang="less" scoped>
.upload-container {
  width: 100%;
  height: 650px;
  overflow: hidden;

  .drop-zone {
    height: 250px;
  }
}
.el-upload__tip {
    color: var(--el-text-color-regular);
    font-size: 12px;
    margin-top: 7px;
    height: 10px;
}

</style>