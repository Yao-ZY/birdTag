<template>
  <div class="main">
    <div class="search">
      <el-segmented v-model="trigger" :options="options" />
      <el-input 
        v-model="input" 
        style="width: 340px; height: 50px; margin-bottom: 40px" placeholder="Please input" />
      <button @click="handleSearch" style="width: 100px; height: 50px"> Search </button>
      <button @click="handleDelete" style="width: 200px; height: 50px; background-color: #9EB0EA; color: #fff"> Delete Files</button>
    </div>
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
              style="width: 200px; height: 100px"
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
import axios from 'axios';
const tableData = ref([])
const urlData = ref([])
const input = ref('')
const selectedFileIds = ref([])
const trigger = ref('Species')
const options = ['Species', 'Tags', 'File_Url']

const handleSelectionChange = (val) => {
  selectedFileIds.value = val.map(item => item.file_id);
}

const isImage = (url) => {
  return url.toLowerCase().endsWith('.png') || url.toLowerCase().endsWith('.jpg');
};

const handleSearch = async () => {
  try {
    console.log(trigger.value)
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
      console.log(urlData.value)
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
    await axios.post('/bird/query/delete_files', requestbody);
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
  }

}
.el-table__body, .el-table__footer, .el-table__header {
    border-collapse: separate;
    table-layout: fixed;
    margin-left: 45px;
}
</style>