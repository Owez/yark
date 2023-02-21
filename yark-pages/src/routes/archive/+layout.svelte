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
		width: 100%;
        margin:0;
	}
</style>
