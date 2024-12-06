<template>
  <div class="dropdown" :class="{ disabled: disabled }" @click="toggleDropdown" @focusout="hideDropdown" tabindex="0">
    <div class="title">
      <div>{{ title }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Dropdown",
  props: {
    width: {
      type: String,
      default: "80px",
    },
    height: {
      type: String,
      default: "auto",
    },
    title: {
      type: String,
      default: "",
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    defaultDisplay: {
      type: Boolean,
      default: false,
    },
  }
};
</script>

<style>
.code-editor .disabled:hover > .title {
  opacity: 0.5 !important;
}
.code-editor .dropdown:hover > .title {
  opacity: 1;
}
.code-editor .dropdown > .title {
  transition: opacity 0.2s ease;
  opacity: 0.5;
  display: flex;
  align-items: center;
  -webkit-user-select: none;
  user-select: none;
}
.code-editor .dropdown > .title > div {
  white-space: nowrap;
  font-size: 12px;
  line-height: 16px;
}
.code-editor .dropdown > .title > svg {
  transition: 0.2s;
  margin-left: 3px;
  margin-top: 1px;
}
</style>
