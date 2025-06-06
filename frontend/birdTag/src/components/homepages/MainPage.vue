<template>
  <div class="main">
    <div class="search">
      <el-segmented v-model="trigger" :options="options" />
      <el-input 
        v-model="input" 
        style="width: 340px; height: 50px; margin-bottom: 40px" placeholder="Please Input" />
      <button @click="handleSearch" style="width: 100px; height: 50px"> Search </button>
      <button @click="handleTags(1)" style="width: 100px; height: 50px"> AddTags </button>
      <button @click="handleTags(0)" style="width: 100px; height: 50px"> DelTags </button>
      <button @click="handleDelete" style="width: 150px; height: 50px; background-color: #9EB0EA; color: #fff"> Delete Files</button>
    </div>
    <p style="height: 20px;font-size: 10px;margin-top: -10px;color: #dcdcdc;">If you want to add/delete Tags, please input format: (e.g Pigeon,657;Crow,723)</p>
    <div class="cards" v-show="urlData.length">
      <el-card class="box-card" v-for="url in urlData">
        <template v-if="!isImage(url)">
          <a :href="url" target="_blank">
            <video controls style="margin-top: -15px" >
              <source :src="url" type="video/mp4" />
            </video>
          </a> 
        </template>
        <template v-else>
          <a :href="url" target="_blank">
            <img :src="url" alt="media" />
          </a>
        </template>
      </el-card>
    </div>
    <div class ="table">
      <el-table 
      :data="tableData" 
      :row-key="(row) => row.file_id"
      @selection-change="handleSelectionChange"
      style="width: 100%; border-radius: 10px; padding: 20px 10px;">
        <el-table-column type="selection" width="50" />
        <el-table-column label="file" width="400">
          <template #default="{ row }">
            <img 
              v-if="row.file_type == 'image'" 
              width ="200px" 
              style="height: 150px;"
              :src="row.file_id" 
              alt="Preview" 
              class="image-preview"
            />
            <video v-else controls width="200px" height="100px">
              <source :src="row.file_id" type="video/mp4">
            </video>
          </template>
        </el-table-column>
        <el-table-column prop="file_type" label="file_type" width="50" />
        <el-table-column prop="tags" label="tags" width="600" />
      </el-table>
    </div>
  </div>

</template>
<script setup>
import { onMounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus';
import { urlToBase64 } from "../../urlToBase64.js";
import axios from 'axios';

const tableData = ref([])
const urlData = ref([])
const input = ref('')
const selectedFileIds = ref([])
const trigger = ref('Species')
const options = ['Species', 'Tags', 'File_Url']
const idToken = localStorage.getItem('idToken')
const handleSelectionChange = (val) => {
  selectedFileIds.value = val.map(item => item.file_id);
}

const isImage = (url) => {
  return url.toLowerCase().endsWith('.png') || url.toLowerCase().endsWith('.jpg');
};

const handleTags = async (type) => {
  if (selectedFileIds.value.length == 0) {
    ElMessage.error('You need to select files that want to edit tages');
    return 
  }
  let tag = []
  // Pigeon,657;Crow,723
  tag = input.value.split(';')
  
  if (tag.length === 1 && tag[0].indexOf(',') === -1) {
    ElMessage.error('Tags Format Error(e.g Pigeon,657;Crow,723)! ');
  }
  
  const data = {
    url: selectedFileIds.value,
    operation: type,
    tags: tag
  }
  try {
    console.log(data)
    await axios.post('/bird/query/delete_add_by_tags ', data);
    getTableData()
    ElMessage.success('Edit Tags Successful');
  } catch (error) {
    ElMessage.error('Edit Tags Fail Please again');
  }

}

const handleSearch = async () => {
  try {
    const queryType = trigger.value;
    if (queryType == "Tags") {
      const response = await axios.post('/bird/query/found_by_tag', input.value, {
      headers: {
         Authorization: localStorage.getItem('idToken'), 
      }});
      urlData.value = response.data.links;
      ElMessage.success('Search Successful');
    } else if (queryType == "Species") {
      const response = await axios.get(`/bird/query/found_by_species?species=${input.value}`, {
      headers: {
         Authorization: localStorage.getItem('idToken'), 
      }});
      urlData.value = response.data.links;
      ElMessage.success('Search Successful');
    } else {
      const isImage = input.value.indexOf(".png") !== -1 || input.value.indexOf(".jpg") !== -1
      console.log(isImage)
      if (!isImage) {
        ElMessage.error('Sorry, due to timeout restrictions, video/audio url search is not currently supported');
        return
      }
      const base64 = await urlToBase64(input.value);
      const base64WithoutPrefix = base64.startsWith('data:') 
          ? base64.split(',')[1] 
          : base64;
      const response = await axios.post(`/bird/query/found_by_file_uploaded/media_upload`, {
        "file_type": '.png',
        "file_bytes": base64WithoutPrefix
      });
      const tagsBody = {
        "tags": response.data
      }
      const response2 = await axios.post('/bird/query/found_by_tag', tagsBody, {
      headers: {
         Authorization: localStorage.getItem('idToken'), 
      }});
      urlData.value = response2.data.links;
      ElMessage.success('Search Successful');
    }
  } catch (error) {
    ElMessage.error('Search Fail Please again');
  }
};

const handleDelete = async () => {
   try {
    const requestbody = {
      "url": selectedFileIds.value
    }
    await axios.post('/bird/query/delete_files', requestbody, {
      headers: {
        'Content-Type': 'application/json',
         Authorization: idToken, 
      }
    });
    getTableData()
    ElMessage.success('Delete Successful');
  } catch (error) {
    ElMessage.error('Delete Fail Please again');
  }
}

const getTableData = async () => {
  try {
    const response = await axios.get('/bird/query/get_full_data_lists', {
      headers: {
         Authorization: localStorage.getItem('idToken'), 
      }});
    if (response.status === 200) {
      tableData.value = JSON.parse(response.data.body) 
      tableData.value.forEach(it => {
        it.tags = JSON.stringify(it.tags);
      });
       ElMessage.success("Data load successful")
    } else {
       ElMessage.error("Data load failed")
    }
  } catch(error) {
    ElMessage.error("Data load failed")
  }
}

onMounted(getTableData)

</script>

<style lang="less" scoped>
.main {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 90%;
  margin-left: 5%;

  .search {
    width: 100%;
    height: 10%;
    display:flex;
    flex-direction: row;
    justify-content: space-around;
  }

  .cards {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    max-height: 200px;
    margin-bottom: 10px;
    overflow-y: scroll;
    gap: 10px;
  }

  .table {
    width: 100%;
    height: 600px;
    overflow-y: scroll;
    margin-bottom: 50px;
  }

}
.el-table__body, .el-table__footer, .el-table__header {
    border-collapse: separate;
    table-layout: fixed;
    margin-left: 45px;
}
</style>