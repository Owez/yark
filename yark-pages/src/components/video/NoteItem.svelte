<script lang="ts">
	import type { Note } from '$lib/archive';
	import Card from '../Card.svelte';

	export let note: Note;

	let deleteCocked = false;

	function tryDelete() {
		// Cock and stop if not
		if (!deleteCocked) {
			deleteCocked = true;
			return;
		}
	}
</script>

<div class="note">
	<Card tiny alt>
		<h3 class="video">
			<div>{note.title}</div>
			<button on:click={tryDelete()}>
				{#if deleteCocked}⛔️{:else}🗑{/if}
			</button>
		</h3>
		<p>{note.body}</p>
	</Card>
</div>

<style lang="scss">
	.note {
		$margin-v: 0.5rem;

		margin-top: $margin-v;
		margin-bottom: $margin-v;
		margin-right: $margin-v;
	}

	h3 {
		width: 100%;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	button {
		background: 0;
		border: 0;
	}

	p {
		font-size: 12px;
		margin-top: 3.5px;
		overflow-y: auto;
		max-height: 5.75rem;
		color: #4a4a4a;
	}
</style>
