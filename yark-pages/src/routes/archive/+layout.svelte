<script>
	import Sidebar from '../../components/Sidebar.svelte';
</script>

<div class="split">
	<Sidebar />
	<div class="content"><slot /></div>
</div>

<style lang="scss">
	.split {
		display: flex;
	}

	.content {
		$gap: 1rem;

		width: 100%;
		height: 100vh;
		overflow-y: auto;
		padding-left: $gap;
		padding-right: $gap;
	}
</style>
