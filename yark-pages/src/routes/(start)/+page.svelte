<script lang="ts">
	import StartFederated from '../../components/start/StartFederated.svelte';
	import StartCreate from '../../components/start/StartCreate.svelte';
	import StartLoad from '../../components/start/StartLoad.svelte';
</script>

<div class="cards centre-h">
	<div class="cards-left">
		<StartCreate />
		<StartFederated />
	</div>
	<StartLoad />
</div>

<style lang="scss">
	.cards {
		margin-top: 1.5rem;
	}

	.cards-left {
		margin-right: 1.5rem;
	}
</style>
