<template>
    <el-table :data="tableData" style="width: 90%; border-radius: 10px; margin-left:5%">
        <el-table-column fixed prop="file_id" label="file_id" width="150" />
        <el-table-column prop="file_name" label="file_name" width="120" />
        <el-table-column prop="file_type" label="file_type" width="120" />
        <el-table-column prop="tags" label="tags" width="120" />
        <el-table-column fixed="right" label="Operations" min-width="120">
            <template #default>
                <el-button link type="primary" size="small" @click="handleClick">
                Detail
                </el-button>
                <el-button link type="primary" size="small">Del</el-button>
            </template>
        </el-table-column>
    </el-table>
</template>
<script setup>
const handleClick = () => {
  console.log('click')
}

const tableData = [
  {
    file_id: '2016-05-03',
    file_name: 'Tom',
    file_type: 'California',
    tags: 'Home',
  },
  {
    file_id: '2016-05-02',
    file_name: 'Tom',
    file_type: 'California',
    tags: 'Office',
  },
  {
    file_id: '2016-05-04',
    file_name: 'Tom',
    file_type: 'California',
    tags: 'Home',
  },
  {
    file_id: '2016-05-01',
    file_name: 'Tom',
    file_type: 'California',
    tags: 'Office',
  },
]
</script>

<style lang="less" scoped></style>