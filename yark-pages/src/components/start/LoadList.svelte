<script lang="ts">
	import { yarkStore } from '$lib/store';
	import type { Archive } from '$lib/archive';
	import LoadListArchive from './LoadListArchive.svelte';

	export let count: number = 4;

	/**
	 * Gets most recent archives up to the count
	 */
	function getArchives(recents: Archive[]): Archive[] {
		return recents.slice().reverse().slice(0, count);
	}
</script>

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
