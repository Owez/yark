<script lang="ts">
	import { importNewRemoteArchive, setCurrentArchive } from '$lib/archive';
	import { StartCardState } from '$lib/components';
	import { LOCAL_SERVER } from '$lib/utils';
	import { exists } from '@tauri-apps/api/fs';
	import DirSelect from '../../../../components/entries/DirSelect.svelte';
	import Name from '../../../../components/entries/Name.svelte';
	import LoadList from '../../../../components/start/LoadList.svelte';
	import StartCard from '../../../../components/start/StartCard.svelte';

	let path: string;
	let name: string;
	let pathCompletelyInvalid = false;
	let nameCompletelyInvalid = false;

	/**
	 * Checks that the path prop is valid
	 */
	async function checkPathValidity(): Promise<boolean> {
		// TODO: merge validation
		pathCompletelyInvalid = path == undefined || path == '' || !(await exists(path));
		return !pathCompletelyInvalid;
	}

	/**
	 * Checks that the name prop is valid
	 */
	function checkNameValidity(): boolean {
		// TODO: merge validation
		nameCompletelyInvalid = name == undefined || name == '' || name.length < 2;
		return !nameCompletelyInvalid;
	}

	/**
	 * Validates all relevant props
	 * @returns If the inputs are valid or not
	 */
	async function validate(): Promise<boolean> {
		// Check validity beforehand so or doesn't cancel it out
		const pathValid = await checkPathValidity();
		const nameValid = checkNameValidity();

		// Return if they're all valid
		return pathValid && nameValid;
	}

	/**
	 * Loads archive from information provided, making sure it's all valid beforehand
	 */
	async function importOldArchive() {
		// Validate the inputs
		if (!(await validate())) {
			return;
		}

		// Skip if anything is missing
		// NOTE: only for getting rid of incorrect typing errors, can delete
		if (path == undefined || name == undefined) {
			return;
		}

		// Import the archive into the API
		const importedArchive = await importNewRemoteArchive({
			server: LOCAL_SERVER,
			path: path,
			slug: name
		});
		setCurrentArchive(importedArchive);
	}

	/**
	 * Imports archive which already exists in the API
	 */
	async function importExistingArchive() {
		// Validate name only
		if (name == undefined || nameCompletelyInvalid) {
			return;
		}

		// Import the archive already in the API
		const importedArchive = { server: LOCAL_SERVER, slug: name };
		setCurrentArchive(importedArchive);
	}
</script>

<div class="centre-h">
	<StartCard
		title="Load Existing"
		description="Manage or view an archive that's already been made"
		ballKind={1}
		state={StartCardState.Max}
	>
		<h2 class="card-heading">Import v1.2 Archive</h2>
		<DirSelect bind:path bind:pathCompletelyInvalid />
		<Name bind:name bind:nameCompletelyInvalid placeholder="New name" />
		<button on:click={async () => importOldArchive()} class="bright">Import</button>
		<h2 class="card-heading">Use Existing</h2>
		<Name bind:name bind:nameCompletelyInvalid placeholder="Previously-saved archive name" mini={false} />
		<button on:click={async () => importExistingArchive()} class="bright">Use</button>
		<LoadList count={10} />
	</StartCard>
</div>
