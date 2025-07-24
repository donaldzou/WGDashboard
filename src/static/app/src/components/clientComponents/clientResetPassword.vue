<script setup lang="ts">

import LocaleText from "@/components/text/localeText.vue";
</script>

<template>
<div class="p-3">
	<h6>
		<LocaleText t="Reset Password"></LocaleText>
	</h6>
	<div class="row g-2">
		<div class="col-sm-4">
			<label class="mb-1">
				<small class="fw-bold text-muted">
					<LocaleText t="Current Password"></LocaleText>
				</small>
			</label>
			<input type="password" class="form-control form-control-sm rounded-3">
		</div>
		<div class="col-sm-4">
			<label class="mb-1">
				<small class="fw-bold text-muted">
					<LocaleText t="New Password"></LocaleText>
				</small>
			</label>
			<input type="password" class="form-control form-control-sm rounded-3">
		</div>
		<div class="col-sm-4">
			<label class="mb-1">
				<small class="fw-bold text-muted">
					<LocaleText t="Confirm New Password"></LocaleText>
				</small>
			</label>
			<input type="password" class="form-control form-control-sm rounded-3">
		</div>
	</div>
</div>
</template>

<style scoped>

</style>