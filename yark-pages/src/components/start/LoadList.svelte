<script lang="ts">
	import { yarkStore } from '$lib/store';
	import type { Archive } from '$lib/archive';
	import LoadListArchive from './LoadListArchive.svelte';

	export let count: number = 5;

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
		<LoadListArchive {archive} />
	{/each}
</div>

<style lang="scss">
	.list {
		margin-bottom: 1.25rem;
		display: flex;
		flex-direction: column;
	}
</style>
