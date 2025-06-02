<template>
    <div class="upload-container">
        <el-upload
            v-model:file-list="uploadedFiles"
            :on-change="handleChange"
            class="drop-zone"
            drag
            action="https://run.mocky.io/v3/9d059bf9-4660-45f2-925d-ce80ad6c4d15"
            multiple
        >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
            Drop file here or <em>click to upload</em>
            </div>
            <template #tip>
            <div class="el-upload__tip">
                jpg/png files with a size less than 500kb
            </div>
            </template>
        </el-upload>
    </div>
</template>
<script setup>
import { ref, reactive } from 'vue';
import { UploadFilled } from '@element-plus/icons-vue'

const uploadedFiles = reactive([
  {
    name: 'Food.png',
    status: 'success',
    statusText: 'Upload Success',
    thumbnail: 'src/assets/home.png'
  },
  {
    name: 'Food.png',
    status: 'error',
    statusText: 'Upload File',
    thumbnail: 'src/assets/home.png'
  }
]);
const handleChange = (uploadFile, uploadFiles) => {
  uploadedFiles = uploadedFiles.slice(-3);
};
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