<script lang="ts">
	import { Archive } from '$lib/archive';
	import { StartCardState } from '$lib/components';
	import { LOCAL_SERVER } from '$lib/utils';
	import { exists } from '@tauri-apps/api/fs';
	import DirSelect from '../../../../components/entries/DirSelect.svelte';
	import Name from '../../../../components/entries/Name.svelte';
	import LoadList from '../../../../components/start/LoadList.svelte';
	import StartCard from '../../../../components/start/StartCard.svelte';

	let path: string;
	let name: string;
	let pathCompletelyInvalid: boolean = false;
	let nameCompletelyInvalid: boolean = false;

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
		nameCompletelyInvalid = name == undefined || name == '';
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
	async function importArchive() {
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
		const importedArchive = await Archive.createExisting(LOCAL_SERVER, name, path);
		importedArchive.setAsCurrent();
	}
</script>

<div class="centre-h">
	<StartCard
		title="Load Existing"
		description="Manage or view an archive that's already been made"
		ballKind={1}
		state={StartCardState.Max}
	>
		<h2 class="card-heading">Import Archive</h2>
		<DirSelect bind:path bind:pathCompletelyInvalid />
		<Name bind:name bind:nameCompletelyInvalid placeholder="New name" />
		<button on:click={async () => importArchive()} class="bright">Import</button>
		<LoadList count={10} />
	</StartCard>
</div>
