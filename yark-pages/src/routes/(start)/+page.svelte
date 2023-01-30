<script lang="ts">
	import StartConnect from '../../components/start/StartConnect.svelte';
	import StartCreate from '../../components/start/StartCreate.svelte';
	import StartLoad from '../../components/start/StartLoad.svelte';
</script>

<div class="cards">
	<div class="cards-left">
		<StartCreate />
		<StartConnect />
	</div>
	<StartLoad />
</div>

<style lang="scss">
	.cards {
		display: flex;
		justify-content: center;
		flex-wrap: wrap;
		margin-top: 1.5rem;
	}

	.cards-left {
		margin-right: 1.5rem;
	}
</style>
