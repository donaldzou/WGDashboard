<script setup>

</script>

<template>
<div class="">
	<ul class="nav  gap-0 border-bottom">
		<li class="nav-item">
			<a class="nav-link text-body border-start-0" aria-current="page" href="#">
				<strong>WGDashboard Client</strong>
			</a>
		</li>
		<li class="nav-item ms-auto">
			<a class="nav-link text-body" aria-current="page" href="#">
				<i class="bi bi-gear-fill me-sm-2"></i>
				<span>Settings</span>
			</a>
		</li>
		<li class="nav-item">
			<RouterLink to="/signout" class="nav-link text-danger" aria-current="page">
				<i class="bi bi-box-arrow-left me-sm-2"></i>
				<span>Sign Out</span>
			</RouterLink>
		</li>
	</ul>
	<div class="d-flex flex-column gap-3">
		<div class="px-3 border-bottom py-4">
			<h6>Hi donaldzou@live.hk!</h6>
			<h5 class="mb-0">You have <strong>3</strong> configurations available</h5>
		</div>
		<div></div>
	</div>
</div>
</template>

<style scoped>
.nav-link{
	padding: 1rem 1rem;
	border-left: 1px solid var(--bs-border-color)
}

@media screen and (max-width: 576px) {
	.nav-link span{
		display: none;
	}
}
</style>