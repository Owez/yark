<script lang="ts">
	import type { Note } from '$lib/archive';
	import Card from '../Card.svelte';

	export let note: Note;
</script>

<div class="note">
	<Card mini={true}>
		<h3 class="video">{note.title}</h3>
		<p class="video">{note.id}</p>
		<p>{note.body}</p>
	</Card>
</div>

<style lang="scss">
	.note {
		$margin-v: 0.35rem;

		margin-top: $margin-v;
		margin-bottom: $margin-v;
	}

	
</style>
