<template>
  <div id="app">
    <!-- <img alt="Vue logo" src="./assets/logo.png" />
    <HelloWorld msg="Welcome to Your Vue.js App" /> -->
    <!-- <loginsystem></loginsystem> -->
    <router-view name="one" class="  " style="min-width: 1300px; min-height: 500px;" :style="{ width: outerDivWidth, height: outerDivHeight }"></router-view>
    <!-- <div
      class="bg-black"
      id="outer-div"
      :style="{ width: outerDivWidth, height: outerDivHeight }"
    ></div> -->
    <!-- <router-view name="tow"></router-view> -->
  </div>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'
export default {
  name: "App",
  components: {HelloWorld},
  data() {
    return {
      outerDivWidth: "", // 最外层div的宽度
      outerDivHeight: "", // 最外层div的高度
    };
  },
  mounted() {
    this.setOuterDivSize(); // 初始化时设置最外层div的尺寸
    // 监听WebSocket的message事件
    console.log("dfsdf")
    this.$socket.addEventListener("message", (event) => {
      // 当收到消息时，将消息添加到this.messages数组中
      console.log(event.data)

    });
    // 监听窗口大小改变事件，在窗口大小改变时更新最外层div的尺寸
    window.addEventListener("resize", this.setOuterDivSize);
  },
  beforeDestroy() {
    // 组件销毁时，移除窗口大小改变事件的监听
    window.removeEventListener("resize", this.setOuterDivSize);
  },
  methods: {
    setOuterDivSize() {
      this.outerDivWidth = window.innerWidth + "px";
      this.outerDivHeight = window.innerHeight + "px";
    },
  },

};
</script>

<style lang="css" scoped>

::v-deep .el-scrollbar__wrap{
  overflow-x: hidden;
}
</style>
