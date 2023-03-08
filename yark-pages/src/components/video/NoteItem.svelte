<script lang="ts">
	import { deleteNote, editNote, type Note, type NoteUpdate } from '$lib/archive';
	import Card from '../Card.svelte';

	export let videoId: string;
	export let videoNotes: Note[];
	export let note: Note;
	export let editable = false;
	export let deletable = false;

	let deleteCocked = false;
	let userDefinedTitle: string;
	let userDefinedTimestamp: number = note.timestamp; // TODO
	let userDefinedBody: string;

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

	/**
	 * Edits the note to be what they are defined as
	 */
	async function doEditNote() {
		const payload: NoteUpdate = {
			title: userDefinedTitle,
			body: userDefinedBody,
			timestamp: userDefinedTimestamp
		};
		await editNote(videoId, note.id, payload);
	}
</script>

<div class="note">
	<Card tiny alt>
		<h3 class="video">
			{#if editable}
				<div
					contenteditable="true"
					on:focusout={async () => doEditNote()}
					bind:textContent={userDefinedTitle}
				>
					{note.title}
				</div>
			{:else}
				<div>{note.title}</div>
			{/if}
			{#if deletable}
				<button on:click={() => doDelete()}>
					{#if deleteCocked}⛔️{:else}🗑{/if}
				</button>
			{/if}
		</h3>
		{#if editable}
			<p
				contenteditable="true"
				on:focusout={async () => doEditNote()}
				bind:textContent={userDefinedBody}
			>
				{#if note.body}{note.body}{:else}No further information{/if}
			</p>
		{:else}
			<p>
				{#if note.body}{note.body}{:else}No further information{/if}
			</p>
		{/if}
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
		min-width: 100px;
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
