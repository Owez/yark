<script lang="ts">
	import { truncate } from '$lib/utils';
	import { open } from '@tauri-apps/api/dialog';

	export let path: string;
	export let pathCompletelyInvalid = false;
	export let name: string = "";

	/**
	 * Gets directory from tauri dialog and pipes into the path prop
	 */
	async function getDir() {
		// Get path from tauri
		const gotPath = await open({ directory: true });

		// They clicked out of the menu without giving a path
		if (gotPath == null) {
			pathCompletelyInvalid = path == undefined || path == '';
		}

		// Get first path if multiple are selected
		else if (Array.isArray(gotPath)) {
			pathCompletelyInvalid = false;
			path = gotPath[0];
		}

		// Get path if one is selected
		else {
			pathCompletelyInvalid = false;
			path = gotPath;
		}
	}

	/**
	 * Gets the last filename (or directory name) on a provided path or returns nothing
	 * @param path Path to get the filename of
	 */
	function getPathFilename(path: string): string | undefined {
		// Don't do anything with no path
		if (path == undefined || path == '') {
			return undefined;
		}

		// Get the last path on the directory and return if possible
		let filename = path.split('\\').pop();
		if (filename == undefined) {
			return undefined;
		}
		filename = filename.split('/').pop();
		return filename;
	}

	// Set the name to the filename if it ever changes
	$: name = getPathFilename(path) ?? '';
</script>

<button class="bright" on:click={async () => await getDir()} class:invalid={pathCompletelyInvalid}>
	{#if path == undefined}
		Select Folder..
	{:else}
		{truncate(path, 50)}
	{/if}
</button>
