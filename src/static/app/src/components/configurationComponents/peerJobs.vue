<script>
export default {
	name: "peerJobs"
}
</script>

<template>
	<div class="container po">
		<div class="mb-5">
			<RouterLink to="peers" is="div" class="d-flex align-items-center gap-4 text-decoration-none">
				<h3 class="mb-0 text-body">
					<i class="bi bi-chevron-left"></i>
				</h3>
				<h3 class="text-body mb-0">Peer Jobs</h3>
			</RouterLink>
		</div>
		<div>
			<div class="row">
				<div class="col-sm-4">
					<small class="text-muted">Peer</small>
					<p class="mb-0"><samp>ymoO2hZDAxnMXOcMML7rnE5ot8lLoh9Uma8mzt1TwAc=</samp></p>
				</div>
				<div class="col-sm-8">
					<div class="card shadow-sm rounded-3">
						<div class="card-header bg-transparent text-muted border-0">
							<small class="d-flex">
								<strong class="me-auto">Job ID</strong>
								7e9b5ef2-9417-4399-88a4-79ac378edfae
							</small>
						</div>
						<div class="card-body pt-1">
							<div class="d-flex gap-3 align-items-center">
								<samp>
									if
								</samp>
								<div class="dropdown">
									<button class="btn btn-sm btn-outline-primary rounded-3" type="button" data-bs-toggle="dropdown" aria-expanded="false">
										<samp>Total Received</samp>
									</button>
									<ul class="dropdown-menu rounded-3">
										<li><a class="dropdown-item" href="#">Total Usage</a></li>
										<li><a class="dropdown-item" href="#">Total Sent</a></li>
										<li><a class="dropdown-item" href="#">Total Received</a></li>
									</ul>
								</div>
								<samp>
									is
								</samp>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>