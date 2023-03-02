<script lang="ts">
	import type { VideoDetailed } from '$lib/archive';
	import NoteItem from './NoteItem.svelte';

	export let video: VideoDetailed;
</script>

{#if video.notes.length != 0}
	<h2 class="video">Notes</h2>
	<p class="video">Interesting information</p>
	{#each video.notes as note}
		<NoteItem {note} />
	{/each}
{/if}
