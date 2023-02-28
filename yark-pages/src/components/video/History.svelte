<script lang="ts">
	import type { VideoDetailed } from '$lib/archive';
	import { elementWasUpdated } from '$lib/element';
	import HistoryItem from './HistoryItem.svelte';

	export let video: VideoDetailed;

	$: titleEntries = Object.entries(video.title);
	$: descriptionEntries = Object.entries(video.description);
</script>

<h2 class="video">History</h2>
<p class="video" style="margin-bottom:0.35rem;">Author's changes</p>
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
	{#if !elementWasUpdated(video.views)}
		<li>No view count changes on record</li>
	{/if}
	{#if !elementWasUpdated(video.likes)}
		<li>No like count changes on record</li>
	{/if}
</ul>

<style lang="scss">
</style>
