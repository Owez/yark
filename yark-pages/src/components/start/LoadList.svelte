<script lang="ts">
	import { yarkStore } from '$lib/store';
	import type { Archive } from '$lib/archive';
	import LoadListItem from './LoadListItem.svelte';

	export let count = 4;

	/**
	 * Gets most recent archives up to the count
	 * @param recents Archive list to use in computation
	 */
	function getArchives(recents: Archive[]): Archive[] {
		return recents.slice().reverse().slice(0, count);
	}
</script>

<h2 class="card-heading">Recents</h2>
<div class="list">
	{#each getArchives($yarkStore.recents) as archive}
		<LoadListItem {archive} />
	{/each}
</div>

<style lang="scss">
	.list {
		margin-bottom: 0.75rem;
		display: flex;
		flex-direction: column;
	}
</style>
