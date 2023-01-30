<script lang="ts">
	import StartCreate from '../../components/start/StartCreate.svelte';
	import StartFederated from '../../components/start/StartFederated.svelte';
	import StartLoad from '../../components/start/StartLoad.svelte';
</script>

<div class="cards">
	<StartCreate />
	<StartFederated />
	<StartLoad />
</div>

<style lang="scss">
	.cards {
		display: flex;
		justify-content: center;
		flex-wrap: wrap;
	}
</style>
