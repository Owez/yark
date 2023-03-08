<script lang="ts">
	import { deleteNote, type Note } from '$lib/archive';
	import Card from '../Card.svelte';

	export let videoId: string;
	export let videoNotes: Note[];
	export let note: Note;

	let deleteCocked = false;

	/**
	 * Cocks and then resets the cocked status after a little while
	 */
	function cockDelete() {
		deleteCocked = true;
		const seconds = 1.25;
		setTimeout(function () {
			deleteCocked = false;
		}, seconds * 1000);
	}

	/**
	 * Deletes or cocks the deletion status
	 */
	async function doDelete() {
		// Cock and stop if not
		if (!deleteCocked) {
			cockDelete();
			return;
		}

		// Delete the note from the API
		await deleteNote(videoId, note);

		// Filter the note out from the list
		const keptNotes = videoNotes.filter((n) => n.id != note.id);
		videoNotes = keptNotes;
	}
</script>

<div class="note">
	<Card tiny alt>
		<h3 class="video">
			<div>{note.title}</div>
			<button on:click={() => doDelete()}>
				{#if deleteCocked}⛔️{:else}🗑{/if}
			</button>
		</h3>
		<p>
			{#if note.body}{note.body}{:else}No further information{/if}
		</p>
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
		margin: 0;
	}

	p {
		font-size: 12px;
		margin-top: 5px;
		overflow-y: auto;
		max-height: 5.75rem;
		color: #4a4a4a;
	}
</style>
