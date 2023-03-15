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
	let userDefinedTitleInvalid: boolean = false;
	let userDefinedTimestamp: number = note.timestamp; // TODO
	let userDefinedBody: string;

	const bodyPlaceholder = 'No further information.';

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
		// Validate title before anything else
		if (!validateTitle()) {
			return;
		}

		// Edit it in the API
		let payload: NoteUpdate = {};
		let changed = false;

		// Add title if it's relevant
		if (userDefinedTitle != note.title) {
			payload.title = userDefinedTitle;
			changed = true;
		}

		// Add timestamp if it's relevant
		if (userDefinedTimestamp != note.timestamp) {
			payload.timestamp = userDefinedTimestamp;
			changed = true;
		}

		// Add body if it's relevant
		if (userDefinedBody != note.body) {
			if (userDefinedBody == '') {
				userDefinedBody = bodyPlaceholder;
			}
			payload.body = userDefinedBody;
			changed = true;
		}

		// Make sure something has changed
		if (!changed) {
			return;
		}

		// Edit it locally
		note.title = userDefinedTitle;
		note.body = userDefinedBody;
		note.timestamp = userDefinedTimestamp;

		await editNote(videoId, note.id, payload);
	}

	/**
	 * Validates the user defined title, to be called on focus out for user feedback
	 */
	function validateTitle(): boolean {
		const invalid = userDefinedTitle == undefined || userDefinedTitle == '';
		userDefinedTitleInvalid = invalid;
		return !invalid;
	}
</script>

<div class="note">
	<Card tiny alt>
		<h3 class="video">
			{#if editable}
				<div
					class="title"
					contenteditable="true"
					on:focusout={async () => doEditNote()}
					bind:textContent={userDefinedTitle}
					class:invalid={userDefinedTitleInvalid}
				>
					{note.title}
				</div>
			{:else}
				<div class="title">{note.title}</div>
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
				{#if note.body == undefined}
					{bodyPlaceholder}
				{:else}
					{note.body}
				{/if}
			</p>
		{:else}
			<p>
				{#if note.body == undefined}
					{bodyPlaceholder}
				{:else}
					{note.body}
				{/if}
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
		display: flex;
		align-items: center;
		justify-content: space-between;

		div.title {
			width: 235px;

			&.invalid {
				padding: 3px;
				border-radius: 5px;
			}
		}
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
