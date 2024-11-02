<script>
import LocaleText from "@/components/text/localeText.vue";
import dayjs from "dayjs";

export default {
	name: "message",
	methods: {dayjs},
	components: {LocaleText},
	props: {
		message: Object
	},
	mounted() {
		setTimeout(() => {
			this.message.show = false
		}, 5000)
	}
}
</script>

<template>
	<div class="card shadow rounded-3 position-relative message ms-auto" 
	     :class="{
			'text-bg-danger': this.message.type === 'danger', 
			'text-bg-success': this.message.type === 'success',
			'text-bg-warning': this.message.type === 'warning'}"
	     :id="this.message.id">
		<div class="card-body">
			<div class="d-flex">
				<small class="fw-bold d-block" style="text-transform: uppercase">
					<LocaleText t="FROM "></LocaleText>
					{{this.message.from}}
				</small>
				<small class="ms-auto">
					{{dayjs().format("hh:mm A")}}
				</small>
			</div>
			{{this.message.content}}
		</div>
	</div>
</template>

<style scoped>
	.message{
		width: 100%;
	}
	
	@media screen and (min-width: 576px) {
		.message{
			width: 400px;
		}
	}
</style>