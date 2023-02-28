<script lang="ts">
	import type { VideoDetailed } from '$lib/archive';
	import HistoryItem from './HistoryItem.svelte';

	export let video: VideoDetailed;

	$: titleEntries = Object.entries(video.title);
	$: descriptionEntries = Object.entries(video.description);
</script>

<ul>
	{#if titleEntries.length < 2}
		<li>No title changes on record</li>
	{:else}
		{#each titleEntries as entry, ind}
			<HistoryItem name="title" {entry} {ind} />
		{/each}
	{/if}
	{#if descriptionEntries.length < 2}
		<li>No description changes on record</li>
	{:else}
		{#each descriptionEntries as entry, ind}
			<HistoryItem name="description" {entry} {ind} />
		{/each}
	{/if}
</ul>

<style lang="scss">

</style>
