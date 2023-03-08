<script lang="ts">
	import type { VideoDetailed } from '$lib/archive';
	import NoteItem from './NoteItem.svelte';

	export let videoId: string;
	export let video: VideoDetailed;
</script>

{#if video.notes.length != 0}
	<h2 class="video">Notes</h2>
	<p class="video">Interesting information</p>
	<div class="notes">
		{#each video.notes as note}
			<NoteItem {videoId} bind:videoNotes={video.notes} {note} />
		{/each}
	</div>
{/if}

<style lang="scss">
	.notes {
		display: flex;
		flex-wrap: wrap;
	}
</style>
